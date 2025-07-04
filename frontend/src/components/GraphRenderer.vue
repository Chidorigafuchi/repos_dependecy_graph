<script setup>
import { ref, watch } from 'vue';
import { Network } from 'vis-network';
import PackagePopup from './NodeInfo.vue';
import { buildGraph } from '@/utils/graphBuilder';

const props = defineProps({
  graphData: Object,
  packageName: String,
});

const emit = defineEmits(['node-clicked']);
const network = ref(null);
const container = ref(null);

const currentNodeId = ref(null);
const popupVisible = ref(false);
const popupTop = ref(0);
const popupLeft = ref(0);

const lastClickedNodeId = ref(null);

watch(
  () => props.graphData, (newData) => {
    if (!newData || Object.keys(newData).length === 0) return;
    drawGraph(newData, props.packageName);
  },
  { deep: true }
);

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
      size: 16,
      widthConstraint: { maximum: 110 },
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

  if (lastClickedNodeId.value !== nodeId) {
    lastClickedNodeId.value = nodeId;
    popupVisible.value = false;
    return;
  }

  if (nodeId in data.sets) {
    emit('node-clicked', { nodeId, nodeType: 'set', items: data.sets[nodeId] });
    popupVisible.value = false;
  } 
  else if (nodeId.startsWith('libs_for_')) {
    const pkg = nodeId.replace('libs_for_', '');
    const libs = data.library_package?.[pkg] || [];
    if (libs.length > 0) {
      emit('node-clicked', { nodeId, nodeType: 'library', items: libs });
      popupVisible.value = false;
    }
  } 
  else {
    emit('node-clicked', { nodeId, nodeType: 'package' });

    const pos = network.value.getPositions([nodeId])[nodeId];
    const domPos = network.value.canvasToDOM(pos);

    currentNodeId.value = nodeId;
    popupTop.value = domPos.y + 10;
    popupLeft.value = domPos.x + 10;
    popupVisible.value = true;
  }
};

const closePopup = () => {
  popupVisible.value = false;
};
</script>

<template>
  <div style="position: relative;">
    <div ref="container" style="height: 700px; border: 1px solid #ccc; margin-top: 20px;"></div>

    <PackagePopup
      v-if="popupVisible"
      :package-id="currentNodeId"
      :packageName="props.packageName"
      :style="{
        position: 'absolute',
        top: popupTop + 'px',
        left: popupLeft + 'px',
        zIndex: 200,
      }"
      @close="closePopup"
      @goToPackage="$emit('goToPackage', $event)"
    />
  </div>
</template>