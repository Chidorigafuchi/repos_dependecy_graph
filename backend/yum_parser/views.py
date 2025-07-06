from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.graph import Graph
from .services.package_info import Package_info
from .services.package_tracking import track_package

class PackageView(APIView):
    def post(self, request):
        pkg_name = request.data.get('name')
        repos = request.data.get('repos')

        packages_graph = Graph.get_package_graph(pkg_name, repos)
        
        return Response(packages_graph)
    
class PackageInfoView(APIView):
    def get(self, request):
        pkg_name = request.query_params.get('package_name')
        
        package_info = Package_info.get_package_info(pkg_name)

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
    