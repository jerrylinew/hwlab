<script setup>
import { toRef } from "vue";

import { useCommandLog } from "../composables/useCommandLog";
import { formatCommandTime } from "../lib/pythonServer";

const props = defineProps({
  wsUrl: {
    type: String,
    required: true,
  },
});

const { commands, connected } = useCommandLog(toRef(props, "wsUrl"));
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
        <span class="time">{{ formatCommandTime(entry.timestamp) }}</span>
        <span class="command">{{ entry.command }}</span>
        <span
          :class="[
            'badge',
            entry.sent_to_xiao
              ? 'ok'
              : entry.send_to_xiao_enabled
                ? 'fail'
                : 'vue-only',
          ]"
        >
          {{
            entry.sent_to_xiao
              ? "XIAO + Vue"
              : entry.send_to_xiao_enabled
                ? "XIAO failed"
                : "Vue only"
          }}
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

.badge.vue-only {
  background: #d9edf7;
  color: #0c5460;
}

.empty {
  color: #888;
}
</style>
