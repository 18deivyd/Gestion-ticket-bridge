from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# 1. El Administrador de Usuarios
class UsuarioManager(BaseUserManager):
    def create_user(self, usuario_seccion, clave=None, **extra_fields):
        if not usuario_seccion:
            raise ValueError('El usuario es obligatorio')
        
        extra_fields.setdefault('activo', 1)
        
        user = self.model(usuario_seccion=usuario_seccion, **extra_fields)
        user.set_password(clave)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, usuario_seccion, clave=None, **extra_fields):
        extra_fields.setdefault('rol', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(usuario_seccion, clave, **extra_fields)
    
# 2. Modelo de Usuario que apunta a la tabla existente
class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES_CHOICES = [
        ('cliente', 'Cliente'),
        ('agente', 'Agente de Soporte'),
        ('admin', 'Administrador'),
        ('superUser', 'Super Usuario')
    ]
    
    GRUPO_CHOICES = [
        ('tecnologia', 'Tecnología'),
        ('sistema', 'Sistema'),
        ('davan_eleconstruc', 'Davan y Eleconstruc'),
        ('somos_deporte', 'Somos Deporte'),
        ('lompanes_alombarda', 'Lompanes y Alombarda'),
        ('gestion_humana', 'Gestión Humana'),
        ('proconsul_ipconstruc', 'Proconsul y Ipconstruc'),
        ('grupo_loscar', 'Grupo LosCar'),
        ('sata', 'SATA'),
        ('legal', 'Legal'),
        ('contabilidad', 'Contabilidad'),
        ('salud_movil', 'Salud Móvil'),
        ('nuevo_horizonte', 'Nuevo Horizonte'),
    ]
    
    # Campos existentes
    id_usuario = models.AutoField(primary_key=True)
    usuario_seccion = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=255, db_column='clave')    
    nombre = models.CharField(max_length=200, null=True, blank=True)
    activo = models.IntegerField(default=1, null=True, blank=True)
    
    # Nuevos campos
    correo = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES_CHOICES, default='cliente')
    grupo = models.CharField(max_length=30, choices=GRUPO_CHOICES, default='tecnologia')
    
    # Campos Obligatorios
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'usuario_seccion'
    REQUIRED_FIELDS = ['nombre']
    
    class Meta:
        db_table = 'usuario'
        managed = True

    def __str__(self):
        return f'{self.nombre or self.usuario_seccion} ({self.rol})'
  
# 3. Modelo de Ticket  
class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('abierto', 'Abierto'),
        ('en_progreso', 'En Progreso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    TIPO_CHOICES = [
        ('incidencia', 'Incidencia'),
        ('requerimiento', 'Requerimiento'),
    ]
    
    GRUPO_CHOICES = [
        ('tecnologia', 'Tecnología'),
        ('sistema', 'Sistema'),
        ('davan_eleconstruc', 'Davan y Eleconstruc'),
        ('somos_deporte', 'Somos Deporte'),
        ('lompanes_alombarda', 'Lompanes y Alombarda'),
        ('gestion_humana', 'Gestión Humana'),
        ('proconsul_ipconstruc', 'Proconsul y Ipconstruc'),
        ('grupo_loscar', 'Grupo LosCar'),
        ('sata', 'SATA'),
        ('legal', 'Legal'),
        ('contabilidad', 'Contabilidad'),
        ('salud_movil', 'Salud Móvil'),
        ('nuevo_horizonte', 'Nuevo Horizonte'),
        ]
    
    id_ticket = models.AutoField(primary_key=True)
    message_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    para = models.EmailField(max_length=254, null=True, blank=True)
    asunto = models.CharField(max_length=255)
    descripcion = models.TextField()
    imagen = models.ImageField(null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='incidencia')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierto')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    grupo = models.CharField(max_length=30, choices=GRUPO_CHOICES, default='tecnologia')
    
    # Relaciones de clave foránea
    creado_por = models.ForeignKey(
        Usuario, 
        on_delete = models.CASCADE,
        related_name='tickets_creados'
    )
    
    # Asignado a (Agente)
    asignado_a = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados'
    )
    
    # Colaborador a (Agente)
    colaborador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_colaborados'
    )
    
    en_papelera = models.BooleanField(default=False)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ticket'
        ordering = ['-fecha_creacion']
        
    def __str__(self):
        return f'Ticket #{self.id_ticket}: {self.asunto} ({self.estado})'
    
# 4. Modelo Respuesta
class RespuestaTicket(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='respuestas')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    contenido = models.TextField()
    es_nota_interna = models.BooleanField(default=False)
    mencionados = models.ManyToManyField(Usuario, blank=True, related_name='menciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuesta_ticket'
        ordering = ['fecha_creacion']
        
    def __str__(self):
        return f'Respuesta #{self.id_respuesta} en Ticket #{self.ticket.id_ticket}'
    
# 5. Modelo de  Imagenes
class TicketAdjunto(models.Model):
    id_adjunto =  models.AutoField(primary_key=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='ticket_adjuntos/')
    content_id = models.CharField(max_length=255, null=True, blank=True)
    fecha_subida = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'ticket_adjunto'
    
    def __str__(self):
        return f'Adjunto #{self.id_adjunto} en Ticket #{self.ticket.id_ticket}'