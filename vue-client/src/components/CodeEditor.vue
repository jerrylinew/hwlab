<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from "vue";
import { EditorView, basicSetup } from "codemirror";
import { keymap } from "@codemirror/view";
import { Compartment, EditorState } from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";

// The editor reads and writes files through the same server that serves this
// page, so plain relative URLs are correct in the normal (built) flow. main.py
// is the only editable file and is saved through /api/code; the others are
// fetched read-only from /api/files for students to preview.
const CODE_URL = "/api/code";
const FILES_URL = "/api/files";

// A runtime error from the student's gesture functions (captured by the server
// while the camera runs), passed down so we can show it under the editor.
const props = defineProps({
  runtimeError: {
    type: String,
    default: null,
  },
});

const host = ref(null);
const view = shallowRef(null);
const loadError = ref(null);
const saving = ref(false);
// { kind: "ok" | "syntax", text, line? } describing the last save attempt.
const saveResult = ref(null);

// The active file's contents as last loaded or saved, so we can tell whether the
// editor has unsaved edits (used to autosave before switching files).
const baselineCode = ref("");

function isDirty() {
  return !!view.value && view.value.state.doc.toString() !== baselineCode.value;
}

// The list of files the server lets us open, and which one is showing. main.py
// is editable; the rest are read-only previews of the lab plumbing.
const files = ref([]);
const activeFile = ref("main.py");
const activeEditable = computed(
  () => files.value.find((f) => f.name === activeFile.value)?.editable ?? false,
);

// Toggling read-only at runtime means reconfiguring the live editor, so the
// editable extensions live in a compartment we can swap per file.
const editable = new Compartment();

function editableExtensions(canEdit) {
  return [EditorView.editable.of(canEdit), EditorState.readOnly.of(!canEdit)];
}

async function fetchFile(name) {
  const response = await fetch(`${FILES_URL}/${name}`);
  if (!response.ok) {
    throw new Error(`Server returned ${response.status}`);
  }
  const result = await response.json();
  if (result.ok === false) {
    throw new Error(result.error || `Couldn't load ${name}`);
  }
  return result.code;
}

async function loadCode() {
  try {
    const listResponse = await fetch(FILES_URL);
    if (listResponse.ok) {
      files.value = (await listResponse.json()).files ?? [];
    }
    const code = await fetchFile(activeFile.value);
    baselineCode.value = code;
    view.value = new EditorView({
      doc: code,
      extensions: [
        basicSetup,
        python(),
        keymap.of([indentWithTab]),
        editable.of(editableExtensions(activeEditable.value)),
      ],
      parent: host.value,
    });
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : String(error);
  }
}

async function selectFile(name) {
  if (!view.value || name === activeFile.value) {
    return;
  }
  // Autosave the current file's edits before leaving it, so switching tabs
  // never silently drops changes. If the save is rejected for a syntax error,
  // stay put so the student can fix it instead of losing the broken edits.
  if (activeEditable.value && isDirty()) {
    await save();
    if (saveResult.value?.kind === "syntax") {
      return;
    }
  }
  // Clear any save note from the previous file before switching.
  saveResult.value = null;
  try {
    const code = await fetchFile(name);
    baselineCode.value = code;
    activeFile.value = name;
    view.value.dispatch({
      changes: { from: 0, to: view.value.state.doc.length, insert: code },
      effects: editable.reconfigure(editableExtensions(activeEditable.value)),
    });
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : String(error);
  }
}

async function save() {
  if (!view.value || saving.value || !activeEditable.value) {
    return;
  }
  saving.value = true;
  saveResult.value = null;
  const code = view.value.state.doc.toString();

  // Never let the button hang on "Saving...": if the response doesn't come back
  // promptly (the server writes the file then restarts), give up waiting and
  // treat it as saved + restarting.
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), 12000);

  try {
    const response = await fetch(CODE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: activeFile.value, code }),
      signal: controller.signal,
    });
    const result = await response.json();
    if (result.ok) {
      baselineCode.value = code; // this version is now on disk — no longer dirty
      saveResult.value = { kind: "ok", text: "Saved! The lab is restarting with your changes..." };
    } else if (result.line) {
      saveResult.value = {
        kind: "syntax",
        line: result.line,
        text: `Not saved - there's a typo on line ${result.line}: ${result.error}`,
      };
    } else {
      saveResult.value = { kind: "syntax", text: `Not saved - ${result.error}` };
    }
  } catch (error) {
    // The server writes the file then auto-reloads, which can drop this request
    // mid-flight (or trip the timeout above). That almost always means the save
    // landed and the lab is restarting.
    baselineCode.value = code;
    saveResult.value = { kind: "ok", text: "Saved! The lab is restarting with your changes..." };
  } finally {
    window.clearTimeout(timer);
    saving.value = false;
  }
}

