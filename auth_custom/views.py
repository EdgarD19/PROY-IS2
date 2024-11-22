from django.shortcuts import render

# Create your views here.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm #importa el formulario de registro y el formulario de autenticacion de django
from django.contrib.auth import login, authenticate, logout #importa las funciones de autenticacion de django
from django.contrib.auth.models import User  
from django.shortcuts import redirect #redirecciona la pagina 
from django.db import IntegrityError #maneja los errores de integridad de la base de datos
from django.contrib.auth.decorators import login_required #decorador para verificar si el usuario esta autenticado
from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import ModelBackend  # Añade esta importación

def home(request):
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', 
        {
            'form': UserCreationForm #formulario de registro por defecto 
        })

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                #'username' y 'password1' son los nombres de los campos en el formulario de registro que se inspeccionan en el html(verificar con el inspector del navegador)
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1']) 
                user.save() #guarda el usuario en la base de datos
                login(request, user, backend='django.contrib.auth.backends.ModelBackend') 
                return redirect('espacio_trabajo') 
            except IntegrityError:
                return render(request, 'signup.html', 
                {
                    'form': UserCreationForm, #envia el formulario de registro
                    'error': 'El usuario ya existe' 
                })
        return render(request, 'signup.html',{
            'form': UserCreationForm,
            'error': 'La contraseña no coincide'
        })
    

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html',
        {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], 
                        password=request.POST['password']) 
        if user is None: #si el usuario no existe
            return render(request, 'signin.html',
            {
                'form': AuthenticationForm,
                'error': 'Nombre de usuario o contraseña incorrectos'
            })
        else:
            login(request, user) 
            return redirect('espacio_trabajo')

@login_required
def signout(request):
    logout(request) #elimina la cookie de autenticacion del usuario
    return redirect('home')
