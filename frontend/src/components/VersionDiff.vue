<script setup>
import { ref, onMounted } from 'vue';
import { fetchVersionDiffApi, fetchPackageVersionsApi } from '../utils/requestApi';

const props = defineProps({
  packageName: String,
  repos: Array,
});

const versionsData = ref(null); // Список доступных версий (или объект с NEVRA)
const diffData = ref(null);     // Данные по разнице версий после выбора версии
const loading = ref(false);
const error = ref(null);
const selectedVersion = ref(null);

onMounted(() => {
  loadVersions();
});

const loadVersions = async () => {
  if (!props.packageName || !props.repos?.length) {
    return;
  }

  loading.value = true;
  error.value = null;
  diffData.value = null;
  selectedVersion.value = null;

  try {
    versionsData.value = await fetchPackageVersionsApi(props.packageName, props.repos);
  } 
  catch (e) {
    error.value = 'Ошибка при получении версий';
    console.error(e);
  } 
  finally {
    loading.value = false;
  }
};

const loadDiff = async (version) => {
  if (!version) return;

  loading.value = true;
  error.value = null;
  diffData.value = null;
  selectedVersion.value = version;

  try {
    diffData.value = await fetchVersionDiffApi(props.packageName, props.repos, version);
  } 
  catch (e) {
    error.value = 'Ошибка при получении различий версий';
    console.error(e);
  } 
  finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="version-diff">
    <p>Пакет: <strong>{{ packageName }}</strong></p>

    <div v-if="!repos || repos.length === 0">
      <p>Нет выбранных репозиториев для сравнения</p>
    </div>

    <div v-if="loading">🔄 Загрузка данных...</div>
    <div v-if="error" style="color:red;">{{ error }}</div>

    <div v-if="versionsData && !loading">
      <p>Доступные версии:</p>
      <ul>
        <li v-for="version in versionsData" :key="version">
          <button
            :class="{ selected: selectedVersion === version }"
            @click="loadDiff(version)"
          >
            {{ version }}
          </button>
        </li>
      </ul>
    </div>

    <div v-if="diffData && !loading">
      <p>Сравнение версий для: <strong>{{ selectedVersion }}</strong></p>
      <pre>{{ JSON.stringify(diffData, null, 2) }}</pre>
    </div>

    <p v-else-if="selectedVersion && !diffData && !loading">❗ Нет данных для выбранной версии</p>
  </div>
</template>

<style scoped>
.version-diff {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #bbb;
  border-radius: 8px;
  background-color: #f9f9f9;
  font-family: sans-serif;
}

ul {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

button {
  padding: 4px 8px;
  margin: 2px;
  border-radius: 4px;
  border: 1px solid #aaa;
  background: #eee;
  cursor: pointer;
}

button.selected {
  background-color: #4caf50;
  color: white;
  border-color: #3a8d3a;
}

button:hover {
  background-color: #d4edda;
}
</style>
