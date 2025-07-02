<script setup>
import { onMounted, ref, watch } from 'vue';
import { Network } from 'vis-network';

const props = defineProps({
  graphData: Object,
  packageName: String,
});

const emit = defineEmits(['node-clicked']);
const network = ref(null);
const container = ref(null);

watch(() => props.graphData, (newData) => {
  if (!newData || Object.keys(newData).length === 0) return;
  drawGraph(newData, props.packageName);
}, { deep: true });

const drawGraph = (data, target) => {
  const { nodes, edges } = buildGraph(data, target);

  if (network.value) {
    network.value.destroy();
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
      font: { size: 16, multi: true },
      widthConstraint: { maximum: 110 },
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

  network.value = new Network(container.value, { nodes, edges }, options);
  network.value.on('click', (params) => handleNodeClick(params, data));
};

const handleNodeClick = (params, data) => {
  const nodeId = params.nodes[0];
  if (!nodeId) return;

  if (nodeId in data.sets) {
    emit('node-clicked', { nodeId, nodeType: 'set', items: data.sets[nodeId] });
  } else if (nodeId.startsWith('libs_for_')) {
    const pkg = nodeId.replace('libs_for_', '');
    const libs = data.library_package?.[pkg] || [];
    if (libs.length > 0) {
      emit('node-clicked', { nodeId, nodeType: 'library', items: libs });
    }
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
    nodes.get(libNodeId).label = 'unresolved';
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

<template>
  <div ref="container" style="height: 700px; border: 1px solid #ccc; margin-top: 20px;"></div>
</template>