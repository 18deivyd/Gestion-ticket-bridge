from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, obtener_usuarios, registrar_usuario, verificar_correo_imap, sync_and_list_tickets, responder_ticket, sync_imap_background

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns=[
    path('', include(router.urls)),
    path('register/', registrar_usuario, name='registrar_usuario'),
    path('verificar-imap/', verificar_correo_imap, name='verificar_imap'),
    path('user-tickets/', sync_and_list_tickets, name='sync_user_tickets'),
    path('user-sync-imap/', sync_imap_background, name='sync-imap'),
    path('usuarios/', obtener_usuarios, name='obtener_usuarios'),
    path('tickets/<int:pk>/responder/', responder_ticket, name='responder_ticket'),
]