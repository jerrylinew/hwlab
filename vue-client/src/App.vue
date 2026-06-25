<script setup>
import { computed, ref } from "vue";

import { useHwLab } from "./useHwLab";
import { formatCommandTime } from "./lib/pythonServer";
import CodeEditor from "./components/CodeEditor.vue";

const {
  commands,
  connected,
  diagnostics,
  latestCommand,
  refreshDiagnostics,
  sendToPython,
  videoFeedUrl,
} = useHwLab();

const manualCommand = ref("thumbs_up");

// Debug Status panel is hidden for now — flip to true to bring it back.
const showDebug = ref(false);

// A banner describing what the camera/detection is doing, so a slow first-run
// model download or a setup failure is visible instead of a frozen feed.
const labStatus = computed(() => {
  const d = diagnostics.value;
  if (!d) {
    return null;
  }
  if (d.camera_error) {
    return { kind: "error", text: d.camera_error };
  }
  if (d.camera_status === "starting") {
    return {
      kind: "info",
      text: "Starting the camera and detection... the first run can download a model, which may take up to a minute.",
    };
  }
  return null;
});

function sendManualToPython() {
  const command = manualCommand.value.trim();
  if (command) {
    sendToPython(command, true);
  }
}

function clearHistory() {
  commands.value = [];
}
</script>

<template>
  <main>
    <h1>OpenCV Gesture &amp; Face Lab</h1>
    <p class="subtitle">
      Webcam and command log on the left; edit your gesture code on the right.
    </p>

    <p v-if="labStatus" :class="['lab-status', labStatus.kind]">
      {{ labStatus.text }}
    </p>

    <div class="workspace">
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
          <button type="submit">Send</button>
          <button type="button" @click="clearHistory">Clear history</button>
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

      <div class="col-right">
        <CodeEditor :runtime-error="diagnostics?.user_code_error ?? null" />
      </div>
    </div>

    <section v-if="showDebug" class="panel diagnostics-panel">
      <div class="debug-header">
        <div>
          <h2>Debug Status</h2>
          <p>Live pipeline health for Vue, Python, and the XIAO.</p>
        </div>
        <button type="button" @click="refreshDiagnostics">Refresh</button>
      </div>

      <div class="diagnostics-grid">
        <article :class="['debug-card', diagnostics?.python_ok ? 'good' : 'bad']">
          <span class="debug-dot"></span>
          <h3>Python API</h3>
          <strong>{{ diagnostics?.python_ok ? "Connected" : "Not connected" }}</strong>
        </article>

        <article :class="['debug-card', connected ? 'good' : 'warn']">
          <span class="debug-dot"></span>
          <h3>Vue WebSocket</h3>
          <strong>{{ connected ? "Connected" : "Disconnected" }}</strong>
          <small>{{ diagnostics?.vue_clients ?? 0 }} Vue client(s)</small>
        </article>

        <article :class="['debug-card', diagnostics?.xiao_connected ? 'good' : 'bad']">
          <span class="debug-dot"></span>
          <h3>XIAO</h3>
          <strong>{{ diagnostics?.xiao_connected ? "Connected" : "Not connected" }}</strong>
          <small>{{ diagnostics?.xiao_transport?.last_transport ?? "no transport yet" }}</small>
        </article>

        <article class="debug-card">
          <span class="debug-dot neutral"></span>
          <h3>Transport</h3>
          <strong>{{ diagnostics?.xiao_transport?.configured_transport ?? "auto" }}</strong>
          <small>{{ diagnostics?.xiao_transport?.serial_port ?? diagnostics?.xiao_transport?.http_url ?? "unknown" }}</small>
        </article>

        <article class="debug-card">
          <span class="debug-dot neutral"></span>
          <h3>Last Command</h3>
          <strong>{{ diagnostics?.last_sent_command ?? "none" }}</strong>
          <small>{{ diagnostics?.last_sent_to_xiao ? "XIAO received it" : "not confirmed by XIAO" }}</small>
        </article>

        <article class="debug-card color-card">
          <span class="debug-dot neutral"></span>
          <h3>RGB LED</h3>
          <strong>{{ diagnostics?.xiao_status?.rgb_color ?? "unknown" }}</strong>
          <small>{{ diagnostics?.xiao_status?.rgb_red ?? "?" }}, {{ diagnostics?.xiao_status?.rgb_green ?? "?" }}, {{ diagnostics?.xiao_status?.rgb_blue ?? "?" }}</small>
        </article>
      </div>

      <p v-if="diagnostics?.xiao_transport?.last_error" class="debug-error">
        {{ diagnostics.xiao_transport.last_error }}
      </p>
    </section>
  </main>
