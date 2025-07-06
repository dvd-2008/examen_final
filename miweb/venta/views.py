from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.db import transaction

from .models import Cliente, Producto, VentaSimple
from .forms import (ClienteCreateForm, ClienteUpdateForm, 
                   ProductoCreateForm, ProductoUpdateForm,
                   VentaSimpleForm)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)  
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Error de usuario o clave')
        else:
            messages.error(request, 'Ingrese los datos')
    return render(request, 'venta/autenticacion/login.html')

@login_required
def home(request):
    user_permissions = {
        'can_manage_clients': (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_cliente').exists() or
            request.user.has_perm('venta.add_cliente')
        ),
        'can_manage_products': (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_producto').exists()
        ),
        'can_manage_providers': (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_proveedor').exists()
        ),
        'can_manage_sales': (
            request.user.is_superuser or
            request.user.groups.filter(name='grp_venta').exists()
        ),
        'is_admin': request.user.is_superuser
    }

    context = {
        'user_permissions': user_permissions,
        'user': request.user
    }
    return render(request, 'venta/autenticacion/home.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente')
    return redirect('login')

# ====================== VISTAS PARA CLIENTES ======================
@login_required
@permission_required('venta.view_cliente', raise_exception=True)
def consulta_clientes(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='grp_cliente').exists() or
            request.user.has_perm('venta.view_cliente')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')
    
    clientes = Cliente.objects.all().order_by('ape_nombre')
    context = {
        'clientes': clientes,
        'titulo': 'Lista de Clientes',
        'mensaje': 'Listado completo de clientes'
    }
    return render(request, 'venta/clientes/lista_clientes.html', context)

@login_required
@permission_required('venta.add_cliente', raise_exception=True)
def crear_cliente(request):
    dni_duplicado = False

    if request.method == 'POST':
        form = ClienteCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente registrado correctamente')
            return redirect('crear_cliente')
        else:
            if 'id_cliente' in form.errors:
                for error in form.errors['id_cliente']:
                    if str(error) == "DNI_DUPLICADO":
                        dni_duplicado = True
                        form.errors['id_cliente'].clear()
                        break
    else:
        form = ClienteCreateForm()

    context = {
        'form': form,
        'dni_duplicado': dni_duplicado
    }
    return render(request, 'venta/clientes/crear_cliente.html', context)

@login_required
@permission_required('venta.change_cliente', raise_exception=True)
def actualizar_cliente(request):
    cliente = None
    dni_buscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            dni_buscado = request.POST.get('dni_busqueda')
            if dni_buscado:
                try:
                    cliente = Cliente.objects.get(id_cliente=dni_buscado)
                    form = ClienteUpdateForm(instance=cliente)
                    messages.success(request, f'Cliente con DNI {dni_buscado} encontrado')
                except Cliente.DoesNotExist:
                    messages.error(request, 'No se encontró Cliente con ese DNI')    
            else:
                messages.error(request, 'Por favor ingrese el DNI para buscar') 
        elif 'guardar' in request.POST:
            dni_buscado = request.POST.get('dni_busqueda') or request.POST.get('id_cliente')
            if dni_buscado:
                try:
                    cliente = Cliente.objects.get(id_cliente=dni_buscado)
                    form = ClienteUpdateForm(request.POST, instance=cliente)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Cliente actualizado correctamente')
                        cliente.refresh_from_db()
                        form = ClienteUpdateForm(instance=cliente)
                    else:
                        messages.error(request, 'Error en los datos del formulario')
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
            else:
                messages.error(request, 'No se puede identificar al cliente para actualizar')
    context = {
        'form': form,
        'dni_buscado': dni_buscado,
        'cliente_encontrado': cliente is not None,
        'cliente': cliente
    }
    return render(request, 'venta/clientes/u_cliente.html', context)

