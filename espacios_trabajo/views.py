from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import EspacioTrabajo, Tablero, Lista, Tarjeta
from .forms import EspacioTrabajoForm, AgregarUsuarioForm, EliminarUsuarioForm, TableroForm, ListaForm, TarjetaForm
from django.db.models import Q
from django.views.decorators.http import require_POST
import json
from django.utils import timezone

# Create your views here.

@login_required
def espacio_trabajo(request):
    espacios = EspacioTrabajo.objects.filter(usuarios=request.user)
    return render(request, 'espacio_trabajo.html', {'espacios': espacios})

@login_required
def crear_espacio(request):
    if request.method == 'POST':
        form = EspacioTrabajoForm(request.POST, usuario_actual=request.user)
        if form.is_valid():
            espacio = form.save(commit=False)
            espacio.propietario = request.user
            espacio.save()
            espacio.usuarios.add(request.user)
            espacio.usuarios.add(*form.cleaned_data['usuarios'])
            return redirect('espacio_trabajo')
    else:
        form = EspacioTrabajoForm(usuario_actual=request.user)
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

            # Crear las listas por defecto
            crear_listas_por_defecto(tablero)
            return redirect('detalle_tablero', tablero_id=tablero.id)
    else:
        form = TableroForm()
    
    return render(request, 'espacios_trabajo/crear_tablero.html', {'form': form, 'espacio': espacio})


def crear_listas_por_defecto(tablero):
    nombres_listas = ["To Do", "Doing", "Done"]
    for nombre in nombres_listas:
        Lista.objects.create(nombre=nombre, tablero=tablero, max_wip=5)

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
def eliminar_tablero(request, tablero_id):
    tablero = get_object_or_404(Tablero, id=tablero_id)
    
    if request.user not in tablero.espacio_trabajo.usuarios.all():
        return HttpResponseForbidden("No tienes permiso para eliminar este tablero.")
    
    if request.method == 'POST':
        tablero.delete()
        return redirect('listar_tableros', espacio_id=tablero.espacio_trabajo.id)
    
    return render(request, 'espacios_trabajo/confirmar_eliminar_tablero.html', {'tablero': tablero})

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

@require_POST
def mover_tarjeta(request):
    tarjeta_id = request.POST.get('tarjeta_id')
    nueva_lista_id = request.POST.get('nueva_lista_id')
    
    try:
        tarjeta = Tarjeta.objects.get(id=tarjeta_id)
        nueva_lista = Lista.objects.get(id=nueva_lista_id)
        
        tarjeta.lista = nueva_lista
        tarjeta.save()
        
        return JsonResponse({'status': 'success'})
    except (Tarjeta.DoesNotExist, Lista.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Tarjeta o lista no encontrada'}, status=400)

@require_POST
def mover_lista(request):
    try:
        lista_id = request.POST.get('lista_id')
        nuevo_orden = request.POST.get('nuevo_orden')
        
        lista = Lista.objects.get(id=lista_id)
        lista.orden = nuevo_orden
        lista.save()
        
        # Reordenar las demás listas si es necesario
        listas = Lista.objects.filter(tablero=lista.tablero).exclude(id=lista.id)
        for idx, otra_lista in enumerate(listas):
            if idx >= int(nuevo_orden):
                otra_lista.orden = idx + 1
                otra_lista.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def dashboard_tablero(request, tablero_id):
    tablero = get_object_or_404(Tablero, id=tablero_id)

    # Validar distribución de tareas
    listas = tablero.listas.all()
    distribucion_tareas = {
        'labels': [lista.nombre for lista in listas],
        'data': [lista.tarjetas.count() for lista in listas]
    }

    # Validar tareas por usuario
    usuarios_dict = {}
    for lista in listas:
        for tarjeta in lista.tarjetas.all():
            if tarjeta.usuario_asignado:
                nombre_usuario = tarjeta.usuario_asignado.username
                usuarios_dict[nombre_usuario] = usuarios_dict.get(nombre_usuario, 0) + 1

    tareas_por_usuario = {
        'labels': list(usuarios_dict.keys()),
        'data': list(usuarios_dict.values())
    }

    # Validar estado de vencimiento
    hoy = timezone.now().date()
    atrasadas = 0
    a_tiempo = 0
    sin_fecha = 0

    for lista in listas:
        for tarjeta in lista.tarjetas.all():
            if tarjeta.fecha_vencimiento:
                if tarjeta.fecha_vencimiento < hoy:
                    atrasadas += 1
                else:
                    a_tiempo += 1
            else:
                sin_fecha += 1

    estado_vencimiento = {
        'labels': ['Atrasadas', 'A tiempo', 'Sin fecha'],
        'data': [atrasadas, a_tiempo, sin_fecha]
    }

    # Serializar a JSON y pasar al contexto
    context = {
        'tablero': tablero,
        'distribucion_tareas': json.dumps(distribucion_tareas),
        'tareas_por_usuario': json.dumps(tareas_por_usuario),
        'estado_vencimiento': json.dumps(estado_vencimiento)
    }

    return render(request, 'espacios_trabajo/dashboard.html', context)
