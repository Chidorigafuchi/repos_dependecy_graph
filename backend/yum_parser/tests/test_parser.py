from django.test import SimpleTestCase
from yum_parser.services.parser import parse_repos, repos_union, PackageDependencies, get_names
from unittest.mock import patch, MagicMock
from django.test import TestCase
from pickle import dumps
from zlib import compress
from django.db import DatabaseError


class GetNamesTests(SimpleTestCase):
    def test_get_names_returns_list(self):
        deps = [('openssl', '>=1.1'), ('glibc', None)]
        result = get_names(deps)
        self.assertEqual(result, ['openssl', 'glibc'])

    def test_get_names_with_empty_input(self):
        self.assertEqual(get_names([]), [])


class ReposUnionTests(TestCase):
    @patch('yum_parser.services.parser.redis_get')
    def test_repos_union_merges_dependencies(self, mock_redis_get):
        mock_data = {
            "repo1": {
                "pkg1": PackageDependencies(["dep1"], ["prov1"]),
                "pkg2": PackageDependencies(["dep2"], ["prov2"]),
            },
            "repo2": {
                "pkg3": PackageDependencies(["dep3"], ["prov3"]),
            }
        }
        compressed_data = compress(dumps(mock_data))
        mock_redis_get.return_value = compressed_data

        result = repos_union(["repo1"])
        self.assertIn("pkg1", result)
        self.assertIn("pkg2", result)
        self.assertNotIn("pkg3", result)
    
    @patch('yum_parser.services.parser.redis_get')
    def test_repos_union_empty_input(self, mock_redis_get):
        mock_data = {
            "repo1": {
                "pkg1": PackageDependencies(["dep1"], ["prov1"]),
                "pkg2": PackageDependencies(["dep2"], ["prov2"]),
            },
            "repo2": {
                "pkg3": PackageDependencies(["dep3"], ["prov3"]),
            }
        }
        compressed_data = compress(dumps(mock_data))
        mock_redis_get.return_value = compressed_data

        result = repos_union([])
        self.assertNotIn("pkg1", result)
        self.assertNotIn("pkg2", result)
        self.assertNotIn("pkg3", result)
        
    @patch("yum_parser.tasks.parse_repos_task")
    @patch('yum_parser.services.parser.redis_get') 
    def test_repos_union_empty_redis_get(self, mock_redis_get, mock_parse_repos_task):
        mock_data = {}
        compressed_data = compress(dumps(mock_data))
        mock_redis_get.return_value = compressed_data

        result = repos_union(["repo1"])

        mock_redis_get.return_value = None

        result = repos_union(["repo1"])

        mock_parse_repos_task.delay.assert_called_once()
        assert result == {}
        

class ParseReposTests(TestCase):
    @patch('yum_parser.services.parser.disable_reparse_repos')
    @patch('yum_parser.services.parser.redis_set')
    @patch('yum_parser.services.parser.createrepo_c.Metadata')
    @patch('yum_parser.services.parser.Repo_path.objects.all')
    def test_parse_repos_successful(self, mock_repo_paths, mock_metadata_cls, mock_redis_set, mock_disable):
        mock_repo = MagicMock()
        mock_repo.get_full_url.return_value = 'http://example.repo'
        mock_repo_paths.return_value = [mock_repo]

        mock_metadata = MagicMock()
        mock_metadata.keys.return_value = ['pkg1']
        
        mock_pkg = MagicMock()
        mock_pkg.name = 'testpkg'
        mock_pkg.requires = ['dep1']
        mock_pkg.provides = ['prov1']
        mock_pkg.obsoletes = [('obs',)]
        mock_pkg.conflicts = [('conf',)]
        mock_pkg.nevra.return_value = 'nevra'
        mock_pkg.version = '1.0'
        mock_pkg.release = '1'
        mock_pkg.url = 'http://example.repo/testpkg'

        mock_metadata.get.return_value = mock_pkg
        mock_metadata_cls.return_value = mock_metadata

        parse_repos()

        self.assertTrue(mock_redis_set.called)
        self.assertTrue(mock_disable.called)

    @patch('yum_parser.services.parser.reparse_repos')
    @patch('yum_parser.services.parser.Repo_path.objects.all')
    def test_parse_repos_db_error(self, mock_repo_paths, mock_reparse_repos):
        mock_repo_paths.side_effect = DatabaseError("DB connection failed")

        parse_repos()

        mock_reparse_repos.assert_called_once()

    @patch('yum_parser.services.parser.reparse_repos')
    @patch('yum_parser.services.parser.createrepo_c.Metadata')
    @patch('yum_parser.services.parser.Repo_path.objects.all')
    def test_parse_repos_one_broken_xml_or_url(self, mock_repo_paths, mock_metadata_cls, mock_reparse_repos):
        mock_repo_1 = MagicMock()
        mock_repo_2 = MagicMock()
        mock_repo_1.get_full_url.return_value = 'http://example1.repo'
        mock_repo_2.get_full_url.return_value = 'http://example2.repo'
        mock_repo_paths.return_value = [mock_repo_1, mock_repo_2]

        mock_metadata = MagicMock()
        mock_metadata.locate_and_load_xml.side_effect = [Exception("Broken XML"), None]
        mock_metadata_cls.return_value = mock_metadata

        parse_repos()

        mock_reparse_repos.assert_called_once_with(['http://example1.repo'])
    
    @patch('yum_parser.services.parser.reparse_repos')
    @patch('yum_parser.services.parser.createrepo_c.Metadata')
    @patch('yum_parser.services.parser.Repo_path.objects.all')
    def test_parse_repos_all_broken_xml_or_url(self, mock_repo_paths, mock_metadata_cls, mock_reparse_repos):
        mock_repo_1 = MagicMock()
        mock_repo_1.get_full_url.return_value = 'http://example1.repo'
        mock_repo_paths.return_value = [mock_repo_1]

        mock_metadata = MagicMock()
        mock_metadata.locate_and_load_xml.side_effect = [Exception("Broken url")]
        mock_metadata_cls.return_value = mock_metadata

        parse_repos()

        mock_reparse_repos.assert_called_once_with()