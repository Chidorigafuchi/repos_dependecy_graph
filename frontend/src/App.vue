<template>
  <div id="app">
    <h1>Ввод названия пакета</h1>
    <input
      v-model="packageName"
      type="text"
      placeholder="Введите название пакета"
      class="input-field"
    />
    <button @click="submitPackage" class="submit-button">Отправить</button>
    <div v-if="packageData">
      <h2>Данные пакета:</h2>
      <p><strong>Название:</strong> {{ packageData.name }}</p>
      <p><strong>Архитектура:</strong> {{ packageData.arch }}</p>
      <p><strong>Версия:</strong> {{ packageData.version }}</p>
      <p><strong>Релиз:</strong> {{ packageData.release }}</p>
      <p><strong>URL:</strong> <a :href="packageData.url" target="_blank">{{ packageData.url }}</a></p>
    </div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      packageName: '',
      packageData: null,
      errorMessage: '',
    };
  },
  methods: {
    async submitPackage() {
      this.packageData = null;
      this.errorMessage = '';
      try {
        const response = await axios.post('http://localhost:8000/api/package/', {
          name: this.packageName,
        });
        this.packageData = response.data;
      } catch (error) {
        this.errorMessage = 'Ошибка: ' + (error.response?.data?.error || 'Неизвестная ошибка');
      }
    },
  },
};
</script>

<style scoped>
#app {
  font-family: Arial, sans-serif;
  max-width: 400px;
  margin: 50px auto;
  text-align: center;
  color: #2c3e50;
}

.input-field {
  width: 100% !important;
  min-height: 40px !important; /* Увеличиваем высоту */
  padding: 12px !important; /* Больший внутренний отступ */
  font-size: 18px !important; /* Больший шрифт */
  border: 1px solid #ccc !important;
  border-radius: 4px !important;
  margin-top: 10px !important;
  box-sizing: border-box !important; /* Учитываем padding в ширине */
}

.input-field:focus {
  outline: none !important;
  border-color: #007bff !important;
}

.submit-button {
  margin-top: 10px;
  padding: 10px 20px;
  font-size: 16px;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.submit-button:hover {
  background-color: #0056b3;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>