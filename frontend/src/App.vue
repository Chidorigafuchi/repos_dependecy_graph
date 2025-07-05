<script setup>
import RepoSelector from './components/RepoSelector.vue';
import GraphRenderer from './components/GraphRenderer.vue';
import NodeModal from './components/NodeElements.vue';

import { ref } from 'vue';
import axios from 'axios';

const packageName = ref('');
const selectedRepos = ref([]);
const repositories = ["os", "updates", "debuginfo", "kernel-rt", "kernel-testing"];
const message = ref('');

const graphData = ref({});

const selectedNodeId = ref(null);
const selectedNodeType = ref(null);
const selectedNodeItems = ref([]);
const filterText = ref('');

const isLoading = ref(false);

const fetchGraph = async () => {
  if (!packageName.value || selectedRepos.value.length === 0) return;

  isLoading.value = true;

  try {
    const response = await axios.post('http://localhost:8000/api/package/', {
      name: packageName.value,
      repos: selectedRepos.value,
    });
    graphData.value = response.data;
  } 
  catch (error) {
    console.error('Ошибка при получении графа:', error);
  } 
  finally {
    isLoading.value = false;
  }
};

const trackPackage = async () => {
  if (!packageName.value || selectedRepos.value.length === 0) return;
  
  isLoading.value = true;

  try {
    const response = await axios.post('http://localhost:8000/api/track_package/', {
      name: packageName.value,
      repos: selectedRepos.value,
    }, 
    {
      withCredentials: true
    })

    if (response.data.track_created === true) {
      message.value = `Пакет "${packageName.value}" добавлен в отслеживание.`
    } 
    else if (response.data.track_created === false) {
      message.value = `Пакет "${packageName.value}" уже отслеживается.`
    }
    else {
      message.value = 'Неожиданный ответ от сервера.'
    }
  } 
  catch (error) {
    console.error('Ошибка при отслеживании пакета:', error)
    message.value = 'Ошибка при добавлении пакета в отслеживание.'
  }
  finally {
    isLoading.value = false;
  }
};

const onNodeClicked = ({ nodeId, nodeType, items }) => {
  selectedNodeId.value = nodeId;
  selectedNodeType.value = nodeType;
  selectedNodeItems.value = items || []
};

const closeModal = () => {
  selectedNodeId.value = null;
  selectedNodeType.value = null;
  selectedNodeItems.value = [];
  filterText.value = '';
};

const onGoToPackage = (newPackageName) => {
  packageName.value = newPackageName;
  fetchGraph();
};
</script>

<template>
  <div class="app">
    <repo-selector v-model:selectedRepos="selectedRepos" :repositories="repositories" />

    <input
      v-model="packageName"
      placeholder="Введите имя пакета"
      @keyup.enter="fetchGraph"
    />
    <button :disabled="isLoading || !packageName || selectedRepos.length === 0" @click="fetchGraph">Показать граф</button>
    <div>
      <button :disabled="isLoading || !packageName || selectedRepos.length === 0" @click="trackPackage">Добавить в отслеживаемые</button>
      <p>{{ message }}</p>
    </div>
    
    <graph-renderer
      :graphData="graphData"
      :packageName="packageName"
      @node-clicked="onNodeClicked"
      @goToPackage="onGoToPackage"
    />

    <node-modal
      v-if="selectedNodeId && (selectedNodeType === 'set' || selectedNodeType === 'library')"
      :node-id="selectedNodeId"
      :node-type="selectedNodeType"
      :node-items="selectedNodeItems"
      v-model:filterText="filterText"
      @close="closeModal"
      @goToPackage="onGoToPackage"
    />
  </div>
</template>

<style scoped>
.app {
  padding: 20px;
  font-family: Arial, sans-serif;
}

input {
  padding: 6px 10px;
  font-size: 16px;
  width: 300px;
  margin-right: 10px;
}

button {
  padding: 6px 12px;
  font-size: 16px;
  cursor: pointer;
}
</style>