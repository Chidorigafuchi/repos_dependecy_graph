from unittest import TestCase
from unittest.mock import patch
from yum_parser.services.package_info import get_package_info, get_package_info_with_cache
from yum_parser.services.parser import PackageInfo
from pickle import dumps
from zlib import compress


class PackageInfoTests(TestCase):
    @patch('yum_parser.services.package_info.redis_get')
    def test_get_package_info_found(self, mock_redis_get):
        info = PackageInfo(nevra="mypkg-1.0-1", version="1.0", release="1", obsoletes=["oldpkg"], conflicts=["conflict"])
        fake_cache = {"mypackage": info}
        compressed_data = compress(dumps(fake_cache))

        mock_redis_get.return_value = compressed_data

        result = get_package_info("mypackage")
        self.assertIsInstance(result, PackageInfo)
        self.assertEqual(result.nevra, "mypkg-1.0-1")
        self.assertIn("oldpkg", result.obsoletes)

        result2 = get_package_info("fakePackage")
        self.assertIsInstance(result2, PackageInfo)

    @patch('yum_parser.services.package_info.redis_get')
    @patch('yum_parser.tasks.parse_repos_task')
    def test_get_package_info_not_found_triggers_reparse(self, mock_parse_task, mock_redis_get):
        mock_redis_get.return_value = None

        result = get_package_info("mypackage")
        self.assertIsInstance(result, PackageInfo) 
        self.assertEqual(result.nevra, "")
        mock_parse_task.delay.assert_called_once()

    @patch('yum_parser.services.package_info.redis_set')
    @patch('yum_parser.services.package_info.redis_get')
    @patch('yum_parser.services.package_info.get_package_info')
    def test_get_package_info_with_cache_miss(self, mock_get_package_info, mock_redis_get, mock_redis_set):
        mock_redis_get.return_value = None
        info = PackageInfo(nevra="mypkg-1.2-3", version="1.2", release="3")
        mock_get_package_info.return_value = info

        result = get_package_info_with_cache("sess123", "mypackage")

        self.assertEqual(result['nevra'], "mypkg-1.2-3")
        mock_redis_set.assert_called_once()
        self.assertIn("version", result)

    @patch('yum_parser.services.package_info.redis_get')
    def test_get_package_info_with_cache_hit(self, mock_redis_get):
        cached_info = PackageInfo(nevra="cached-2.0", version="2.0")
        mock_redis_get.return_value = dumps(cached_info.__dict__)

        result = get_package_info_with_cache("sess123", "mypackage")

        self.assertEqual(result['nevra'], "cached-2.0")
        self.assertIn("version", result)
