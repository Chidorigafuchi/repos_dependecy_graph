<template>
  <div>
    <input v-model="packageName" placeholder="Введите название пакета" />
    <button @click="fetchGraph">Показать граф</button>
    <div id="network" style="height: 600px; border: 1px solid #ccc;"></div>
  </div>
</template>

<script>
import { Network } from "vis-network/standalone";
import axios from "axios";

export default {
  data() {
    return {
      packageName: "",
      network: null,
    };
  },
  methods: {
    async fetchGraph() {
      try {
        const response = await axios.post("http://localhost:8000/api/package/", {
          name: this.packageName,
        });

        const data = response.data;

        const nodes = [];
        const edges = [];

        const root = Object.keys(data)[0];
        const children = data[root];

        // Добавляем материнский пакет
        nodes.push({ id: root, label: root, color: "#ff9900" });

        // Добавляем дочерние пакеты
        children.forEach((child) => {
          nodes.push({ id: child, label: child });
          edges.push({ from: root, to: child });
        });

        const container = document.getElementById("network");
        const visData = { nodes, edges };
        const options = {
          nodes: {
            shape: "dot",
            size: 20,
            font: { size: 16 },
          },
          edges: {
            arrows: "to",
          },
          layout: {
            hierarchical: {
              direction: "UD",
              sortMethod: "hubsize",
            },
          },
        };

        if (this.network) {
          this.network.destroy();
        }

        this.network = new Network(container, visData, options);
      } catch (error) {
        console.error("Ошибка при загрузке графа:", error);
      }
    },
  },
};
</script>

<style scoped>
#network {
  margin-top: 20px;
}
</style>