@login_required
@permission_required('venta.delete_cliente', raise_exception=True)
def borrar_cliente(request):
    clientes_encontrados = []
    tipo_busqueda = 'dni'
    termino_busqueda = ''
    total_registros = 0

    if request.method == 'POST':
        if 'consultar' in request.POST:
            tipo_busqueda = request.POST.get('tipo_busqueda', 'dni')
            termino_busqueda = request.POST.get('termino_busqueda','').strip()

            if termino_busqueda:
                if tipo_busqueda == 'dni':
                    try:
                        cliente = Cliente.objects.get(id_cliente=termino_busqueda)
                        clientes_encontrados = [cliente]
                    except Cliente.DoesNotExist:
                        messages.error(request, 'No se encontró cliente con ese DNI')    
                elif tipo_busqueda == 'nombre':
                    clientes_encontrados = Cliente.objects.filter(
                        ape_nombre__icontains=termino_busqueda
                    ).order_by('id_cliente')

                    if not clientes_encontrados:
                        messages.error(request, 'No se encontraron clientes con ese nombre')

                total_registros = len(clientes_encontrados)
                if total_registros > 0:
                    messages.success(request, f'Se encontraron {total_registros} registro(s)')        
            else:
                messages.error(request, 'Ingrese un término de búsqueda')    

        elif 'eliminar' in request.POST:
            dni_eliminar = request.POST.get('dni_eliminar')
            if dni_eliminar:
                try:
                    cliente = Cliente.objects.get(id_cliente=dni_eliminar)
                    cliente.delete()
                    messages.success(request, f'Cliente con DNI {dni_eliminar} eliminado correctamente')

                    tipo_busqueda = request.POST.get('tipo_busqueda_actual', 'dni')
                    termino_busqueda = request.POST.get('termino_busqueda_actual','')

                    if termino_busqueda:
                        if tipo_busqueda == 'dni':
                            clientes_encontrados = []
                        elif tipo_busqueda == 'nombre':
                            clientes_encontrados = Cliente.objects.filter(
                                ape_nombre__icontains=termino_busqueda
                            ).order_by('id_cliente')

                        total_registros = len(clientes_encontrados)
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
    context = {
        'clientes_encontrados': clientes_encontrados,
        'tipo_busqueda': tipo_busqueda,
        'termino_busqueda': termino_busqueda,
        'total_registros': total_registros
    }
    return render(request, 'venta/clientes/borrar_cliente.html', context)

# ====================== VISTAS PARA PRODUCTOS ======================
@login_required
@permission_required('venta.view_producto', raise_exception=True)
def consulta_productos(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='grp_producto').exists() or
            request.user.has_perm('venta.view_producto')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')
    
    productos = Producto.objects.filter(estado=True).order_by('nom_prod')
    context = {
        'productos': productos,
        'titulo': 'Lista de Productos',
        'mensaje': 'Listado de productos activos'
    }
    return render(request, 'venta/productos/lista_productos.html', context)

@login_required
@permission_required('venta.add_producto', raise_exception=True)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoCreateForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.nom_prod}" registrado correctamente')
            return redirect('crear_producto')
    else:
        form = ProductoCreateForm()

    context = {
        'form': form,
        'titulo': 'Registrar Nuevo Producto'
    }
    return render(request, 'venta/productos/crear_producto.html', context)

