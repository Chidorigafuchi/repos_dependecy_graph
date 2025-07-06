from rest_framework.views import APIView
from rest_framework.response import Response
from .services.graph import get_package_graph_with_cache
from .services.package_info import get_package_info_with_cache
from .services.package_tracking import track_package

class PackageView(APIView):
    def post(self, request):
        session_key = request.session.session_key
        pkg_name = request.data.get('name')
        repos = request.data.get('repos')

        packages_graph = get_package_graph_with_cache(session_key, pkg_name, repos)
        
        return Response(packages_graph)
    
class PackageInfoView(APIView):
    def get(self, request):
        session_key = request.session.session_key
        pkg_name = request.query_params.get('name')        
        
        package_info = get_package_info_with_cache(session_key, pkg_name)

        return Response(package_info)
    
class TrackPackageView(APIView):
    def post(self, request):
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key
        pkg_name = request.data.get('name')
        repos = request.data.get('repos')

        result = track_package(session_key, pkg_name, repos)

        return Response(result)
    