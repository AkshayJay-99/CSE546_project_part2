from django.contrib import admin
from django.urls import include, path
from imglookup_app import views


urlpatterns = [
    path("", views.imglookup, name = "imglookup" )
]