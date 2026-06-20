<script setup>
import { ref } from "vue";

import { useHwLab } from "./useHwLab";
import { formatCommandTime } from "./lib/pythonServer";

const {
  addVueOnlyCommand,
  commands,
  connected,
  diagnostics,
  latestCommand,
  refreshDiagnostics,
  sendToPython,
  videoFeedUrl,
} = useHwLab();

const manualCommand = ref("thumbs_up");

function sendManualToPython() {
  const command = manualCommand.value.trim();
  if (command) {
    sendToPython(command, true);
  }
}

function sendManualToVue() {
  const command = manualCommand.value.trim();
  if (command) {
    addVueOnlyCommand(command);
  }
}
</script>

<template>
  <main>
    <h1>OpenCV Gesture &amp; Face Lab</h1>
    <p>
      Camera feed on the left, command log on the right. Use the manual sender
      to test commands without making a gesture.
    </p>

    <div class="layout">
      <section class="panel video-panel">
        <h2>Webcam Feed</h2>
        <img :src="videoFeedUrl" alt="Live webcam feed from Python" />
      </section>

      <section class="panel log-panel">
        <h2>
          Commands Sent
          <span :class="['status-pill', connected ? 'connected' : 'disconnected']">
            Vue {{ connected ? "connected" : "disconnected" }}
          </span>
        </h2>

        <form class="manual-send" @submit.prevent="sendManualToPython">
          <input
            v-model="manualCommand"
            type="text"
            placeholder="thumbs_up"
            aria-label="Command to send"
          />
          <button type="submit">Send through Python</button>
          <button type="button" @click="sendManualToVue">Vue only</button>
        </form>

        <p class="latest">
          Latest from Python: <strong>{{ latestCommand?.command ?? "none" }}</strong>
        </p>

        <ul class="command-list">
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
                    : entry.vue_only
                      ? "Vue test"
                      : "Vue only"
              }}
            </span>
          </li>
        </ul>
        <p v-if="commands.length === 0" class="empty">
          No commands yet - try a thumbs-up or send one manually.
        </p>
      </section>
    </div>

    <section class="panel diagnostics-panel">
      <h2>Debug Status</h2>
      <button type="button" @click="refreshDiagnostics">Refresh</button>
      <div class="diagnostics-grid">
        <p>Python: <strong>{{ diagnostics?.python_ok ? "connected" : "not connected" }}</strong></p>
        <p>Vue WebSocket: <strong>{{ connected ? "connected" : "not connected" }}</strong></p>
        <p>Vue clients: <strong>{{ diagnostics?.vue_clients ?? 0 }}</strong></p>
        <p>XIAO sending: <strong>{{ diagnostics?.send_to_xiao_enabled ? "on" : "off" }}</strong></p>
        <p>XIAO status: <strong>{{ diagnostics?.xiao_connected ? "connected" : "not connected" }}</strong></p>
        <p>Last sent: <strong>{{ diagnostics?.last_sent_command ?? "none" }}</strong></p>
        <p>Last XIAO result: <strong>{{ diagnostics?.last_sent_to_xiao ? "success" : "no success yet" }}</strong></p>
        <p>XIAO color: <strong>{{ diagnostics?.xiao_status?.rgb_color ?? "unknown" }}</strong></p>
        <p>Attempts: <strong>{{ diagnostics?.send_attempts ?? 0 }}</strong></p>
      </div>
    </section>
  </main>
</template>

<style scoped>
main {
  font-family: sans-serif;
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

.layout {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.panel {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 18px;
  background: #fff;
}

.video-panel,
.log-panel {
  flex: 1;
  min-width: 320px;
}

.video-panel img {
  display: block;
  width: 100%;
  max-width: 640px;
  border: 2px solid #333;
  border-radius: 8px;
  background: #000;
}

.status-pill,
.badge {
  border-radius: 12px;
  font-size: 0.75rem;
  padding: 2px 8px;
}

.connected,
.badge.ok {
  background: #d4edda;
  color: #155724;
}

.disconnected,
.badge.fail {
  background: #fff3cd;
  color: #856404;
}

.badge.vue-only {
  background: #d9edf7;
  color: #0c5460;
}

.manual-send {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 12px 0;
}

.manual-send input {
  flex: 1;
  min-width: 150px;
  padding: 8px;
}

.manual-send button,
.diagnostics-panel button {
  cursor: pointer;
  padding: 8px 10px;
}

.command-list {
  list-style: none;
  max-height: 420px;
  overflow-y: auto;
  padding: 0;
}

.command-list li {
  align-items: center;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 10px;
  padding: 7px 0;
}

.time {
  color: #777;
  min-width: 78px;
}

.command {
  flex: 1;
  font-weight: 700;
}

.latest,
.empty {
  color: #666;
}

.diagnostics-panel {
  margin-top: 24px;
}

.diagnostics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 4px 18px;
}

@media (max-width: 740px) {
  main {
    padding: 14px;
  }

  .command-list li {
    align-items: flex-start;
    flex-direction: column;
  }

  .time {
    min-width: 0;
  }
}
</style>
