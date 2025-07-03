from django.urls import path
from .views import PackageView

urlpatterns = [
    path('package/', PackageView.as_view(), name='package')
]