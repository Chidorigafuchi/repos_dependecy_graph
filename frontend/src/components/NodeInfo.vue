<script setup>
import { ref, watch } from 'vue';
import { fetchPackageInfoApi } from '../utils/request_api';
import TrackPackage from './TrackPackage.vue';

const props = defineProps({
  packageId: String,
  selectedRepos: Array,
});
const emit = defineEmits(['close', 'goToPackage']);

const packageInfo = ref(null);

watch(
  () => props.packageId,
  async (newId) => {
    if (!newId) return;

    packageInfo.value = null;

    const data = await fetchPackageInfoApi(newId);    
    packageInfo.value = data;
  },
  { immediate: true }
);

const goToPackage = () => {
  emit('goToPackage', props.packageId);
  emit('close');
};
</script>

<template>
  <div class="popup">
    <div class="header">
      <h3>Пакет: {{ packageId }}</h3>
      <button @click="$emit('close')" class="close-btn">×</button>
    </div>
    
    <div v-if="packageInfo">
      <TrackPackage
        :package-name="packageId"
        :selected-repos="selectedRepos"
        :disabled="false"
      />

      <p><strong>Version:</strong> {{ packageInfo.version }}</p>
      <p><strong>Release:</strong> {{ packageInfo.release }}</p>

      <p><strong>Url:</strong> 
        <a :href="packageInfo.url" target="_blank" rel="noopener noreferrer">
            {{ packageInfo.url }}
        </a>
      </p>

      <p><strong>NEVRA:</strong> {{ packageInfo.nevra }}</p>

      <p><strong>Conflicts:</strong></p>
      <ul>
        <li v-for="(item, index) in packageInfo.conflicts" :key="index">{{ item }}</li>
      </ul>

      <p><strong>Obsoletes:</strong></p>
      <ul>
        <li v-for="(item, index) in packageInfo.obsoletes" :key="index">{{ item }}</li>
      </ul>
      
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
