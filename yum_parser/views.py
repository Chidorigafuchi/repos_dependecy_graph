from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.graph import Graph
from .services.package_info import get_package_info

# Create your views here.
class PackageView(APIView):
    def post(self, request):
        packages_graph = Graph.get_package_graph(request.data['name'], request.data['repos'])
        
        return Response(packages_graph)
    
class PackageInfoView(APIView):
    def get(self, request):
        package_info = get_package_info(request.query_params.get('name'))

        return Response(package_info)
    