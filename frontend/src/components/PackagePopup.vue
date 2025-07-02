<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  packageId: String,
});
const emit = defineEmits(['close', 'goToPackage']);

const packageInfo = ref(null);
const error = ref(null);

watch(
  () => props.packageId,
  async (newId) => {
    if (!newId) return;

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
    }
  },
  { immediate: true }
);

const goToPackage = () => {
  emit('goToPackage', props.packageId);
};
</script>

<template>
  <div class="popup">
    <div class="header">
      <h3>Пакет: {{ packageId }}</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>

    <div v-if="error">{{ error }}</div>
    <div v-else-if="packageInfo">
      <p><strong>Version:</strong> {{ packageInfo.version }}</p>
      <p><strong>Release:</strong> {{ packageInfo.release }}</p>
      <p><strong>Url:</strong> 
        <a :href="packageInfo.url" target="_blank" rel="noopener noreferrer">
            {{ packageInfo.url }}
        </a>
      </p>
      <p><strong>NEVRA:</strong> {{ packageInfo.nevra }}</p>
      <button class="go-btn" @click="goToPackage" v-if="packageInfo && props.packageId">
      Перейти
      </button>
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

.go-btn {
  display: block;
  width: 60%;
  max-width: 200px;
  margin: 10px auto 0 auto;
  padding: 12px 0;
  font-size: 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  text-align: center;
  transition: background-color 0.3s ease;
}

.go-btn:hover {
  background-color: #0056b3;
}
</style>
