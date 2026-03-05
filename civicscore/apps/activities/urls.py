from django.urls import path
from . import views

urlpatterns = [
  path('/activities', views.activities, name='activities'),
]
