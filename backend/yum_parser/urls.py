from django.urls import path
from .views import PackageView, PackageInfoView

urlpatterns = [
    path('package/', PackageView.as_view(), name='package'),
    path('package_info/', PackageInfoView.as_view(), name='package_info'),
]