<script setup>
import { ref, computed, reactive, watch } from 'vue';
import { deleteRepoGroupApi } from '../utils/requestApi';

const props = defineProps({
  onClose: Function,
  trackedPackages: Object
});

const emit = defineEmits(['show-graph']);

const localTracked = reactive({ ...props.trackedPackages });

const expanded = ref(null);
const searchQuery = ref('');

watch(() => props.trackedPackages, (newVal) => {
  Object.keys(localTracked).forEach(k => delete localTracked[k]);
  Object.assign(localTracked, newVal);
});

const filteredPackages = computed(() => {
  if (!searchQuery.value.trim()) return localTracked;
  const result = {};
  for (const [pkg, repos] of Object.entries(localTracked)) {
    if (pkg.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      result[pkg] = repos;
    }
  }
  return result;
});

async function deleteGroup(pkg, repoGroup) {
  const result = await deleteRepoGroupApi(pkg, repoGroup);
  if (result) {
    const groups = localTracked[pkg];
    if (groups) {
      const index = groups.findIndex(g => JSON.stringify(g) === JSON.stringify(repoGroup));
      if (index !== -1) {
        groups.splice(index, 1);
        if (groups.length === 0) {
          delete localTracked[pkg];
          if (expanded.value === pkg) expanded.value = null;
        }
      }
    }
  } 
  else {
    console.warn('Не удалось удалить группу');
  }
}

function toggle(pkg) {
  expanded.value = expanded.value === pkg ? null : pkg;
}
</script>

<template>
  <div class="tracked-list">
    <button @click="onClose" class="close-btn">×</button>

    <div class="header">
      <h2>Список отслеживаемых пакетов</h2>
    </div>

    <input
      type="text"
      v-model="searchQuery"
      placeholder="Поиск по названию..."
      class="search-input"
    />

    <ul>
      <li v-for="(repos, pkg) in filteredPackages" :key="pkg" class="package-row">
        <div class="package-item">
          <span @click="toggle(pkg)" class="package-name">{{ pkg }}</span>
        </div>

        <ul v-if="expanded === pkg" class="repo-list">
          <li v-for="repoGroup in repos" :key="repoGroup.join(',')">
            <div class="repo-group">
              <div class="repo-group-content">
                <button 
                class="graph-btn"
                @click.prevent="() => emit('show-graph', { pkg, repos: [...repoGroup] })"
                >📈</button>

                <div class="repo-tags">
                  <span v-for="repo in repoGroup" :key="repo" class="repo">{{ repo }}</span>
                </div>
                
                <button 
                  class="delete-btn" 
                  @click.prevent="deleteGroup(pkg, repoGroup)"
                >🗑</button>
              </div>
            </div>
          </li>
        </ul>
      </li>
    </ul>

    <p v-if="Object.keys(filteredPackages).length === 0">Пакеты не найдены.</p>
  </div>
</template>


<style scoped>
.tracked-list {
  position: fixed;
  top: 60px;
  right: 20px;
  width: 360px;
  max-height: 80vh;
  overflow-y: auto;
  background-color: #f9f9f9;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  padding: 16px 16px 16px 16px;
  z-index: 1000;
  font-family: sans-serif;
}

.search-input {
  width: 100%;
  padding: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 10px;
  background: none;
  border: none;
  font-size: 22px;
  font-weight: bold;
  cursor: pointer;
  color: #888;
}

.close-btn:hover {
  color: red;
}

.header {
  text-align: center;
  margin-bottom: 12px;
}

.repo-list {
  margin-left: 12px;
  list-style: none;
  padding: 0;
}

.package-row {
  margin-bottom: 8px;
}

.package-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  cursor: pointer;
}

.package-name:hover {
  color: #007acc;
}

.repo-group {
  margin-bottom: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
}

.repo-group-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.repo-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.repo {
  display: inline-block;
  background-color: #e0e0e0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.graph-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 16px;
  cursor: pointer;
}

.delete-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 16px;
  cursor: pointer;
}
</style>