// Once the lab has restarted, clear the "restarting" note.
watch(
  () => props.runtimeError,
  () => {
    if (saveResult.value?.kind === "ok") {
      saveResult.value = null;
    }
  },
);

// Cmd+S (mac) / Ctrl+S (win) saves and runs the lab instead of triggering the
// browser's "save this web page" dialog. A window listener catches it whether
// or not the editor is focused (CodeMirror doesn't bind Mod-s itself). save()
// already no-ops for read-only files or an in-flight save.
function handleSaveShortcut(event) {
  if ((event.metaKey || event.ctrlKey) && event.key?.toLowerCase() === "s") {
    event.preventDefault();
    save();
  }
}

onMounted(() => {
  loadCode();
  window.addEventListener("keydown", handleSaveShortcut);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleSaveShortcut);
  view.value?.destroy();
});
</script>

<template>
  <section class="panel editor-panel">
    <div class="editor-header">
      <div>
        <h2>Edit Your Gestures</h2>
        <p v-if="activeEditable">
          Editing <code>{{ activeFile }}</code>. Change the code, then Save - the lab updates itself.
        </p>
        <p v-else>
          Viewing <code>{{ activeFile }}</code> (read-only). Only <code>main.py</code> can be edited.
        </p>
      </div>
      <button
        v-if="activeEditable"
        type="button"
        :disabled="saving || !!loadError"
        @click="save"
      >
        {{ saving ? "Saving..." : "Save & Run" }}
      </button>
    </div>

    <div v-if="files.length" class="file-tabs">
      <button
        v-for="file in files"
        :key="file.name"
        type="button"
        :class="['file-tab', { active: file.name === activeFile }]"
        @click="selectFile(file.name)"
      >
        {{ file.name }}<span v-if="!file.editable" class="lock" title="Read-only">🔒</span>
      </button>
    </div>

    <p v-if="loadError" class="editor-msg error">
      Couldn't load your code: {{ loadError }}
    </p>

    <div ref="host" class="editor-host"></div>

    <p
      v-if="saveResult"
      :class="['editor-msg', saveResult.kind === 'ok' ? 'ok' : 'error']"
    >
      {{ saveResult.text }}
    </p>

    <p v-if="runtimeError && activeEditable" class="editor-msg error">
      Your code ran into an error: {{ runtimeError }}
    </p>
  </section>
</template>

<style scoped>
.editor-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.editor-header {
  align-items: flex-start;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.editor-header h2,
.editor-header p {
  margin: 0 0 6px;
}

.editor-header p {
  color: #666;
}

.editor-header button {
  background: #2563eb;
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  padding: 10px 16px;
  white-space: nowrap;
}

.editor-header button:disabled {
  background: #9db8ea;
  cursor: default;
}

.file-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 12px;
}

.file-tab {
  background: #f1f3f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #444;
  cursor: pointer;
  font-family: monospace;
  font-size: 0.8rem;
  padding: 5px 10px;
}

.file-tab:hover {
  background: #e7eaee;
}

.file-tab.active {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}

.file-tab .lock {
  margin-left: 5px;
  font-size: 0.7rem;
}

.editor-host {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 12px;
  flex: 1;
  min-height: 360px;
  overflow: auto;
}

.editor-host :deep(.cm-editor) {
  font-size: 14px;
  height: 100%;
}

.editor-host :deep(.cm-focused) {
  outline: none;
}

.editor-msg {
  border-radius: 8px;
  margin-top: 12px;
  padding: 10px 12px;
}

.editor-msg.ok {
  background: #d4edda;
  color: #155724;
}

.editor-msg.error {
  background: #f8d7da;
  color: #721c24;
}
</style>
