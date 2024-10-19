from django.urls import path
from . import views

urlpatterns = [
    path('', views.espacio_trabajo, name='espacio_trabajo'),
    path('crear/', views.crear_espacio, name='crear_espacio'),
    path('<int:espacio_id>/', views.detalle_espacio, name='detalle_espacio'),
    path('<int:espacio_id>/cambiar-estado/', views.cambiar_estado_espacio, name='cambiar_estado_espacio'),
    #usuarios
    path('<int:espacio_id>/agregar-usuarios/', views.agregar_usuarios, name='agregar_usuarios'),
    path('<int:espacio_id>/eliminar-usuarios/', views.eliminar_usuarios, name='eliminar_usuarios'),
    #tableros
    path('<int:espacio_id>/tableros/', views.listar_tableros, name='listar_tableros'),
    path('<int:espacio_id>/crear-tablero/', views.crear_tablero, name='crear_tablero'),
    path('tablero/<int:tablero_id>/', views.detalle_tablero, name='detalle_tablero'),
    path('tablero/<int:tablero_id>/editar/', views.editar_tablero, name='editar_tablero'),
    #listas
    path('tablero/<int:tablero_id>/crear-lista/', views.crear_lista, name='crear_lista'),
    path('lista/<int:lista_id>/editar/', views.editar_lista, name='editar_lista'),
    path('lista/<int:lista_id>/eliminar/', views.eliminar_lista, name='eliminar_lista'),
    #tarjetas
    path('lista/<int:lista_id>/crear-tarjeta/', views.crear_tarjeta, name='crear_tarjeta'),
    path('tarjeta/<int:tarjeta_id>/editar/', views.editar_tarjeta, name='editar_tarjeta'),
    path('tarjeta/<int:tarjeta_id>/eliminar/', views.eliminar_tarjeta, name='eliminar_tarjeta'),
    path('mover_tarjeta/', views.mover_tarjeta, name='mover_tarjeta'),
]
