from django.urls import path
from .views import (
    PackageView, 
    PackageInfoView, 
    TrackPackageView,
    TrackedPackagesListView
)

urlpatterns = [
    path('package/', PackageView.as_view(), name='package'),
    path('package_info/', PackageInfoView.as_view(), name='package_info'),
    path('track_package/', TrackPackageView.as_view(), name='track_package'),
    path('tracked_packages_list/', TrackedPackagesListView.as_view(), name='tracked_packages_list'),
]