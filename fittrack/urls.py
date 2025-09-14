
from django.contrib import admin
from django.urls import path
from tracker import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name="tracker/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log/', views.log_view, name='log'),
    path('weekly-summary/', views.weekly_summary, name='weekly_summary'),
    path('export/csv/', views.export_csv, name='export_csv'),
]
