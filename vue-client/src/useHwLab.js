import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { useCommandLog } from "./composables/useCommandLog";
import { createPythonServerUrls } from "./lib/pythonServer";

// By default the Vue app and the Python server share an origin (the Python
// server serves this built app). VITE_PY_SERVER only needs to be set when
// running the Vite dev server separately (see .env.development).
export function useHwLab(pyServer = import.meta.env.VITE_PY_SERVER ?? window.location.origin) {
  const urls = createPythonServerUrls(pyServer);
  const wsUrl = computed(() => urls.wsUrl);
  const { commands, connected, addVueOnlyCommand, sendToPython } = useCommandLog(wsUrl);
  const latestCommand = computed(() => commands.value[0] ?? null);
  const diagnostics = ref(null);
  let diagnosticsTimer = null;

  // The webcam feed is a long-lived MJPEG <img> stream. When the Python server
  // restarts (e.g. after Save & Run), that stream breaks and the browser won't
  // reopen it on its own — the feed stays black until a manual page refresh.
  // The WebSocket drops and reconnects on every restart, so we treat a
  // reconnect as "server is back" and bump a token that re-requests the feed
  // URL, forcing the <img> to reopen the stream automatically.
  const videoReloadToken = ref(0);
  let hasConnected = false;
  watch(connected, (isConnected) => {
    if (!isConnected) {
      return;
    }
    if (hasConnected) {
      videoReloadToken.value += 1; // a reconnect, i.e. the server came back
    }
    hasConnected = true;
  });

  const videoFeedUrl = computed(() =>
    videoReloadToken.value === 0
      ? urls.videoFeedUrl
      : `${urls.videoFeedUrl}?reload=${videoReloadToken.value}`,
  );

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
    videoFeedUrl,
  };
}
