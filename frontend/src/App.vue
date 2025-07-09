<script setup>
import RepoSelector from './components/RepoSelector.vue';
import GraphRenderer from './components/GraphRenderer.vue';
import NodeModal from './components/NodeElements.vue';
import TrackedList from './components/TrackedList.vue';
import { fetchTrackedPackagesApi } from './utils/request_api';

import { fetchGraphApi } from './utils/request_api';
import { ref, computed, onMounted, watch } from 'vue';

const packageName = ref('');
const selectedRepos = ref([]);

const repoSource = {
  "https://repo1.red-soft.ru/redos/8.0/x86_64/": ["os", "updates", "debuginfo", "kernel-rt", "kernel-testing"],
  "https://repo1.red-soft.ru/redos/7.3/x86_64/": ["test", "test2"]
};
const isLoading = ref(false);
const message = ref('');
const graphData = ref({});

const selectedNodeId = ref(null);
const selectedNodeType = ref(null);
const selectedNodeItems = ref([]);
const filterText = ref('');

const trackedPackages = ref([]);
const showTrackedList = ref(false);

onMounted(async () => {
  trackedPackages.value = await fetchTrackedPackagesApi();
});

const repositories = computed(() =>
  Object.entries(repoSource).map(([base_url, names]) => ({
    base_url,
    repos: names.map(name => ({
      name,
      full: `${base_url}${name}/`,
      base_url,
    }))
  }))
);

const getRepoList = computed(() => {
  return selectedRepos.value.map(repo => {
    if (typeof repo === 'string') return repo;
    return `${repo.base_url}${repo.name}/`;
  });
});


const fetchGraph = async () => {
  if (!packageName.value || getRepoList.value.length === 0) return;

  closeModal();

  message.value = '';
  isLoading.value = true;

  const data = await fetchGraphApi(packageName.value, getRepoList.value);
  graphData.value = data;
  isLoading.value = false;
};

const showGraphFromTracked = async ({ pkg, repos }) => {
  packageName.value = pkg;
  selectedRepos.value = repos.map(r => {
    if (typeof r === 'string') {
      for (const [baseUrl, repoNames] of Object.entries(repoSource)) {
        if (r.startsWith(baseUrl)) {
          const repoName = r.slice(baseUrl.length).replace(/\/$/, '');
          if (repoNames.includes(repoName)) {
            return {
              name: repoName,
              full: r,
              base_url: baseUrl,
            };
          }
        }
      }
      return null;
    }
    return r;
  }).filter(Boolean);
  showTrackedList.value = false;
  await fetchGraph();
};

const onNodeClicked = ({ nodeId, nodeType, items }) => {
  selectedNodeId.value = nodeId;
  selectedNodeType.value = nodeType;
  selectedNodeItems.value = items || [];
};

const onWatchlistClick = () => {
  showTrackedList.value = true;
};

const closeModal = () => {
  selectedNodeId.value = null;
  selectedNodeType.value = null;
  selectedNodeItems.value = [];
  filterText.value = '';
};

const closeTrackedList = () => {
  showTrackedList.value = false;
};

const onGoToPackage = (newPackageName) => {
  packageName.value = newPackageName;
  fetchGraph();
};
</script>

<template>
  <div class="app">
    <button class="watchlist-button" @click="onWatchlistClick">
      Список отслеживаемых
    </button>

    <tracked-list 
      v-if="showTrackedList" 
      :tracked-packages="trackedPackages"
      :onClose="closeTrackedList"
      @show-graph="showGraphFromTracked"
      />

    <repo-selector v-model:selectedRepos="selectedRepos" :repositories="repositories" />

    <input
      v-model="packageName"
      placeholder="Введите имя пакета"
      @keyup.enter="fetchGraph"
    />
    <button :disabled="isLoading || !packageName || selectedRepos.length === 0" @click="fetchGraph">
      Показать граф
    </button>
    
    <graph-renderer
      :graph-data="graphData"
      :package-name="packageName"
      :selected-repos="getRepoList"
      :node-id="selectedNodeId"
      :is-loading="isLoading"
      @node-clicked="onNodeClicked"
      @goToPackage="onGoToPackage"
    />

    <node-modal
      v-if="selectedNodeId && (selectedNodeType === 'set' || selectedNodeType === 'library')"
      :node-id="selectedNodeId"
      :node-type="selectedNodeType"
      :node-items="selectedNodeItems"
      :selected-repos="getRepoList"
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

.watchlist-button {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 8px 14px;
  font-size: 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.watchlist-button:hover {
  background-color: #45a049;
}
</style>