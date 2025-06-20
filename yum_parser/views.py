from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PackageSerializer, PackageResponseSerializer
from .parser import parse_package

# Create your views here.
class PackageView(APIView):
    def post(self, request):
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            package_name = serializer.validated_data['name']
            try:
                package_data = parse_package(package_name)
                response_serializer = PackageResponseSerializer(package_data)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)