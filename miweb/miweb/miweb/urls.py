
from django.contrib import admin
from django.urls import path, include  # Coma correctamente colocada
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('venta.urls')),
    path('', RedirectView.as_view(url='venta/q_cliente/')),  # Redirige la raíz
    path('venta/', include('venta.urls')),
]
