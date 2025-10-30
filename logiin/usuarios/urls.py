# usuarios/urls.py
from django.urls import path
from . import views
from django.views.generic import TemplateView
urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro_admin, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),

    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/residente/', views.dashboard_residente, name='dashboard_residente'),
    path('dashboard/residente/cambiar-password/', views.cambiar_password_residente, name='cambiar_password_residente'),
    # Residentes (listado + CRUD desde admin)
    path('residentes/', views.gestion_residentes, name='gestion_residentes'),
    path('residentes/agregar/', views.agregar_residente_from_admin, name='agregar_residente'),
    path('residentes/editar/<str:usuario>/', views.editar_residente, name='editar_residente'),
    path('residentes/borrar/<str:usuario>/', views.borrar_residente, name='borrar_residente'),

    # Apartamentos
    path('apartamentos/', views.gestion_apartamentos, name='gestion_apartamentos'),
    path('apartamentos/agregar/', views.agregar_apartamento, name='agregar_apartamento'),
    path('apartamentos/editar/<int:apt_id>/', views.editar_apartamento, name='editar_apartamento'),
    path('apartamentos/eliminar/<int:apt_id>/', views.eliminar_apartamento, name='eliminar_apartamento'),
    path('apartamentos/anadir-residente/<int:numero>/', views.anadir_residente_departamento, name='anadir_residente_departamento'),

    # Personal
    path('personal/', views.gestion_personal, name='gestion_personal'),
    path('personal/agregar/', views.agregar_personal, name='agregar_personal'),
    path('personal/agregar-provisional/', views.agregar_personal_provisional, name='agregar_personal_provisional'),
    path('personal/editar/<int:pid>/', views.editar_personal, name='editar_personal'),
    path('personal/borrar/<int:pid>/', views.borrar_personal, name='borrar_personal'),


    ###
    # Finanzas e Informes
path('finanzas/', views.gestion_finanzas, name='gestion_finanzas'),
path('informes/', views.panel_informes, name='panel_informes'),

# Dashboard de residente - vistas adicionales
path('dashboard/residente/reservas/', views.reservas_residente, name='reservas_residente'),
path('dashboard/residente/pagos/', views.pagos_residente, name='pagos_residente'),
]

