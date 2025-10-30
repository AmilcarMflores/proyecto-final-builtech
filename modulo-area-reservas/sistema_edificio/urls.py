"""
URL configuration for sistema_edificio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from usuarios import views as usuarios_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", usuarios_views.home, name="home"), 
    path('login/', usuarios_views.login_view, name='login'),
    path('reservas/', usuarios_views.reservas, name='reservas'),
    path('reservas_disponibles/<int:area_id>/', usuarios_views.reservas_disponibles, name='reservas_disponibles'),
    path('horarios_disponibles/<int:area_id>/', usuarios_views.horarios_disponibles, name='horarios_disponibles'),
    path('logout/', usuarios_views.logout_view, name='logout'),
    path('dashboard/', usuarios_views.dashboard, name='dashboard'),
    path('fechas_ocupadas/<int:area_id>/', usuarios_views.fechas_ocupadas, name='fechas_ocupadas'),
    path('editar-reserva/<int:reserva_id>/', usuarios_views.editar_reserva, name='editar_reserva'),
    path('eliminar-reserva/<int:reserva_id>/', usuarios_views.eliminar_reserva, name='eliminar_reserva'),
    path('facturas/', usuarios_views.facturas_view, name='facturas'),
    path('financiera/', usuarios_views.modulo_financiero, name='modulo_financiero'),
]