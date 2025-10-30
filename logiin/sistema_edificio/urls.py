from django.contrib import admin
from django.urls import path, include
from usuarios import views
from django.contrib.auth import views as auth_views
from usuarios import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # rutas de usuarios (tu app)
    path('', user_views.home, name='home'),
    path('usuarios/', include('usuarios.urls')),

    # Vistas built-in para reset de contraseña
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset_form.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'),
         name='password_reset_complete'),
    path('', views.home, name='home'),
    #path('registro/', views.registro, name='registro'),
    path('registro/', user_views.registro_admin, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #path('dashboard/', views.dashboard, name='dashboard'),
]
