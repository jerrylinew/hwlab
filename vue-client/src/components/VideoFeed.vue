<script setup>
defineProps({
  src: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <div class="video-feed">
    <h2>Webcam Feed</h2>
    <img :src="src" alt="Live webcam feed from the Python OpenCV client" />
  </div>
</template>

<style scoped>
.video-feed img {
  width: 100%;
  max-width: 640px;
  border: 2px solid #333;
  border-radius: 8px;
  background: #000;
}
</style>
