from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import EspacioTrabajo, Tablero, Lista, Tarjeta
from .forms import EspacioTrabajoForm, AgregarUsuarioForm, EliminarUsuarioForm, TableroForm, ListaForm, TarjetaForm
from django.db.models import Q

# Create your views here.

@login_required
def espacio_trabajo(request):
    espacios = EspacioTrabajo.objects.filter(usuarios=request.user)
    return render(request, 'espacio_trabajo.html', {'espacios': espacios})

@login_required
def crear_espacio(request):
    if request.method == 'POST':
        form = EspacioTrabajoForm(request.POST)
        if form.is_valid():
            espacio = form.save(commit=False)
            espacio.propietario = request.user
            espacio.save()
            espacio.usuarios.add(request.user)
            espacio.usuarios.add(*form.cleaned_data['usuarios'])
            return redirect('espacio_trabajo')
    else:
        form = EspacioTrabajoForm()
    return render(request, 'espacios_trabajo/crear_espacio.html', {'form': form})

@login_required
def detalle_espacio(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id, usuarios=request.user)
    return render(request, 'espacios_trabajo/detalle_espacio.html', {'espacio': espacio})

@login_required
def inactivar_espacio(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id)
    
    if request.user != espacio.propietario:
        return HttpResponseForbidden("No tienes permiso para inactivar este espacio de trabajo.")
    
    if request.method == 'POST':
        espacio.activo = False
        espacio.save()
        return redirect('espacio_trabajo')
    
    return render(request, 'espacios_trabajo/confirmar_inactivar.html', {'espacio': espacio})

@login_required
def cambiar_estado_espacio(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id)
    
    if request.user != espacio.propietario:
        return HttpResponseForbidden("No tienes permiso para cambiar el estado de este espacio de trabajo.")
    
    if request.method == 'POST':
        espacio.activo = not espacio.activo
        espacio.save()
        return redirect('detalle_espacio', espacio_id=espacio.id)
    
    template = 'espacios_trabajo/activar_espacio.html' if not espacio.activo else 'espacios_trabajo/inactivar_espacio.html'
    return render(request, template, {'espacio': espacio})

@login_required
def agregar_usuarios(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id)
    
    if request.user != espacio.propietario:
        return HttpResponseForbidden("No tienes permiso para agregar usuarios a este espacio de trabajo.")
    
    if request.method == 'POST':
        form = AgregarUsuarioForm(request.POST, espacio=espacio)
        if form.is_valid():
            usuarios_nuevos = form.cleaned_data['usuarios']
            espacio.usuarios.add(*usuarios_nuevos)
            return redirect('detalle_espacio', espacio_id=espacio.id)
    else:
        form = AgregarUsuarioForm(espacio=espacio)
    
    return render(request, 'espacios_trabajo/agregar_usuarios.html', {'form': form, 'espacio': espacio})

@login_required
def eliminar_usuarios(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id)
    
    if request.user != espacio.propietario:
        return HttpResponseForbidden("No tienes permiso para eliminar usuarios de este espacio de trabajo.")
    
    if request.method == 'POST':
        form = EliminarUsuarioForm(request.POST, espacio=espacio)
        if form.is_valid():
            usuarios_a_eliminar = form.cleaned_data['usuarios']
            espacio.usuarios.remove(*usuarios_a_eliminar)
            return redirect('detalle_espacio', espacio_id=espacio.id)
    else:
        form = EliminarUsuarioForm(espacio=espacio)
    
    return render(request, 'espacios_trabajo/eliminar_usuarios.html', {'form': form, 'espacio': espacio})

@login_required
def listar_tableros(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id)
    if request.user not in espacio.usuarios.all():
        return HttpResponseForbidden("No tienes permiso para ver este espacio de trabajo.")
    tableros = espacio.tableros.all()
    return render(request, 'espacios_trabajo/listar_tableros.html', {'espacio': espacio, 'tableros': tableros})

@login_required
def crear_tablero(request, espacio_id):
    espacio = get_object_or_404(EspacioTrabajo, id=espacio_id)
    if request.user not in espacio.usuarios.all():
        return HttpResponseForbidden("No tienes permiso para crear tableros en este espacio de trabajo.")
    
    if request.method == 'POST':
        form = TableroForm(request.POST)
        if form.is_valid():
            tablero = form.save(commit=False)
            tablero.espacio_trabajo = espacio
            tablero.save()
            return redirect('detalle_tablero', tablero_id=tablero.id)
    else:
        form = TableroForm()
    
    return render(request, 'espacios_trabajo/crear_tablero.html', {'form': form, 'espacio': espacio})

