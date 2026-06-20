import { computed } from "vue";

import { useCommandLog } from "./composables/useCommandLog";
import { createPythonServerUrls } from "./lib/pythonServer";

export function useHwLab(pyServer = import.meta.env.VITE_PY_SERVER ?? "http://localhost:8000") {
  const urls = createPythonServerUrls(pyServer);
  const wsUrl = computed(() => urls.wsUrl);
  const { commands, connected, sendToPython } = useCommandLog(wsUrl);
  const latestCommand = computed(() => commands.value[0] ?? null);

  return {
    commands,
    connected,
    latestCommand,
    sendToPython,
    videoFeedUrl: urls.videoFeedUrl,
  };
}
