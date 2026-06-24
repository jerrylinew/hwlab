<script setup>
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from "vue";
import { EditorView, basicSetup } from "codemirror";
import { keymap } from "@codemirror/view";
import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";

// The editor reads and writes main.py through the same server that serves this
// page, so plain relative URLs are correct in the normal (built) flow.
const CODE_URL = "/api/code";

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

async function loadCode() {
  try {
    const response = await fetch(CODE_URL);
    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }
    const { code } = await response.json();
    view.value = new EditorView({
      doc: code,
      extensions: [basicSetup, python(), keymap.of([indentWithTab])],
      parent: host.value,
    });
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : String(error);
  }
}

async function save() {
  if (!view.value || saving.value) {
    return;
  }
  saving.value = true;
  saveResult.value = null;
  const code = view.value.state.doc.toString();

  try {
    const response = await fetch(CODE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const result = await response.json();
    if (result.ok) {
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
    // mid-flight. A network error here almost always means "saved, restarting."
    saveResult.value = { kind: "ok", text: "Saved! The lab is restarting with your changes..." };
  } finally {
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

onMounted(loadCode);
onBeforeUnmount(() => view.value?.destroy());
</script>

<template>
  <section class="panel editor-panel">
    <div class="editor-header">
      <div>
        <h2>Edit Your Gestures</h2>
        <p>This is <code>main.py</code>. Change the rules, then Save - the lab updates itself.</p>
      </div>
      <button type="button" :disabled="saving || !!loadError" @click="save">
        {{ saving ? "Saving..." : "Save & Run" }}
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

    <p v-if="runtimeError" class="editor-msg error">
      Your code ran into an error: {{ runtimeError }}
    </p>
  </section>
</template>

<style scoped>
.editor-panel {
  margin-top: 24px;
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

.editor-host {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 12px;
  max-height: 460px;
  overflow: auto;
}

.editor-host :deep(.cm-editor) {
  font-size: 14px;
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