@login_required
def detalle_tablero(request, tablero_id):
    tablero = get_object_or_404(Tablero, id=tablero_id)
    if request.user not in tablero.espacio_trabajo.usuarios.all():
        return HttpResponseForbidden("No tienes permiso para ver este tablero.")
    
    listas = tablero.listas.all()
    usuario_filtro = request.GET.get('usuario')
    etiqueta_filtro = request.GET.get('etiqueta')
    
    for lista in listas:
        lista.sobre_wip = lista.esta_sobre_wip()
        tarjetas = lista.tarjetas.all()
        
        if usuario_filtro:
            tarjetas = tarjetas.filter(usuario_asignado__username=usuario_filtro)
        if etiqueta_filtro:
            tarjetas = tarjetas.filter(etiqueta=etiqueta_filtro)
        
        lista.tarjetas_filtradas = tarjetas
    
    usuarios = tablero.espacio_trabajo.usuarios.all()
    etiquetas = Tarjeta.objects.filter(lista__tablero=tablero).values_list('etiqueta', flat=True).distinct()
    
    return render(request, 'espacios_trabajo/detalle_tablero.html', {
        'tablero': tablero,
        'listas': listas,
        'usuarios': usuarios,
        'etiquetas': etiquetas,
        'usuario_filtro': usuario_filtro,
        'etiqueta_filtro': etiqueta_filtro,
    })

@login_required
def crear_lista(request, tablero_id):
    tablero = get_object_or_404(Tablero, id=tablero_id, espacio_trabajo__usuarios=request.user)
    
    if request.method == 'POST':
        form = ListaForm(request.POST)
        if form.is_valid():
            lista = form.save(commit=False)
            lista.tablero = tablero
            lista.orden = tablero.listas.count()
            lista.save()
            return redirect('detalle_tablero', tablero_id=tablero.id)
    else:
        form = ListaForm()
    
    return render(request, 'espacios_trabajo/crear_lista.html', {'form': form, 'tablero': tablero})

@login_required
def editar_tablero(request, tablero_id):
    tablero = get_object_or_404(Tablero, id=tablero_id, espacio_trabajo__usuarios=request.user)
    
    if request.method == 'POST':
        form = TableroForm(request.POST, instance=tablero)
        if form.is_valid():
            form.save()
            return redirect('detalle_tablero', tablero_id=tablero.id)
    else:
        form = TableroForm(instance=tablero)
    
    return render(request, 'espacios_trabajo/editar_tablero.html', {'form': form, 'tablero': tablero})

@login_required
def editar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)
    tablero = lista.tablero
    
    if request.user not in tablero.espacio_trabajo.usuarios.all():
        return HttpResponseForbidden("No tienes permiso para editar esta lista.")
    
    if request.method == 'POST':
        form = ListaForm(request.POST, instance=lista)
        if form.is_valid():
            form.save()
            return redirect('detalle_tablero', tablero_id=tablero.id)
    else:
        form = ListaForm(instance=lista)
    
    return render(request, 'espacios_trabajo/editar_lista.html', {'form': form, 'lista': lista, 'tablero': tablero})

@login_required
def eliminar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)
    tablero = lista.tablero
    
    if request.user not in tablero.espacio_trabajo.usuarios.all():
        return HttpResponseForbidden("No tienes permiso para eliminar esta lista.")
    
    if request.method == 'POST':
        lista.delete()
        return redirect('detalle_tablero', tablero_id=tablero.id)
    
    return render(request, 'espacios_trabajo/confirmar_eliminar_lista.html', {'lista': lista, 'tablero': tablero})

@login_required
def crear_tarjeta(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)
    espacio_trabajo = lista.tablero.espacio_trabajo
    if request.method == 'POST':
        form = TarjetaForm(request.POST, espacio_trabajo=espacio_trabajo)
        if form.is_valid():
            tarjeta = form.save(commit=False)
            tarjeta.lista = lista
            tarjeta.save()
            return redirect('detalle_tablero', tablero_id=lista.tablero.id)
    else:
        form = TarjetaForm(espacio_trabajo=espacio_trabajo)
    return render(request, 'espacios_trabajo/crear_tarjeta.html', {'form': form, 'lista': lista})

@login_required
def editar_tarjeta(request, tarjeta_id):
    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)
    espacio_trabajo = tarjeta.lista.tablero.espacio_trabajo
    if request.method == 'POST':
        form = TarjetaForm(request.POST, instance=tarjeta, espacio_trabajo=espacio_trabajo)
        if form.is_valid():
            form.save()
            return redirect('detalle_tablero', tablero_id=tarjeta.lista.tablero.id)
    else:
        form = TarjetaForm(instance=tarjeta, espacio_trabajo=espacio_trabajo)
    return render(request, 'espacios_trabajo/editar_tarjeta.html', {'form': form, 'tarjeta': tarjeta})

@login_required
def eliminar_tarjeta(request, tarjeta_id):
    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)
    if request.method == 'POST':
        tablero_id = tarjeta.lista.tablero.id
        tarjeta.delete()
        return redirect('detalle_tablero', tablero_id=tablero_id)
    return render(request, 'espacios_trabajo/confirmar_eliminar_tarjeta.html', {'tarjeta': tarjeta})
