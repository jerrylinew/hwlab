import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import { useCommandLog } from "./composables/useCommandLog";
import { createPythonServerUrls } from "./lib/pythonServer";

export function useHwLab(pyServer = import.meta.env.VITE_PY_SERVER ?? "http://localhost:8000") {
  const urls = createPythonServerUrls(pyServer);
  const wsUrl = computed(() => urls.wsUrl);
  const { commands, connected, addVueOnlyCommand, sendToPython } = useCommandLog(wsUrl);
  const latestCommand = computed(() => commands.value[0] ?? null);
  const diagnostics = ref(null);
  let diagnosticsTimer = null;

  async function refreshDiagnostics() {
    try {
      const response = await fetch(urls.debugStatusUrl);
      diagnostics.value = await response.json();
    } catch (error) {
      diagnostics.value = {
        python_ok: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  onMounted(() => {
    refreshDiagnostics();
    diagnosticsTimer = window.setInterval(refreshDiagnostics, 1000);
  });

  onBeforeUnmount(() => {
    window.clearInterval(diagnosticsTimer);
  });

  return {
    commands,
    connected,
    diagnostics,
    addVueOnlyCommand,
    latestCommand,
    refreshDiagnostics,
    sendToPython,
    videoFeedUrl: urls.videoFeedUrl,
  };
}
