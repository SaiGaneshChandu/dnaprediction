from django.contrib import admin
from django.urls import path
from bioapp import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', views.welcome),

    path('login/', views.login_view),
    path('register/', views.register),
    path('logout/', views.logout_view),

    path('home/', views.home),

    path('predict/', views.predict),

    path('admin-dashboard/', views.admin_dashboard),

    path('create-user/', views.create_user),
    path('edit-user/', views.edit_user),
    path('delete-user/<str:username>/', views.delete_user),

    path('delete-report/<int:sno>/', views.delete_report),

]