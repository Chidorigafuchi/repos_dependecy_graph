<template>
  <div class="app">
    <div style="margin-bottom: 10px; max-width: 300px;">
      <label class="label">Выберите репозитории:</label>
      <multiselect
        v-model="selectedRepos"
        :options="repositories"
        :multiple="true"
        :close-on-select="false"
        :clear-on-select="false"
        :preserve-search="true"
        placeholder="Выберите один или несколько..."
        class="multiselect"
      />
    </div>

    <input
      v-model="packageName"
      placeholder="Введите имя пакета"
      @keyup.enter="fetchGraph"
    />
    <button @click="fetchGraph">Показать граф</button>

    <div
      ref="networkContainer"
      style="height: 700px; border: 1px solid #ccc; margin-top: 20px;"
    ></div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { Network } from 'vis-network';
import Multiselect from 'vue-multiselect';
import 'vue-multiselect/dist/vue-multiselect.min.css';

const packageName = ref('');
const selectedRepos = ref([]);
const repositories = ["os", "updates", "debuginfo", "kernel-rt", "kernel-testing"];
const network = ref(null);
const networkContainer = ref(null);

const fetchGraph = async () => {
  if (!packageName.value || selectedRepos.value.length === 0) return;

  try {
    const response = await axios.post('http://localhost:8000/api/package/', {
      name: packageName.value,
      repos: selectedRepos.value,
    });

    const data = response.data;

    const isEmpty =
      Object.keys(data.package_package || {}).length === 0 &&
      Object.keys(data.set_package || {}).length === 0 &&
      Object.keys(data.library_package || {}).length === 0;

    if (isEmpty) {
      alert('Такого пакета нет или у него нет зависимостей.');
      return;
    }

    const { nodes, edges } = buildGraph(data, packageName.value);

    if (network.value) {
      network.value.destroy();
      network.value = null;
    }

    const options = {
      layout: {
        hierarchical: {
          enabled: true,
          direction: 'UD',
          sortMethod: 'directed',
          nodeSpacing: 150,
          levelSeparation: 120,
        },
      },
      physics: false,
      nodes: {
        shape: 'dot',
        size: 16,
        font: { size: 16 },
        borderWidth: 1,
      },
      edges: {
        arrows: 'to',
        smooth: {
          type: 'cubicBezier',
          forceDirection: 'vertical',
          roundness: 0.4,
        },
      },
    };

    network.value = new Network(networkContainer.value, { nodes, edges }, options);
  } catch (error) {
    console.error('Ошибка при получении графа:', error);
  }
};

const buildGraph = (data, target) => {
  const nodes = new Map();
  const edges = [];
  const visited = new Set();
  const addedLibs = new Set();

  const addNode = (id, level, shape = 'dot', color = null, label = null) => {
    if (!nodes.has(id)) {
      nodes.set(id, {
        id,
        label: label || id,
        level,
        shape,
        ...(color && { color }),
      });
    } else {
      const node = nodes.get(id);
      if (level < node.level) node.level = level;
    }
  };

  const addLibrariesForPackage = (pkg, pkgLevel) => {
    const libs = data.library_package?.[pkg] || [];
    if (libs.length === 0 || addedLibs.has(pkg)) return;
    addedLibs.add(pkg);

    const libNodeId = `libs_for_${pkg}`;
    addNode(libNodeId, pkgLevel - 1, 'triangle', '#ccffff', 'libraries');
    nodes.get(libNodeId).label = 'unused';
    edges.push({ from: libNodeId, to: pkg });
  };

  const walkDown = (pkg, level) => {
    addNode(pkg, level);
    addLibrariesForPackage(pkg, level);

    if (visited.has(pkg)) return;
    visited.add(pkg);

    const children = data.package_package?.[pkg] || [];
    for (const child of children) {
      addNode(child, level + 1);
      edges.push({ from: pkg, to: child });
      walkDown(child, level + 1);
    }

    for (const [packageKey, setList] of Object.entries(data.set_package || {})) {
      if (packageKey === pkg) {
        for (const setName of setList) {
          addNode(setName, level + 1, 'box', '#ccffcc');
          edges.push({ from: pkg, to: setName });
        }
      }
    }
  };

  const walkUp = (pkg, level) => {
    addNode(pkg, level);
    addLibrariesForPackage(pkg, level);

    const parents = Object.entries(data.package_package || {}).filter(
      ([parent, children]) => children.includes(pkg)
    );

    for (const [parent] of parents) {
      addNode(parent, level - 1);
      edges.push({ from: parent, to: pkg });
      walkUp(parent, level - 1);
    }

    for (const [setName, packages] of Object.entries(data.set_package || {})) {
      if (packages.includes(pkg)) {
        addNode(setName, level - 1, 'box', '#ffff66');
        edges.push({ from: setName, to: pkg });
      }
    }
  };

  addNode(target, 0, 'dot', '#ff9900');
  walkUp(target, 0);
  walkDown(target, 0);

  return {
    nodes: Array.from(nodes.values()),
    edges,
  };
};
</script>

<style>
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

.label {
  font-weight: bold;
  margin-bottom: 4px;
  display: block;
}
</style>
