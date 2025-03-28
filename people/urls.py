from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('person/<slug:slug>/', views.show_person, name='person'),
    path('country/<slug:slug>/', views.stars_by_country, name='stars_by_country'), # Знаменитости по стране
    path('industry/<slug:slug>/', views.stars_by_category, name='stars_by_category'), # Знаменитости по виду деятельности
    path('add/', views.add_star, name='add_star'),  # Добавление знаменитости

# Маршруты для аутентификации
    path('login/', auth_views.LoginView.as_view(template_name='people/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]