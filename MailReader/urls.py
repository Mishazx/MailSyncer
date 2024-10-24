from django.urls import path

from .consumers import EmailConsumer
from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('login/', index, name='login'),
]

websocket_urlpatterns = [
    path('ws/emails/', EmailConsumer.as_asgi()),
]
