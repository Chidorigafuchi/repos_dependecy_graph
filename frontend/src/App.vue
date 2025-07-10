<script setup>
import RepoSelector from './components/RepoSelector.vue';
import GraphRenderer from './components/GraphRenderer.vue';
import NodeModal from './components/NodeElements.vue';
import TrackedList from './components/TrackedList.vue';
import VersionDiff from './components/VersionDiff.vue';
import { fetchTrackedPackagesApi, getAvailabelRepos } from './utils/requestApi';
import { transformRepoList, fetchGraph, showGraphFromTracked } from './utils/graphFetch';

import { ref, computed, onMounted } from 'vue';

const packageName = ref('');
const selectedRepos = ref([]);

const repoSource = ref({});
const isLoading = ref(false);
const message = ref('');
const graphData = ref({});

const selectedNodeId = ref(null);
const selectedNodeType = ref(null);
const selectedNodeItems = ref([]);
const filterText = ref('');

const trackedPackages = ref([]);
const showTrackedList = ref(false);
const showVersionDiff = ref(false);

onMounted(async () => {
  const reposList = await getAvailabelRepos(); 
  repoSource.value = transformRepoList(reposList);
  trackedPackages.value = await fetchTrackedPackagesApi();
});

const isTrackedPackageDisplayed = computed(() =>
  packageName.value in trackedPackages.value
);

const repositories = computed(() =>
  Object.entries(repoSource.value).map(([base_url, names]) => ({
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

const fetchGraphHandler = async () => {
  closeModal();

  const data = await fetchGraph({
    packageName: packageName.value,
    selectedRepos: getRepoList.value,
    setMessage: msg => message.value = msg,
    setIsLoading: val => isLoading.value = val,
  });

  if (data) {
    graphData.value = data;
  }
};

const showGraphFromTrackedHandler = async ({ pkg, repos }) => {
  showTrackedList.value = false;

  await showGraphFromTracked({
    pkg,
    repos,
    repoSource: repoSource.value,
    setPackageName: val => packageName.value = val,
    setSelectedRepos: val => selectedRepos.value = val,
    fetchGraph: fetchGraphHandler,
  });
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
  fetchGraphHandler();
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
      @show-graph="showGraphFromTrackedHandler"
      />

    <repo-selector v-model:selectedRepos="selectedRepos" :repositories="repositories" />

    <input
      v-model="packageName"
      placeholder="Введите имя пакета"
      @keyup.enter="fetchGraphHandler"
    />
    <button :disabled="isLoading || !packageName || selectedRepos.length === 0" @click="fetchGraphHandler">
      Показать граф
    </button>

    <button
      v-if="Object.keys(graphData || {}).length > 0 && isTrackedPackageDisplayed"
      class="diff-button"
      @click="showVersionDiff = !showVersionDiff"
    >
      {{ showVersionDiff ? 'Скрыть сравнение версий' : 'Разница версий' }}
    </button>

    <version-diff
      v-if="showVersionDiff"
      :package-name="packageName"
      :repos="getRepoList"
    />
    
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

.diff-button {
  margin-top: 10px;
  padding: 6px 12px;
  font-size: 16px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.diff-button:hover {
  background-color: #1976d2;
}
</style>