from django.test import TestCase
from django.db import DatabaseError
from unittest.mock import patch, MagicMock
from hashlib import sha1
from json import dumps

from yum_parser.services.tracked_packages import get_tracked_packages_list, delete_tracked_package_from_db


class TrackedPackageTests(TestCase):
    def setUp(self):
        self.session_key = "abc123"
        self.package_name = "mypkg"
        self.repos = ["http://mirror1/repo", "http://mirror2/repo"]
        self.sorted_repos = sorted(self.repos)
        self.repos_hash = sha1(dumps(self.sorted_repos).encode()).hexdigest()

    @patch("yum_parser.services.tracked_packages.Tracked_package.objects")
    def test_get_tracked_packages_list_success(self, mock_objects):
        mock_repo = MagicMock()
        mock_repo.get_full_url.side_effect = self.repos

        mock_tp_repo = MagicMock()
        mock_tp_repo.repo = mock_repo

        tracked_package = MagicMock()
        tracked_package.name = self.package_name
        tracked_package.session_key = self.session_key
        tracked_package.tracked_package_repo_set.all.return_value = [mock_tp_repo, mock_tp_repo]

        mock_objects.all.return_value = [tracked_package]

        result = get_tracked_packages_list(self.session_key)

        self.assertIn(self.package_name, result)
        self.assertEqual(result[self.package_name], [self.repos])

    @patch("yum_parser.services.tracked_packages.Tracked_package.objects")
    def test_get_tracked_packages_list_database_error(self, mock_objects):
        mock_objects.all.side_effect = DatabaseError("DB error")
        result = get_tracked_packages_list(self.session_key)
        self.assertEqual(result, {})

    @patch("yum_parser.services.tracked_packages.Tracked_package.objects.get")
    def test_delete_tracked_package_success(self, mock_get):
        mock_instance = MagicMock()
        mock_get.return_value = mock_instance

        result = delete_tracked_package_from_db(self.session_key, self.package_name, self.repos)

        self.assertTrue(result)
        mock_instance.delete.assert_called_once()

        expected_hash = sha1(dumps(sorted(self.repos)).encode()).hexdigest()
        mock_get.assert_called_once_with(
            session_key=self.session_key,
            name=self.package_name,
            repos_hash=expected_hash
        )

    @patch("yum_parser.services.tracked_packages.Tracked_package.objects.get")
    def test_delete_tracked_package_not_found(self, mock_get):
        mock_get.side_effect = DatabaseError("Not found")
        result = delete_tracked_package_from_db(self.session_key, self.package_name, self.repos)
        self.assertFalse(result)
