<script setup>
import { computed, toRef } from "vue";

import CommandLog from "./CommandLog.vue";
import VideoFeed from "./VideoFeed.vue";
import { createPythonServerUrls } from "../lib/pythonServer";

const props = defineProps({
  pyServer: {
    type: String,
    required: true,
  },
});

const pyServer = toRef(props, "pyServer");
const urls = computed(() => createPythonServerUrls(pyServer.value));
</script>

<template>
  <section class="lab-dashboard">
    <p>
      This page shows what your Python OpenCV script sees, and any commands it
      sends to your Seeed Studio XIAO.
    </p>
    <div class="layout">
      <VideoFeed :src="urls.videoFeedUrl" />
      <CommandLog :ws-url="urls.wsUrl" />
    </div>
  </section>
</template>

<style scoped>
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
