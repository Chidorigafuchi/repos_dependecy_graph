from rest_framework.views import APIView
from rest_framework.response import Response
from pickle import loads

from .services.graph import get_package_graph_with_cache
from .services.package_info import get_package_info_with_cache
from .services.package_tracking import track_package
from .services.tracked_packages import get_tracked_packages_list, delete_tracked_package_from_db
from .services.package_versions_diff import get_package_version_diff, get_package_versions
from repos_dependency_graph.services.redis import redis_get


def get_or_create_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

class AvailableReposView(APIView):
    def get(self, request):
        available_repos = loads(redis_get('available_repos'))

        return Response(available_repos)

class PackageView(APIView):
    def post(self, request):
        session_key = get_or_create_session_key(request)
        pkg_name = request.data.get('name')
        repos = request.data.get('repos')

        packages_graph = get_package_graph_with_cache(session_key, pkg_name, repos)
        
        return Response(packages_graph)
    
class PackageInfoView(APIView):
    def get(self, request):
        session_key = get_or_create_session_key(request)
        pkg_name = request.query_params.get('name')        
        
        package_info = get_package_info_with_cache(session_key, pkg_name)

        return Response(package_info)
    
class TrackPackageView(APIView):
    def post(self, request):
        session_key = get_or_create_session_key(request)
        pkg_name = request.data.get('name')
        repos = request.data.get('repos')

        result = track_package(session_key, pkg_name, repos)

        return Response(result)
    

class TrackedPackagesListView(APIView):
    def get(self, request):
        session_key = get_or_create_session_key(request)

        tracked_packages = get_tracked_packages_list(session_key)

        return Response(tracked_packages)
    
    def delete(self, request):
        session_key = get_or_create_session_key(request)
        pkg_name = request.data.get('package')
        repos = request.data.get('repos')

        deleted = delete_tracked_package_from_db(session_key, pkg_name, repos)

        return Response(deleted)
    
class VersionDiffView(APIView):
    def get(self, request):
        session_key = get_or_create_session_key(request)
        pkg_name = request.query_params.get('name')
        repos = request.query_params.getlist('repos[]')

        result = get_package_versions(session_key, pkg_name, repos)

        return Response(result)

    def post(self, request):
        session_key = get_or_create_session_key(request)
        pkg_name = request.data.get('name')
        repos = request.data.get('repos')
        nevra = request.data.get('nevra')

        result = get_package_version_diff(session_key, pkg_name, repos, nevra)

        return Response(result)
    