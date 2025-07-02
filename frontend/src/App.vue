<script setup>
import RepoSelector from './components/RepoSelector.vue';
import GraphRenderer from './components/GraphRenderer.vue';
import NodeModal from './components/NodeModal.vue';

import { ref } from 'vue';
import axios from 'axios';

const packageName = ref('');
const selectedRepos = ref([]);
const repositories = ["os", "updates", "debuginfo", "kernel-rt", "kernel-testing"];

const graphData = ref({});

const selectedNodeId = ref(null);
const selectedNodeType = ref(null);
const selectedNodeItems = ref([]);
const filterText = ref('');

const fetchGraph = async () => {
  if (!packageName.value || selectedRepos.value.length === 0) return;

  try {
    const response = await axios.post('http://localhost:8000/api/package/', {
      name: packageName.value,
      repos: selectedRepos.value,
    });
    graphData.value = response.data;
  } catch (error) {
    console.error('Ошибка при получении графа:', error);
  }
};

const onNodeClicked = ({ nodeId, nodeType, items }) => {
  selectedNodeId.value = nodeId;
  selectedNodeType.value = nodeType;
  selectedNodeItems.value = items;
};

const closeModal = () => {
  selectedNodeId.value = null;
  selectedNodeType.value = null;
  selectedNodeItems.value = [];
  filterText.value = '';
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
    <button @click="fetchGraph">Показать граф</button>

    <graph-renderer
      :graphData="graphData"
      :packageName="packageName"
      @node-clicked="onNodeClicked"
    />

    <node-modal
      v-if="selectedNodeId"
      :node-id="selectedNodeId"
      :node-type="selectedNodeType"
      :node-items="selectedNodeItems"
      v-model:filterText="filterText"
      @close="closeModal"
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