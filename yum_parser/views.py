from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.graph import Graph

# Create your views here.
class PackageView(APIView):
    def post(self, request):
        packages_graph = Graph.get_package_graph(request.data['name'], request.data['repos'])

        return Response(packages_graph)