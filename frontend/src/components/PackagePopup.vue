<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  packageId: String,
});
const emit = defineEmits(['close']);

const packageInfo = ref(null);
const loading = ref(false);
const error = ref(null);

watch(
  () => props.packageId,
  async (newId) => {
    if (!newId) return;

    loading.value = true;
    error.value = null;
    packageInfo.value = null;

    try {
      const response = await axios.get('http://localhost:8000/api/package_info/', {
      params: { name: newId }
    });
    if (!newId) error.value = 'Ошибка при загрузке информации о пакете';
    packageInfo.value = response.data;
    } catch (err) {
      error.value = 'Ошибка при загрузке информации о пакете';
      console.error(err);
    } finally {
      loading.value = false;
    }
  },
  { immediate: true }
);
</script>

<template>
  <div class="popup">
    <div class="header">
      <h3>Пакет: {{ packageId }}</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>

    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="packageInfo">
      <p><strong>Версия:</strong> {{ packageInfo.version }}</p>
      <p><strong>Релиз:</strong> {{ packageInfo.release }}</p>
      <p><strong>Юрл:</strong> 
        <a :href="packageInfo.url" target="_blank" rel="noopener noreferrer">
            {{ packageInfo.url }}
        </a>
      </p>
      <p><strong>Невра:</strong> {{ packageInfo.nevra }}</p>
    </div>
  </div>
</template>

<style scoped>
.popup {
  background: white;
  padding: 12px 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  min-width: 250px;
  max-width: 400px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.close-btn:hover {
  color: red;
}
</style>
