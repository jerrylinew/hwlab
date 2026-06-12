<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const props = defineProps({
  wsUrl: {
    type: String,
    required: true,
  },
});

const commands = ref([]);
const connected = ref(false);
let socket = null;

function formatTime(isoTimestamp) {
  return new Date(isoTimestamp).toLocaleTimeString();
}

onMounted(() => {
  socket = new WebSocket(props.wsUrl);

  socket.addEventListener("open", () => {
    connected.value = true;
  });

  socket.addEventListener("close", () => {
    connected.value = false;
  });

  socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    commands.value.unshift(data);
    // Keep the log from growing forever.
    if (commands.value.length > 50) {
      commands.value.pop();
    }
  });
});

onBeforeUnmount(() => {
  socket?.close();
});
</script>

<template>
  <div class="command-log">
    <h2>
      Commands Sent
      <span :class="['status', connected ? 'connected' : 'disconnected']">
        {{ connected ? "connected" : "disconnected" }}
      </span>
    </h2>
    <ul>
      <li v-for="(entry, index) in commands" :key="index">
        <span class="time">{{ formatTime(entry.timestamp) }}</span>
        <span class="command">{{ entry.command }}</span>
        <span :class="['badge', entry.sent_to_xiao ? 'ok' : 'fail']">
          {{ entry.sent_to_xiao ? "sent to XIAO" : "not sent" }}
        </span>
      </li>
    </ul>
    <p v-if="commands.length === 0" class="empty">
      No commands yet - try making a gesture or showing your face!
    </p>
  </div>
</template>

<style scoped>
.command-log {
  font-family: sans-serif;
}

.status {
  font-size: 0.7em;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 8px;
}

.status.connected {
  background: #d4edda;
  color: #155724;
}

.status.disconnected {
  background: #f8d7da;
  color: #721c24;
}

ul {
  list-style: none;
  padding: 0;
  max-height: 480px;
  overflow-y: auto;
}

li {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 6px 8px;
  border-bottom: 1px solid #eee;
}

.time {
  color: #888;
  font-size: 0.85em;
  min-width: 80px;
}

.command {
  font-weight: bold;
  flex: 1;
}

.badge {
  font-size: 0.75em;
  padding: 2px 8px;
  border-radius: 12px;
}

.badge.ok {
  background: #d4edda;
  color: #155724;
}

.badge.fail {
  background: #fff3cd;
  color: #856404;
}

.empty {
  color: #888;
}
</style>
