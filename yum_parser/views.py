from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.parser import Parser

# Create your views here.
class PackageView(APIView):
    def post(self, request):
        packages_graph = Parser.get_package_graph(request.data['name'])

        return Response(packages_graph)