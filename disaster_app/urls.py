from django.urls import path

from . import views

urlpatterns = [

    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'incident/create/',
        views.create_incident,
        name='create_incident'
    ),

]