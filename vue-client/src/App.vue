<script setup>
import LabDashboard from "./components/LabDashboard.vue";

const pyServer = import.meta.env.VITE_PY_SERVER ?? "http://localhost:8000";
</script>

<template>
  <main>
    <h1>HW Lab</h1>

    <LabDashboard :py-server="pyServer" />

    <!-- Add your own components below -->
  </main>
</template>

<style scoped>
main {
  font-family: sans-serif;
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}
</style>
