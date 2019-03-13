from django.contrib import admin
from django.urls import path, include
from network import views

app_name = 'network'
urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('login', views.login, name='login'),
    path('callback', views.callback, name='callback'),
    path('logout', views.logout, name='logout'),
    path('recommend', views.recommend, name='recommend'),
    path('search', views.search, name='search'),
    path('needusername', views.needusername, name='needusername'),
    path('listento', views.listento, name='listento'),
    path('listentothis/<genurl>', views.listentothis, name='listentothis'),
    path('getuserstorec', views.getuserstorec, name='getuserstorec'),
    path('addmusic', views.addmusic, name='addmusic'),
    path('likemusic', views.likemusic, name='likemusic'),
    path('answer', views.answer, name='answer'),
    path('changeperm', views.changeperm, name='changeperm')

   
    ]
    