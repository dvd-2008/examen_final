from django.db import models
from django.core.validators import MinValueValidator

class Cliente(models.Model):
    id_cliente = models.CharField(
        max_length=8,
        primary_key=True,
        error_messages={'max_length': 'el texto debe tener 8 caracteres'},
        verbose_name="DNI"
    )
    ape_nombre = models.CharField(max_length=80, verbose_name="Apellidos y Nombres")
    fec_registro = models.DateField(verbose_name="Fecha de Registro")
    fec_sistema = models.DateTimeField(auto_now=True, verbose_name="Fecha de Sistema")

    def __str__(self):
        return f"{self.ape_nombre} (DNI: {self.id_cliente})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['ape_nombre']


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True, verbose_name="Código")
    nom_prod = models.CharField(max_length=50, verbose_name="Nombre del Producto")
    des_prod = models.TextField(max_length=500, verbose_name="Descripción", blank=True)
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario",
        validators=[MinValueValidator(0.01)]
    )
    cantidad = models.PositiveIntegerField(verbose_name="Stock", default=0)
    estado = models.BooleanField(default=True, verbose_name="Activo?")
    fec_vencimiento = models.DateField(
        verbose_name="Fecha de Vencimiento",
        null=True,
        blank=True
    )
    fec_reg = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    def __str__(self):
        return f"{self.nom_prod} - S/. {self.precio} (Stock: {self.cantidad})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nom_prod']


class VentaSimple(models.Model):
    cod_venta = models.AutoField(primary_key=True, verbose_name="Código de Venta")
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        related_name="ventas_simples"
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT,
        verbose_name="Producto",
        related_name="ventas_simples"
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        editable=False
    )
    igv = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="IGV (18%)"
    )
    total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        editable=False
    )
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Venta")
    anulado = models.BooleanField(default=False, verbose_name="Anulado?")

    def __str__(self):
        estado = "ANULADA" if self.anulado else "ACTIVA"
        return f"Venta Simple #{self.cod_venta} - {self.cliente.ape_nombre} - Total: S/. {self.total} ({estado})"

    class Meta:
        verbose_name = "Venta Simple"
        verbose_name_plural = "Ventas Simples"
        ordering = ['-fecha_venta']


class Venta(models.Model):
    cod_venta = models.AutoField(primary_key=True, verbose_name="Código de Venta")
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        related_name="ventas"
    )
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        editable=False
    )
    igv = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="IGV (18%)"
    )
    total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        editable=False
    )
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Venta")
    anulado = models.BooleanField(default=False, verbose_name="Anulado?")
    observaciones = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Observaciones"
    )

    def __str__(self):
        estado = "ANULADA" if self.anulado else "ACTIVA"
        return f"Venta #{self.cod_venta} - {self.cliente.ape_nombre} - Total: S/. {self.total} ({estado})"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']


class VentaDetalle(models.Model):
    cod_venta_detalle = models.AutoField(
        primary_key=True,
        verbose_name="Código de Detalle"
    )
    venta = models.ForeignKey(
        Venta, 
        on_delete=models.CASCADE,
        verbose_name="Venta",
        related_name="detalles"
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT,
        verbose_name="Producto",
        related_name="ventas_detalles"
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio Unitario"
    )
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        editable=False
    )
    anulado = models.BooleanField(default=False, verbose_name="Anulado?")

    def __str__(self):
        estado = "ANULADO" if self.anulado else "ACTIVO"
        return f"Detalle #{self.cod_venta_detalle} - {self.producto.nom_prod} x {self.cantidad} - Subtotal: S/. {self.subtotal} ({estado})"

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        ordering = ['cod_venta_detalle']