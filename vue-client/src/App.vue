<script setup>
import { useHwLab } from "./useHwLab";

const { connected, latestCommand, sendToPython, videoFeedUrl } = useHwLab();
</script>

<template>
  <main>
    <h1>My HW Lab Website</h1>

    <!-- Change this page to build your own local website. -->
    <section class="card">
      <h2>Message From Python</h2>
      <p class="big-message">
        {{ latestCommand?.command ?? "No message yet" }}
      </p>
      <p class="status">
        Python connection: {{ connected ? "connected" : "not connected" }}
      </p>
    </section>

    <section class="card">
      <h2>Send A Message To Python</h2>
      <button @click="sendToPython('hello_from_vue')">
        Send hello_from_vue
      </button>
      <p>
        Python can read this with <code>receive()</code>.
      </p>
    </section>

    <details class="camera-card">
      <summary>Show Camera Feed</summary>
      <img :src="videoFeedUrl" alt="Live webcam feed from Python" />
    </details>
  </main>
</template>

<style scoped>
main {
  font-family: sans-serif;
  max-width: 760px;
  margin: 0 auto;
  padding: 24px;
}

.card,
.camera-card {
  border: 2px solid #222;
  border-radius: 12px;
  margin: 18px 0;
  padding: 18px;
}

.big-message {
  font-size: 2rem;
  font-weight: 700;
}

.status {
  color: #555;
}

button {
  cursor: pointer;
  font-size: 1rem;
  padding: 10px 14px;
}

img {
  display: block;
  width: 100%;
  margin-top: 16px;
  border-radius: 8px;
  background: #000;
}
</style>