@login_required
@permission_required('venta.change_producto', raise_exception=True)
def actualizar_producto(request):
    producto = None
    codigo_buscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            codigo_buscado = request.POST.get('codigo_busqueda')
            if codigo_buscado:
                try:
                    producto = Producto.objects.get(id_producto=codigo_buscado, estado=True)
                    form = ProductoUpdateForm(instance=producto)
                    messages.success(request, f'Producto con código {codigo_buscado} encontrado')
                except Producto.DoesNotExist:
                    messages.error(request, 'No se encontró producto con ese código o está inactivo')    
            else:
                messages.error(request, 'Por favor ingrese el código para buscar') 
        elif 'guardar' in request.POST:
            codigo_buscado = request.POST.get('codigo_busqueda') or request.POST.get('id_producto')
            if codigo_buscado:
                try:
                    producto = Producto.objects.get(id_producto=codigo_buscado)
                    form = ProductoUpdateForm(request.POST, instance=producto)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Producto actualizado correctamente')
                        producto.refresh_from_db()
                        form = ProductoUpdateForm(instance=producto)
                    else:
                        messages.error(request, 'Error en los datos del formulario')
                except Producto.DoesNotExist:
                    messages.error(request, 'Producto no encontrado')
            else:
                messages.error(request, 'No se puede identificar el producto para actualizar')
    context = {
        'form': form,
        'codigo_buscado': codigo_buscado,
        'producto_encontrado': producto is not None,
        'producto': producto
    }
    return render(request, 'venta/productos/u_producto.html', context)

@login_required
@permission_required('venta.delete_producto', raise_exception=True)
def borrar_producto(request):
    productos_encontrados = []
    tipo_busqueda = 'codigo'
    termino_busqueda = ''
    total_registros = 0

    if request.method == 'POST':
        if 'consultar' in request.POST:
            tipo_busqueda = request.POST.get('tipo_busqueda', 'codigo')
            termino_busqueda = request.POST.get('termino_busqueda','').strip()

            if termino_busqueda:
                if tipo_busqueda == 'codigo':
                    try:
                        producto = Producto.objects.get(id_producto=termino_busqueda, estado=True)
                        productos_encontrados = [producto]
                    except Producto.DoesNotExist:
                        messages.error(request, 'No se encontró producto con ese código o está inactivo')    
                elif tipo_busqueda == 'nombre':
                    productos_encontrados = Producto.objects.filter(
                        nom_prod__icontains=termino_busqueda,
                        estado=True
                    ).order_by('nom_prod')

                    if not productos_encontrados:
                        messages.error(request, 'No se encontraron productos con ese nombre')

                total_registros = len(productos_encontrados)
                if total_registros > 0:
                    messages.success(request, f'Se encontraron {total_registros} registro(s)')        
            else:
                messages.error(request, 'Ingrese un término de búsqueda')    

        elif 'eliminar' in request.POST:
            codigo_eliminar = request.POST.get('codigo_eliminar')
            if codigo_eliminar:
                try:
                    producto = Producto.objects.get(id_producto=codigo_eliminar)
                    producto.estado = False
                    producto.save()
                    messages.success(request, f'Producto "{producto.nom_prod}" desactivado correctamente')

                    tipo_busqueda = request.POST.get('tipo_busqueda_actual', 'codigo')
                    termino_busqueda = request.POST.get('termino_busqueda_actual','')

                    if termino_busqueda:
                        if tipo_busqueda == 'codigo':
                            productos_encontrados = []
                        elif tipo_busqueda == 'nombre':
                            productos_encontrados = Producto.objects.filter(
                                nom_prod__icontains=termino_busqueda,
                                estado=True
                            ).order_by('nom_prod')

                        total_registros = len(productos_encontrados)
                except Producto.DoesNotExist:
                    messages.error(request, 'Producto no encontrado')
    context = {
        'productos_encontrados': productos_encontrados,
        'tipo_busqueda': tipo_busqueda,
        'termino_busqueda': termino_busqueda,
        'total_registros': total_registros
    }
    return render(request, 'venta/productos/borrar_producto.html', context)

# ====================== VISTAS PARA VENTAS SIMPLES ======================
@login_required
@permission_required('venta.view_ventasimple', raise_exception=True)
def consulta_ventas_simples(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='grp_venta').exists() or
            request.user.has_perm('venta.view_ventasimple')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')

    ventas = VentaSimple.objects.all().order_by('-fecha_venta')
    total_ventas = sum(venta.total for venta in ventas if venta.total)
    total_igv = sum(venta.igv for venta in ventas if venta.igv)
    
    context = {
        'ventas': ventas,
        'total_ventas': total_ventas,
        'total_igv': total_igv,
        'titulo': 'Lista de Ventas Simples',
        'mensaje': 'Listado completo de ventas'
    }
    return render(request, 'venta/ventas_simples/lista_ventas_simples.html', context)
