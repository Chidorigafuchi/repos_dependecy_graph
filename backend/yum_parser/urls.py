from django.urls import path
from .views import PackageView, PackageInfoView, TrackPackageView

urlpatterns = [
    path('package/', PackageView.as_view(), name='package'),
    path('package_info/', PackageInfoView.as_view(), name='package_info'),
    path('track_package/', TrackPackageView.as_view(), name='track_package'),
]