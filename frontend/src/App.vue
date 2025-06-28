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

        const target = this.packageName;
        const nodes = [];
        const edges = [];
        const visited = new Set();
        const nodeLevels = new Map(); // id → level
        let maxDownLevel = 0;
        let minUpLevel = 0;

        const addNode = (id, level, overrideColor = null) => {
          let color = overrideColor;

          if (id.startsWith("SET")) {
            color = "#ffff66"; // жёлтый для множеств
          }

          if (!nodeLevels.has(id)) {
            nodeLevels.set(id, level);
            nodes.push({ id, label: id, level, ...(color && { color }) });
          } else {
            if (level < nodeLevels.get(id)) {
              nodeLevels.set(id, level);
              const node = nodes.find(n => n.id === id);
              if (node) {
                node.level = level;
                if (color) node.color = color;
              }
            }
          }
        };

        const visitDown = (pkg, level) => {
          maxDownLevel = Math.max(maxDownLevel, level);
          addNode(pkg, level);
          const children = data[pkg] || [];
          children.forEach((child) => {
            edges.push({ from: pkg, to: child });
            visitDown(child, level + 1);
          });
        };

        const visitUp = (pkg, level) => {
          minUpLevel = Math.min(minUpLevel, level);
          addNode(pkg, level);
          for (const [parent, deps] of Object.entries(data)) {
            if (deps.includes(pkg)) {
              edges.push({ from: parent, to: pkg });
              visitUp(parent, level - 1);
            }
          }
        };

        addNode(target, 0, "#ff9900");
        visitDown(target, 1);
        visitUp(target, -1);

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
