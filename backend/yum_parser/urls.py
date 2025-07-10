from django.urls import path
from .views import (
    AvailableReposView,
    PackageView, 
    PackageInfoView, 
    TrackPackageView,
    TrackedPackagesListView
)

urlpatterns = [
    path('available_repos/', AvailableReposView.as_view(), name='available_repos'),
    path('package/', PackageView.as_view(), name='package'),
    path('package_info/', PackageInfoView.as_view(), name='package_info'),
    path('track_package/', TrackPackageView.as_view(), name='track_package'),
    path('tracked_packages_list/', TrackedPackagesListView.as_view(), name='tracked_packages_list'),
]