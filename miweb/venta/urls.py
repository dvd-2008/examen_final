from django.urls import path
from venta.views import (
    user_login,
    home,
    user_logout,
    consulta_clientes,
    crear_cliente,
    actualizar_cliente,
    borrar_cliente,
    consulta_productos,
    crear_producto,
    actualizar_producto,
    borrar_producto,
    consulta_ventas_simples,
    crear_venta_simple,
    actualizar_venta_simple,
    eliminar_venta_simple,
)

urlpatterns = [
    # Autenticación
    path('', user_login, name='login'),
    path('home/', home, name='home'),
    path('logout/', user_logout, name='logout'),
    
    # Clientes
    path('clientes/', consulta_clientes, name='lista_clientes'),
    path('clientes/crear/', crear_cliente, name='crear_cliente'),
    path('clientes/actualizar/', actualizar_cliente, name='actualizar_cliente'),
    path('clientes/borrar/', borrar_cliente, name='borrar_cliente'),
    
    # Productos
    path('productos/', consulta_productos, name='lista_productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),
    path('productos/actualizar/', actualizar_producto, name='actualizar_producto'),
    path('productos/borrar/', borrar_producto, name='borrar_producto'),
    
    # Ventas Simples
    path('ventas-simples/', consulta_ventas_simples, name='lista_ventas_simples'),
    path('ventas-simples/crear/', crear_venta_simple, name='crear_venta_simple'),
    path('ventas-simples/editar/<int:pk>/', actualizar_venta_simple, name='actualizar_venta_simple'),
    path('ventas-simples/anular/<int:pk>/', eliminar_venta_simple, name='eliminar_venta_simple'),
]