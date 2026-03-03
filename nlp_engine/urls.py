from django.urls import path
from . import views

urlpatterns = [
    path('test_fuzzy/', views.test_fuzzy, name='test_fuzzy'),
    path('test_ml/', views.test_ml, name='test_ml'),
    path('test_hybrid/', views.test_hybrid, name='test_hybrid'),
]