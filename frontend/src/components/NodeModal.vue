<script setup>
import { computed, ref, nextTick } from 'vue';
import PackagePopup from './PackagePopup.vue';

const props = defineProps({
  nodeId: String,
  nodeItems: Array,
  nodeType: String,
});
const emit = defineEmits(['close']);

const filterText = ref('');
const selectedPackage = ref(null);
const modalRef = ref(null);

const popupStyle = ref({
  position: 'absolute',
  top: '0px',
  left: '0px',
  zIndex: 300,
});

const filteredItems = computed(() => {
  return props.nodeItems.filter(item =>
    item.toLowerCase().includes(filterText.value.toLowerCase())
  );
});

const onItemClick = async (item) => {
  selectedPackage.value = item;

  await nextTick();

  if (modalRef.value) {
    const rect = modalRef.value.getBoundingClientRect();
    popupStyle.value.top = rect.top + 'px';
    popupStyle.value.left = rect.right + 10 + 'px';
  }
};

const closePackagePopup = () => {
  selectedPackage.value = null;
};

function handleGoToPackage(packageId) {
  emit('goToPackage', packageId);
  emit('close');
}
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal" ref="modalRef">
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
        <li
          v-for="item in filteredItems"
          :key="item"
          @click="onItemClick(item)"
          :style="nodeType === 'set' ? { cursor: 'pointer', color: 'blue', textDecoration: 'underline' } : {}"
        >
          {{ item }}
        </li>
      </ul>

      <PackagePopup
        v-if="selectedPackage && nodeType === 'set'"
        :packageId="selectedPackage"
        @close="closePackagePopup"
        @goToPackage="handleGoToPackage"
        :style="popupStyle"
      />
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