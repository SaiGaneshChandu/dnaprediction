from django.urls import path
from . import views

urlpatterns = [

    # ===== PUBLIC PAGES =====
    path('', views.welcome, name='welcome'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ===== USER AREA =====
    path('home/', views.home, name='home'),
    path('predict/', views.predict, name='predict'),

    # ===== ADMIN DASHBOARD =====
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-user/', views.create_user, name='create_user'),
    path('edit-user/', views.edit_user, name='edit_user'),
    path('delete-user/<str:username>/', views.delete_user, name='delete_user'),
    path('delete-report/<int:sno>/', views.delete_report, name='delete_report'),

    # ===== MOBILE API =====
    path('api/predict/', views.api_predict, name='api_predict'),
]