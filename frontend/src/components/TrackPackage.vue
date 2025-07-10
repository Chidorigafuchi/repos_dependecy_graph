<script setup>
import { ref, computed } from 'vue';
import { trackPackageApi } from '../utils/requestApi';

const props = defineProps({
  packageName: String,
  selectedRepos: Array,
  disabled: Boolean,
});

const emit = defineEmits(['start', 'done']);

const message = ref('');
const isTracking = ref(false);

const trackPackage = async () => {
  if (!props.packageName || props.selectedRepos.length === 0) return;

  emit('start');
  isTracking.value = true;
  message.value = '';

  try {
    const data = await trackPackageApi(props.packageName, props.selectedRepos);

    if (data.track_created === true) {
      message.value = `Пакет "${props.packageName}" добавлен в отслеживание.`;
    } 
    else if (data.track_created === false) {
      message.value = `Пакет "${props.packageName}" уже отслеживается.`;
    } 
    else if (data.track_created === 'unknown') {
      message.value = `Ни один из репозиториев не найден`;
    } 
    else {
      message.value = 'Неожиданный ответ от сервера.';
    }
  } 
  catch (err) {
    console.error('Ошибка при добавлении в отслеживание:', err);
    message.value = 'Ошибка при добавлении пакета в отслеживание.';
  } 
  finally {
    isTracking.value = false;
    emit('done');
  }
};
</script>

<template>
  <div>
    <button
      :disabled="disabled || isTracking || !packageName || selectedRepos.length === 0"
      @click="trackPackage"
      :aria-busy="isTracking.toString()"
    >
      Добавить в отслеживаемые
    </button>
    <p>{{ message }}</p>
  </div>
</template>

