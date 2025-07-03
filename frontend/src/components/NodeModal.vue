<script setup>
import { computed, defineProps, defineModel } from 'vue';

const props = defineProps({
  nodeId: String,
  nodeType: String,
  nodeItems: Array,
});
const filterText = defineModel('filterText');

const filteredItems = computed(() => {
  return props.nodeItems.filter(item =>
    item.toLowerCase().includes(filterText.value.toLowerCase())
  );
});
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3 v-if="nodeType === 'set'">
        Зависимости от <strong>{{ nodeId.replace('SET_', '') }}</strong>:
      </h3>
      <h3 v-else-if="nodeType === 'library'">
        Ненайденные зависимости для <strong>{{ nodeId.replace('libs_for_', '') }}</strong>:
      </h3>

      <input
        v-model="filterText"
        placeholder="Фильтр по названию..."
        style="margin-bottom: 10px; width: 100%; padding: 6px;"
      />

      <ul>
        <li v-for="item in filteredItems" :key="item">{{ item }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-height: 70vh;
  overflow-y: auto;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
  min-width: 300px;
}

.modal h3 {
  margin-top: 0;
}
</style>