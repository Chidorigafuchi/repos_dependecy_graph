from unittest import TestCase
from unittest.mock import patch, MagicMock
from yum_parser.services.package_tracking import track_package, save_package_snapshot
from yum_parser.models import Tracked_package, Tracked_package_repo, Repo_path, Package_nevra_info
from yum_parser.services.graph import PackageGraph
from django.db import DatabaseError


class PackageTrackingTests(TestCase):

    @patch('yum_parser.services.package_tracking.get_package_graph')
    @patch('yum_parser.services.package_tracking.get_package_info')
    @patch('yum_parser.services.package_tracking.Package_nevra_info.objects.get_or_create')
    @patch('yum_parser.services.package_tracking.Tracked_package_repo.objects.get_or_create')
    @patch('yum_parser.services.package_tracking.Tracked_package.objects.get_or_create')
    @patch('yum_parser.services.package_tracking.Repo_path.objects.select_related')
    def test_track_package_success_created(self, mock_select_related, mock_tracked_pkg_get_or_create, 
                                           mock_tracked_pkg_repo_get_or_create, mock_nevra_get_or_create,
                                           mock_get_package_info, mock_get_package_graph):
        mock_repo1 = MagicMock()
        mock_repo1.get_full_url.return_value = 'http://repo1'
        mock_select_related.return_value.all.return_value = [mock_repo1]

        mock_tracked_pkg = MagicMock()
        mock_tracked_pkg_get_or_create.return_value = (mock_tracked_pkg, True)  
        
        mock_tracked_pkg_repo_get_or_create.return_value = (MagicMock(), True)
        mock_nevra_get_or_create.return_value = (MagicMock(), True)

        mock_get_package_graph.return_value = PackageGraph()
        mock_get_package_info.return_value = MagicMock(nevra='nevra', obsoletes=[], conflicts=[])

        result = track_package('sess123', 'mypackage', ['http://repo1'])

        self.assertEqual(result, {'track_created': True})
        mock_tracked_pkg_get_or_create.assert_called_once()
        mock_tracked_pkg_repo_get_or_create.assert_called()
        mock_nevra_get_or_create.assert_called_once()
    
    @patch('yum_parser.services.package_tracking.Repo_path.objects.select_related')
    def test_track_package_no_matching_repos(self, mock_select_related):
        mock_repo = MagicMock()
        mock_repo.get_full_url.return_value = 'http://otherrepo'
        mock_select_related.return_value.all.return_value = [mock_repo]

        result = track_package('sess123', 'mypackage', ['http://notfoundrepo'])

        self.assertEqual(result, {'track_created': 'unknown'})
    
    @patch('yum_parser.services.package_tracking.Repo_path.objects.select_related')
    def test_track_package_db_error_fetch_repos(self, mock_select_related):
        mock_select_related.return_value.all.side_effect = DatabaseError('DB failure')

        result = track_package('sess123', 'mypackage', ['http://repo1'])

        self.assertEqual(result, {'track_created': 'unknown'})

    @patch('yum_parser.services.package_tracking.Tracked_package.objects.get_or_create')
    @patch('yum_parser.services.package_tracking.Repo_path.objects.select_related')
    def test_track_package_db_error_create_tracked_package(self, mock_select_related, mock_tracked_pkg_get_or_create):
        mock_repo = MagicMock()
        mock_repo.get_full_url.return_value = 'http://repo1'
        mock_select_related.return_value.all.return_value = [mock_repo]

        mock_tracked_pkg_get_or_create.side_effect = DatabaseError('DB failure')

        result = track_package('sess123', 'mypackage', ['http://repo1'])

        self.assertEqual(result, {'track_created': 'unknown'})

    @patch('yum_parser.services.package_tracking.Tracked_package_repo.objects.get_or_create')
    @patch('yum_parser.services.package_tracking.Tracked_package.objects.get_or_create')
    @patch('yum_parser.services.package_tracking.Repo_path.objects.select_related')
    def test_track_package_db_error_create_tracked_package_repo(self, mock_select_related, mock_tracked_pkg_get_or_create, mock_tracked_pkg_repo_get_or_create):
        mock_repo = MagicMock()
        mock_repo.get_full_url.return_value = 'http://repo1'
        mock_select_related.return_value.all.return_value = [mock_repo]

        mock_tracked_pkg = MagicMock()
        mock_tracked_pkg_get_or_create.return_value = (mock_tracked_pkg, True)
        mock_tracked_pkg_repo_get_or_create.side_effect = DatabaseError('DB failure')

        result = track_package('sess123', 'mypackage', ['http://repo1'])

        self.assertEqual(result, {'track_created': 'unknown'})

    @patch('yum_parser.services.package_tracking.Package_nevra_info.objects.get_or_create')
    def test_save_package_snapshot_success(self, mock_nevra_get_or_create):
        mock_nevra_get_or_create.return_value = (MagicMock(), True)
        tracked_package = MagicMock()
        graph = PackageGraph()
        info = MagicMock(nevra='nevra', obsoletes=['obs'], conflicts=['conf'])

        result = save_package_snapshot(tracked_package, graph, info)
        self.assertTrue(result)
        mock_nevra_get_or_create.assert_called_once()

    @patch('yum_parser.services.package_tracking.Package_nevra_info.objects.get_or_create')
    def test_save_package_snapshot_db_error(self, mock_nevra_get_or_create):
        mock_nevra_get_or_create.side_effect = DatabaseError('DB failure')
        tracked_package = MagicMock()
        graph = PackageGraph()
        info = MagicMock(nevra='nevra', obsoletes=['obs'], conflicts=['conf'])

        result = save_package_snapshot(tracked_package, graph, info)
        self.assertFalse(result)