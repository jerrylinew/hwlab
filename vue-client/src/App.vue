<script setup>
import CommandLog from "./components/CommandLog.vue";
import VideoFeed from "./components/VideoFeed.vue";

const pyServer = import.meta.env.VITE_PY_SERVER ?? "http://localhost:8000";
const videoFeedUrl = `${pyServer}/video_feed`;
const wsUrl = `${pyServer.replace(/^http/, "ws")}/ws`;
</script>

<template>
  <main>
    <h1>OpenCV Gesture &amp; Face Lab</h1>
    <p>
      This page shows what your Python OpenCV script sees, and any commands it
      sends to your Seeed Studio XIAO.
    </p>
    <div class="layout">
      <VideoFeed :src="videoFeedUrl" />
      <CommandLog :ws-url="wsUrl" />
    </div>
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

.layout > * {
  flex: 1;
  min-width: 320px;
}
</style>
