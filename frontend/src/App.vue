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

        if (Object.keys(data).length === 0) {
          this.clearGraph();
          alert("Пакет не найден или не имеет зависимостей.");
          return;
        }

        const nodes = [];
        const edges = [];
        const nodesSet = new Set();

        const target = this.packageName;
        const reverseDeps = []; // кто зависит от искомого пакета
        const directDeps = data[target] || [];

        // Добавляем центр
        nodes.push({ id: target, label: target, color: "#ff9900", level: 1 });
        nodesSet.add(target);

        // Прямые зависимости (target → child)
        directDeps.forEach((child) => {
          if (!nodesSet.has(child)) {
            nodes.push({ id: child, label: child, level: 2 });
            nodesSet.add(child);
          }
          edges.push({ from: target, to: child });
        });

        // Обратные зависимости (parent → target)
        for (const [pkg, deps] of Object.entries(data)) {
          if (deps.includes(target)) {
            if (!nodesSet.has(pkg)) {
              nodes.push({ id: pkg, label: pkg, level: 0 });
              nodesSet.add(pkg);
            }
            edges.push({ from: pkg, to: target });
          }
        }

        const container = document.getElementById("network");
        const visData = { nodes, edges };
        const options = {
          layout: {
            hierarchical: {
              enabled: true,
              direction: "UD",
              sortMethod: "directed",
              nodeSpacing: 150,
              levelSeparation: 100,
            },
          },
          nodes: {
            shape: "dot",
            size: 20,
            font: { size: 16 },
          },
          edges: {
            arrows: "to",
            smooth: true,
          },
          physics: false,
        };

        this.clearGraph();
        this.network = new Network(container, visData, options);
      } catch (error) {
        console.error("Ошибка при загрузке графа:", error);
        this.clearGraph();
      }
    },

    clearGraph() {
      if (this.network) {
        this.network.destroy();
        this.network = null;
      }
      const container = document.getElementById("network");
      if (container) {
        container.innerHTML = ""; // очистка DOM-контейнера
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
