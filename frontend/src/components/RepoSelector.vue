<script setup>
import Multiselect from 'vue-multiselect';
import 'vue-multiselect/dist/vue-multiselect.min.css';
import { defineProps, defineModel } from 'vue';

const props = defineProps({ repositories: Array });
const selected = defineModel('selectedRepos');
</script>

<template>
  <div style="margin-bottom: 10px; max-width: 300px;">
    <label class="label">Выберите репозитории:</label>
    <multiselect
      v-model="selected"
      :options="repositories"
      :multiple="true"
      :close-on-select="false"
      :clear-on-select="false"
      :preserve-search="true"
      placeholder="Выберите один или несколько..."
      class="multiselect"
    />
  </div>
</template>

<style scoped>
.label {
  font-weight: bold;
  margin-bottom: 4px;
  display: block;
}
</style>