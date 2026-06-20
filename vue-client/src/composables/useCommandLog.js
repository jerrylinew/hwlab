import { onBeforeUnmount, onMounted, ref, watch } from "vue";

const MAX_COMMANDS = 50;

export function useCommandLog(wsUrl) {
  const commands = ref([]);
  const connected = ref(false);
  let socket = null;

  function closeSocket() {
    socket?.close();
    socket = null;
    connected.value = false;
  }

  function openSocket(url) {
    closeSocket();
    socket = new WebSocket(url);

    socket.addEventListener("open", () => {
      connected.value = true;
    });

    socket.addEventListener("close", () => {
      connected.value = false;
    });

    socket.addEventListener("message", (event) => {
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
  };
}
