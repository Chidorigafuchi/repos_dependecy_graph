<script setup>
import Multiselect from 'vue-multiselect';
import 'vue-multiselect/dist/vue-multiselect.min.css';

const props = defineProps({ repositories: Array });
const selected = defineModel('selectedRepos');
</script>

<template>
  <div style="margin-bottom: 10px; max-width: 400px;">
    <label class="label">Выберите репозитории:</label>
    <multiselect
      v-model="selected"
      :options="repositories"
      :group-label="'base_url'"
      :group-values="'repos'"
      :label="'name'"
      :track-by="'full'"
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