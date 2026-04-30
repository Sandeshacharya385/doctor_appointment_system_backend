from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactInformationViewSet

router = DefaultRouter()
router.register(r'contact', ContactInformationViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
