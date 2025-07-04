// src/utils/graphBuilder.js
export function buildGraph(data, target) {
  const nodes = new Map();
  const edges = [];
  const visitedUp = new Set();
  const visitedDown = new Set();
  const addedLibs = new Set();

  const addNode = (id, level, shape = 'dot', color = null, label = null) => {
    if (!nodes.has(id)) {
      let fontSettings = {
        color: '#000',
        size: 16,
        strokeColor: '#fff',
        multi: 'html',
      };
      if (shape !== 'box') fontSettings.background = 'white';
      nodes.set(id, {
        id,
        label: label || id,
        level,
        shape,
        ...(color && { color }),
        font: fontSettings,
      });
    } else {
      const node = nodes.get(id);
      if (level < node.level) node.level = level;
    }
  };

  const addLibrariesForPackage = (pkg, pkgLevel) => {
    const libs = data.library_package?.[pkg] || [];
    if (libs.length === 0 || addedLibs.has(pkg)) return;
    addedLibs.add(pkg);

    const libNodeId = `libs_for_${pkg}`;
    addNode(libNodeId, pkgLevel - 1, 'triangle', '#ccffff', 'libraries');
    nodes.get(libNodeId).label = 'unresolved';
    edges.push({ from: libNodeId, to: pkg });
  };

  const walkUp = (pkg, level) => {
    if (visitedUp.has(pkg)) return;
    visitedUp.add(pkg);

    const node = nodes.get(pkg);
    if (node && level < node.level) {
      node.level = level;
      addLibrariesForPackage(pkg, level);
      processParents(pkg, level, walkUp);
    } else {
      addNode(pkg, level);
      addLibrariesForPackage(pkg, level);
      processParents(pkg, level, walkUp);
    }
  };

  const walkDown = (pkg, level) => {
    if (visitedDown.has(pkg)) return;
    visitedDown.add(pkg);

    const node = nodes.get(pkg);
    if (node && level > node.level) {
      node.level = level;
      addLibrariesForPackage(pkg, level);
      processChildren(pkg, level, walkDown);
    } else {
      addNode(pkg, level);
      addLibrariesForPackage(pkg, level);
      processChildren(pkg, level, walkDown);
    }
  };

  const processParents = (pkg, level, walkFn) => {
    const parents = Object.entries(data.package_package || {}).filter(
      ([parent, children]) => children.includes(pkg)
    );
    for (const [parent] of parents) {
      edges.push({ from: parent, to: pkg });
      walkFn(parent, level - 1);
    }

    for (const [setName, packages] of Object.entries(data.set_package || {})) {
      if (packages.includes(pkg)) {
        addNode(setName, level - 1, 'box', '#ffff66');
        edges.push({ from: setName, to: pkg });
      }
    }
  };

  const processChildren = (pkg, level, walkFn) => {
    const children = data.package_package?.[pkg] || [];
    for (const child of children) {
      edges.push({ from: pkg, to: child });
      walkFn(child, level + 1);
    }

    for (const [packageKey, setList] of Object.entries(data.set_package || {})) {
      if (packageKey === pkg) {
        for (const setName of setList) {
          addNode(setName, level + 1, 'box', '#ccffcc');
          edges.push({ from: pkg, to: setName });
        }
      }
    }
  };

  addNode(target, 0, 'dot', '#ff9900');
  walkUp(target, 0);
  walkDown(target, 0);

  return {
    nodes: Array.from(nodes.values()),
    edges,
  };
}
