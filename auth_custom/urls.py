from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),    
    path('signup/', views.signup, name='signup'), #REGISTRARSE
    path('signin/', views.signin, name='signin'), #INICIAR SESION
    path('signout/', views.signout, name='signout'), #CERRAR SESION
]


