<script setup>
import { ref } from 'vue';
import { fetchVersionDiffApi } from '../utils/requestApi';

const props = defineProps({
  packageName: String,
  repoGroups: Array
});

const selectedGroup = ref(null);
const diffData = ref(null);
const loading = ref(false);

const loadVersionDiff = async (group) => {
  if (!props.packageName || !group?.length) return;
  selectedGroup.value = group;
  diffData.value = null;
  loading.value = true;
  try {
    diffData.value = await fetchVersionDiffApi(props.packageName, group);
  } catch (e) {
    console.error('Ошибка при получении различий:', e);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="version-diff">
    <p>Пакет: <strong>{{ packageName }}</strong></p>

    <div v-if="!repoGroups?.length">
      <p>Нет доступных групп репозиториев</p>
    </div>

    <ul v-else class="repo-group-list">
      <li v-for="group in repoGroups" :key="group.join(',')" class="repo-group-item">
        <button @click="loadVersionDiff(group)" class="repo-group-btn">
          <span v-for="repo in group" :key="repo" class="repo">{{ repo }}</span>
        </button>
      </li>
    </ul>

    <div class="result">
      <p v-if="loading">🔄 Загрузка различий версий...</p>
      <div v-else-if="diffData">
        <p>Сравнение версий:</p>
        <pre>{{ JSON.stringify(diffData, null, 2) }}</pre>
      </div>
      <p v-else-if="selectedGroup">❗ Нет данных</p>
    </div>
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

.repo-group-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}

.repo-group-item {
  margin-bottom: 8px;
}

.repo-group-btn {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #f0f0f0;
  cursor: pointer;
}

.repo-group-btn:hover {
  background-color: #e6f2ff;
}

.repo {
  background-color: #e0e0e0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.result {
  margin-top: 16px;
  font-family: monospace;
  font-size: 14px;
}
</style>