</template>

<style>
/* Global reset so the app sits edge-to-edge with no default body margin. */
html,
body,
#app {
  margin: 0;
  height: 100%;
}
</style>

<style scoped>
/* Full-screen app: fill the viewport, no centered max-width, no page scroll.
   The header is fixed at the top; the workspace below fills the rest and each
   column manages its own scrolling. */
main {
  font-family: sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 12px 16px;
  box-sizing: border-box;
  overflow: hidden;
}

main > h1 {
  margin: 0 0 2px;
  font-size: 1.3rem;
}

.subtitle {
  margin: 0 0 12px;
  color: #555;
}

.lab-status {
  border-radius: 8px;
  margin: 0 0 12px;
  padding: 10px 12px;
  flex-shrink: 0;
}

.lab-status.info {
  background: #fff3cd;
  color: #856404;
}

.lab-status.error {
  background: #f8d7da;
  color: #721c24;
}

/* Three horizontal columns filling the viewport height: webcam (¼) and commands
   (¼) on the left, the code editor (½) on the right. min-height:0 lets each
   column shrink so its children can scroll instead of overflowing. */
.workspace {
  display: grid;
  grid-template-columns: 3fr 2fr 5fr;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

.col-right {
  display: flex;
  min-width: 0;
  min-height: 0;
}

.col-right > * {
  flex: 1;
  min-height: 0;
}

.panel {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 18px;
  background: #fff;
  box-sizing: border-box;
}

/* Each side column fills the full workspace height and manages its own
   overflow; min-width:0 lets the quarter-width columns shrink cleanly. */
.video-panel,
.log-panel {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* Hug the feed's natural height instead of stretching to full column height —
   stretching is what forced the letterbox black bars above/below the image. */
.video-panel {
  align-self: start;
}

.video-panel h2,
.log-panel h2 {
  flex-shrink: 0;
}

/* Fill the panel's remaining height and letterbox (contain) so the feed is
   never cropped and never overflows its half. */
/* width:100% + height:auto sizes the image to the feed's own aspect ratio, so
   there are no black letterbox bars. */
.video-panel img {
  display: block;
  width: 100%;
  height: auto;
  border: 2px solid #333;
  border-radius: 8px;
  background: #000;
}

/* The command list takes the leftover space under the form and scrolls. */
.command-list {
  flex: 1;
  min-height: 0;
}

@media (max-width: 900px) {
  /* On narrow screens, stack the three columns and let the page scroll normally
     instead of trapping content inside a fixed-height viewport. */
  main {
    height: auto;
    overflow: visible;
  }

  .workspace {
    grid-template-columns: 1fr;
  }
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
  overflow-y: auto;
  padding: 0;
  margin: 0;
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
  background: linear-gradient(135deg, #101828, #18243a);
  color: #eef4ff;
}

.debug-header {
  align-items: flex-start;
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.debug-header h2,
.debug-header p {
  margin: 0 0 6px;
}

.diagnostics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.debug-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 14px;
}

.debug-card h3,
.debug-card strong,
.debug-card small {
  display: block;
  margin: 4px 0;
}

.debug-card small {
  color: #b8c7e6;
  overflow-wrap: anywhere;
}

.debug-dot {
  background: #f59e0b;
  border-radius: 50%;
  display: inline-block;
  height: 10px;
  width: 10px;
}

.debug-card.good .debug-dot {
  background: #22c55e;
}

.debug-card.bad .debug-dot {
  background: #ef4444;
}

.debug-dot.neutral {
  background: #60a5fa;
}

.debug-error {
  background: rgba(239, 68, 68, 0.18);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 10px;
  margin-top: 14px;
  padding: 10px;
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