from decimal import Decimal

@login_required
@permission_required('venta.add_ventasimple', raise_exception=True)
@transaction.atomic
def crear_venta_simple(request):
    if request.method == 'POST':
        form = VentaSimpleForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            
            # Obtener el producto seleccionado
            producto = venta.producto
            
            # Establecer el precio unitario
            venta.precio_unitario = producto.precio
            
            # Calcular valores usando Decimal para el IGV
            venta.subtotal = venta.precio_unitario * Decimal(venta.cantidad)
            venta.igv = venta.subtotal * Decimal('0.18')  # Usar Decimal en lugar de float
            venta.total = venta.subtotal + venta.igv
            
            # Guardar la venta
            venta.save()
            
            # Actualizar el stock del producto
            producto.cantidad -= venta.cantidad
            producto.save()
            
            messages.success(request, 'Venta simple registrada correctamente')
            return redirect('lista_ventas_simples')
    else:
        form = VentaSimpleForm()

    context = {
        'form': form,
        'titulo': 'Registrar Venta Simple',
        'mensaje': 'Complete los datos de la venta'
    }
    return render(request, 'venta/ventas_simples/crear_venta_simple.html', context)

@login_required
@permission_required('venta.change_ventasimple', raise_exception=True)
@transaction.atomic
def actualizar_venta_simple(request, pk):
    venta = get_object_or_404(VentaSimple, pk=pk)
    cantidad_original = venta.cantidad

    if request.method == 'POST':
        form = VentaSimpleForm(request.POST, instance=venta)
        if form.is_valid():
            venta_actualizada = form.save(commit=False)
            
            # Recalcular valores usando Decimal
            venta_actualizada.subtotal = venta_actualizada.precio_unitario * Decimal(venta_actualizada.cantidad)
            venta_actualizada.igv = venta_actualizada.subtotal * Decimal('0.18')  # Usar Decimal
            venta_actualizada.total = venta_actualizada.subtotal + venta_actualizada.igv
            
            # Guardar la venta
            venta_actualizada.save()
            
            # Actualizar stock (solo si cambió la cantidad)
            if cantidad_original != venta_actualizada.cantidad:
                producto = venta_actualizada.producto
                producto.cantidad += (cantidad_original - venta_actualizada.cantidad)
                producto.save()
            
            messages.success(request, 'Venta simple actualizada correctamente')
            return redirect('lista_ventas_simples')
    else:
        form = VentaSimpleForm(instance=venta)

    context = {
        'form': form,
        'venta': venta,
        'titulo': 'Actualizar Venta Simple'
    }
    return render(request, 'venta/ventas_simples/actualizar_venta_simple.html', context)

@login_required
@permission_required('venta.delete_ventasimple', raise_exception=True)
@transaction.atomic
def eliminar_venta_simple(request, pk):
    venta = get_object_or_404(VentaSimple, pk=pk)
    
    if not venta.anulado:
        if request.method == 'POST':
            # Restaurar stock
            producto = venta.producto
            producto.cantidad += venta.cantidad
            producto.save()
            
            # Marcar como anulado
            venta.anulado = True
            venta.save()
            messages.success(request, 'Venta anulada correctamente')
            return redirect('lista_ventas_simples')
        
        return render(request, 'venta/ventas_simples/eliminar_venta_simple.html', {'venta': venta, 'titulo': 'Anular Venta'})
    else:
        messages.warning(request, 'Esta venta ya estaba anulada')
        return render(request, 'venta/ventas_simples/eliminar_venta_simple.html', {'venta': venta, 'titulo': 'Venta Anulada'})
from django.http import JsonResponse

def get_product_price(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return JsonResponse({'precio': str(producto.precio)})