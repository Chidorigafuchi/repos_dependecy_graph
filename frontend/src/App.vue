<template>
  <div class="app">
    <input
      v-model="packageName"
      placeholder="Введите имя пакета"
      @keyup.enter="fetchGraph"
    />
    <button @click="fetchGraph">Показать граф</button>
    <div
      ref="networkContainer"
      style="height: 700px; border: 1px solid #ccc; margin-top: 20px;"
    ></div>
  </div>
</template>

<script>
import axios from "axios";
import { Network } from "vis-network";

export default {
  data() {
    return {
      packageName: "",
      network: null,
    };
  },
  methods: {
    async fetchGraph() {
      if (!this.packageName) return;

      try {
        const response = await axios.post("http://localhost:8000/api/package/", {
          name: this.packageName,
        });

        const data = response.data;
        const { nodes, edges } = this.buildGraph(data, this.packageName);

        if (this.network) {
          this.network.setData({ nodes: [], edges: [] });
        }

        const options = {
          layout: {
            hierarchical: {
              enabled: true,
              direction: "UD",
              sortMethod: "directed",
              nodeSpacing: 150,
              levelSeparation: 120,
            },
          },
          physics: false,
          nodes: {
            shape: "dot",
            size: 16,
            font: { size: 16 },
            borderWidth: 1,
          },
          edges: {
            arrows: "to",
            smooth: {
              type: "cubicBezier",
              forceDirection: "vertical",
              roundness: 0.4,
            },
          },
        };

        this.network = new Network(this.$refs.networkContainer, { nodes, edges }, options);
      } catch (error) {
        console.error("Ошибка при получении графа:", error);
      }
    },

    buildGraph(data, target) {
      const nodes = new Map();
      const edges = [];
      const visited = new Set();
      const addedLibs = new Set(); // Чтобы не дублировать библиотечные узлы

      const addNode = (id, level, shape = "dot", color = null, label = null) => {
        if (!nodes.has(id)) {
          nodes.set(id, {
            id,
            label: label || id,
            level,
            shape,
            ...(color && { color }),
          });
        } else {
          const node = nodes.get(id);
          if (level < node.level) node.level = level;
        }
      };

      const addLibrariesForPackage = (pkg, pkgLevel) => {
        const libs = data.package_to_library?.[pkg] || [];
        if (libs.length === 0 || addedLibs.has(pkg)) return;
        addedLibs.add(pkg);

        const libNodeId = `libs_for_${pkg}`;
        addNode(libNodeId, pkgLevel - 1, "triangle", "#ccffff", "libraries");
        nodes.get(libNodeId).label = "unkn libraries";
        edges.push({ from: libNodeId, to: pkg });
      };

      const walkDown = (pkg, level) => {
        addNode(pkg, level, "dot");
        addLibrariesForPackage(pkg, level);

        if (visited.has(pkg)) return;
        visited.add(pkg);

        const children = data.package_to_package?.[pkg] || [];
        for (const child of children) {
          addNode(child, level + 1, "dot");
          edges.push({ from: pkg, to: child });
          walkDown(child, level + 1);
        }

        for (const [setName, pkgs] of Object.entries(data.set_to_package || {})) {
          if (pkgs.includes(pkg)) {
            addNode(setName, level + 1, "box", "#ffff66");
            edges.push({ from: pkg, to: setName });
          }
        }
      };

      const walkUp = (pkg, level) => {
        addNode(pkg, level, "dot");
        addLibrariesForPackage(pkg, level);

        const parents = Object.entries(data.package_to_package || {}).filter(
          ([parent, children]) => children.includes(pkg)
        );

        for (const [parent] of parents) {
          addNode(parent, level - 1, "dot");
          edges.push({ from: parent, to: pkg });
          walkUp(parent, level - 1);
        }

        for (const [setName, pkgs] of Object.entries(data.set_to_package || {})) {
          if (pkgs.includes(pkg)) {
            addNode(setName, level - 1, "box", "#ffff66");
            edges.push({ from: setName, to: pkg });
          }
        }
      };

      addNode(target, 0, "dot", "#ff9900");
      walkUp(target, 0);
      walkDown(target, 0);

      return {
        nodes: Array.from(nodes.values()),
        edges,
      };
    },
  },
};
</script>

<style>
.app {
  padding: 20px;
  font-family: Arial, sans-serif;
}
input {
  padding: 6px 10px;
  font-size: 16px;
  width: 300px;
  margin-right: 10px;
}
button {
  padding: 6px 12px;
  font-size: 16px;
  cursor: pointer;
}
</style>
