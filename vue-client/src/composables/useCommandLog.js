import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const MAX_COMMANDS = 50;

export function useCommandLog(wsUrl) {
  const commands = ref([]);
  const connected = ref(false);
  let socket = null;
  let reconnectTimer = null;
  let closing = false;

  function closeSocket() {
    closing = true;
    window.clearTimeout(reconnectTimer);
    socket?.close();
    socket = null;
    connected.value = false;
  }

  function openSocket(url) {
    closing = false;
    window.clearTimeout(reconnectTimer);
    socket?.close();
    const ws = new WebSocket(url);
    socket = ws;

    ws.addEventListener("open", () => {
      if (socket === ws) {
        connected.value = true;
      }
    });

    ws.addEventListener("close", () => {
      if (socket !== ws) {
        return; // superseded by a newer socket; ignore
      }
      connected.value = false;
      // The server briefly restarts whenever main.py is saved. Reconnect so the
      // command log returns on its own instead of going dead until a refresh.
      if (!closing) {
        reconnectTimer = window.setTimeout(() => openSocket(url), 1500);
      }
    });

    ws.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        commands.value.unshift(data);
        if (commands.value.length > MAX_COMMANDS) {
          commands.value.pop();
        }
      } catch (error) {
        console.warn("Ignoring malformed command event", error);
      }
    });
  }

  function sendToPython(command, sendNow = false) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return false;
    }

    socket.send(JSON.stringify({ command, send_now: sendNow }));
    return true;
  }

  function addVueOnlyCommand(command) {
    commands.value.unshift({
      command,
      sent_to_xiao: false,
      send_to_xiao_enabled: false,
      timestamp: new Date().toISOString(),
      vue_only: true,
    });
    if (commands.value.length > MAX_COMMANDS) {
      commands.value.pop();
    }
  }

  onMounted(() => {
    openSocket(wsUrl.value);
  });

  watch(wsUrl, (nextUrl) => {
    openSocket(nextUrl);
  });

  onBeforeUnmount(closeSocket);

  return {
    commands,
    connected,
    addVueOnlyCommand,
    sendToPython,
  };
}
