from django.urls import path
from . import views

urlpatterns = [

    path('', views.activities, name='activities'),

    path('add/', views.activities, name='add_activity'),

    path('my-activities/', views.my_activities, name='my_activities'),

]