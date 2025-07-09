import unittest
from unittest.mock import patch
from yum_parser.services.graph import (
    get_package_graph_with_cache,
    find_package_neighbours,
    add_dependence,
    PackageGraph
)
from yum_parser.services.parser import PackageDependencies
from pickle import dumps

class GraphTests(unittest.TestCase):
    def setUp(self):
        self.pkg_name = "mypkg"
        self.repos = ["repo1", "repo2"]
        self.session_key = "abc123"

    @patch("yum_parser.services.graph.redis_get")
    @patch("yum_parser.services.graph.redis_set")
    @patch("yum_parser.services.graph.get_package_graph")
    def test_get_package_graph_with_cache_miss(self, mock_graph, mock_set, mock_get):
        mock_get.return_value = None
        mock_graph.return_value = PackageGraph(package_package={"mypkg": ["libA"]})
        
        result = get_package_graph_with_cache(self.session_key, self.pkg_name, self.repos)

        self.assertIn("mypkg", result["package_package"])
        mock_set.assert_called_once()

    @patch("yum_parser.services.graph.redis_get")
    def test_get_package_graph_with_cache_hit(self, mock_get):
        graph = PackageGraph(package_package={"mypkg": ["libA"]})
        mock_get.return_value = dumps(graph)

        result = get_package_graph_with_cache(self.session_key, self.pkg_name, self.repos)
        self.assertIsInstance(result, PackageGraph)
        self.assertEqual(result.package_package["mypkg"], ["libA"])

    def test_add_dependence_direct(self):
        graph = PackageGraph()
        graph = add_dependence(["A"], ["B"], "depX", graph)
        self.assertEqual(graph.package_package["A"], ["B"])
        self.assertEqual(graph.sets, {})

    def test_add_dependence_sets(self):
        graph = PackageGraph()
        many_dependents = [f"pkg{i}" for i in range(10)]
        graph = add_dependence(["A"], many_dependents, "depX", graph)
        self.assertIn("SET_depX", graph.sets)
        self.assertEqual(graph.set_package["A"], ["SET_depX"])

    def test_add_dependence_reverse_set(self):
        graph = PackageGraph()
        many_providers = [f"lib{i}" for i in range(8)]
        graph = add_dependence(many_providers, ["Z"], "depX", graph)
        self.assertIn("SET_depX", graph.sets)
        self.assertEqual(graph.set_package["SET_depX"], ["Z"])

    def test_find_package_neighbours_up(self):
        repos_packages = {
            "mypkg": PackageDependencies(requires=[("libX",)]),
            "libpkg": PackageDependencies(provides=[("libX",)])
        }
        graph = PackageGraph()
        neighbours, updated_graph = find_package_neighbours(
            repos_packages, ["libX"], "mypkg", graph, up=True
        )
        self.assertIn("libpkg", neighbours)
        self.assertIn("libpkg", updated_graph.package_package)

    def test_find_package_neighbours_missing_dep(self):
        repos_packages = {
            "mypkg": PackageDependencies(requires=[("libX",)]),
        }
        graph = PackageGraph()
        neighbours, updated_graph = find_package_neighbours(
            repos_packages, ["libX"], "mypkg", graph, up=True
        )
        self.assertEqual(neighbours, [])
        self.assertIn("mypkg", updated_graph.library_package)
        self.assertIn("libX", updated_graph.library_package["mypkg"])

class GraphNegativeTests(unittest.TestCase):
    def setUp(self):
        self.pkg_name = "mypkg"
        self.repos = ["repo1", "repo2"]
        self.session_key = "abc123"

    @patch("yum_parser.services.graph.redis_get")
    @patch("yum_parser.services.graph.redis_set")
    def test_get_package_graph_with_cache_redis_get_exception(self, mock_set, mock_get):
        mock_get.side_effect = Exception("Redis failure")

        with self.assertRaises(Exception) as context:
            get_package_graph_with_cache(self.session_key, self.pkg_name, self.repos)

        self.assertIn("Redis failure", str(context.exception))

    def test_find_package_neighbours_empty_deps(self):
        repos_packages = {
            "mypkg": PackageDependencies(requires=[], provides=[])
        }
        graph = PackageGraph()
        neighbours, updated_graph = find_package_neighbours(
            repos_packages, [], "mypkg", graph, up=True
        )
        self.assertEqual(neighbours, [])
        self.assertEqual(updated_graph.package_package, {})

    def test_add_dependence_empty_lists(self):
        graph = PackageGraph()
        updated_graph = add_dependence([], [], "depX", graph)
        self.assertEqual(updated_graph.package_package, {})
        self.assertEqual(updated_graph.set_package, {})
        self.assertEqual(updated_graph.sets, {})

    def test_find_package_neighbours_invalid_repo_packages(self):
        repos_packages = {
            "mypkg": None 
        }
        graph = PackageGraph()
        with self.assertRaises(AttributeError):
            find_package_neighbours(
                repos_packages, ["libX"], "mypkg", graph, up=True
            )