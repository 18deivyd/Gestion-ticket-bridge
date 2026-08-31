from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Ticket, Usuario, RespuestaTicket, TicketAdjunto
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UsuarioMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=Usuario
        fields=['id_usuario','usuario_seccion','nombre', 'correo', 'rol']
        
class RespuestaTicketSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioMiniSerializer(source='usuario', read_only=True)
    
    class Meta:
            model = RespuestaTicket
            fields = ['id_respuesta', 'ticket', 'usuario', 'usuario_detalle', 'contenido', 'es_nota_interna', 'mencionados', 'fecha_creacion']
            
class TicketAdjuntoSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAdjunto
        fields = ['id_adjunto', 'archivo', 'archivo_url', 'content_id', 'fecha_subida']

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        if obj.archivo:
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return f'http://127.0.0.1:8000{obj.archivo.url}'
        return None
        
class TicketSerializer(serializers.ModelSerializer):
    creado_por_detalle = UsuarioMiniSerializer(source='creado_por', read_only=True)
    asignado_a_detalle = UsuarioMiniSerializer(source='asignado_a', read_only=True)
    colaborador_detalle = UsuarioMiniSerializer(source='colaborador', read_only=True)
    respuestas = RespuestaTicketSerializer(many= True, read_only=True)
    adjuntos = TicketAdjuntoSerializer(many=True, read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True)
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = '__all__'
        
        extra_kwargs={
            'creado_por': {'required':False, 'allow_null':True},
            'asignado_a': {'required':False, 'allow_null':True},
            'colaborador': {'required':False, 'allow_null':True},
            'grupo': {'required':False, 'allow_null':True, 'allow_blank':True},
            'fecha_eliminacion': {'required':False, 'allow_null':True},
            'en_papelera': {'required':False}
        }
    
    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen:
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return f'http://127.0.0.1:8000{obj.imagen.url}'
        return None
        
class TicketListSerializer(serializers.ModelSerializer):
    creado_por_detalle = UsuarioMiniSerializer(source='creado_por', read_only=True)
    asignado_a_detalle = UsuarioMiniSerializer(source='asignado_a', read_only=True)
    colaborador_detalle = UsuarioMiniSerializer(source='colaborador', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id_ticket', 'asunto', 'descripcion', 'estado', 'prioridad', 'grupo',
            'creado_por_detalle', 'asignado_a', 'asignado_a_detalle', 
            'colaborador', 'colaborador_detalle', 'en_papelera', 
            'fecha_eliminacion', 'fecha_creacion'
        ]

class RegistroSerializer(serializers.ModelSerializer):
    correo = serializers.EmailField(required=True)
    nombre = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    grupo = serializers.CharField(required=False, default='tecnologia')
    
    class Meta:
        model=Usuario
        fields = ['id_usuario', 'nombre', 'correo', 'usuario_seccion', 'password', 'rol', 'grupo']
        extra_kwargs = {
            'rol': {'required': False, 'default': 'cliente'},
            'usuario_seccion': {'required': False, 'allow_null': True, 'allow_blank': True}
        }
    
    def validate_email(self, value):
        return value
    
    def create(self, validated_data):
        correo = validated_data.get('correo')
        raw_password = validated_data.get('password')
        nuevo_grupo = validated_data.get('grupo', 'tecnologia')
        nombre = validated_data.get('nombre')
        
        usuario_existente = Usuario.objects.filter(correo=correo).first()
        
        if usuario_existente:
            if usuario_existente.rol == 'cliente':
                usuario_existente.nombre = nombre
                usuario_existente.grupo = nuevo_grupo
                usuario_existente.rol = 'admin'
                usuario_existente.is_staff = True
                usuario_existente.set_password(raw_password)
                usuario_existente.save()
                return usuario_existente
            else:
                raise serializers.ValidationError({
                    'correo': 'Cuenta existente. Este correo ya pertenece a una cuenta administrativa o de agente.'
                })
        
        usuario_seccion = validated_data.get('usuario_seccion') or correo
        validated_data['usuario_seccion'] = usuario_seccion
        validated_data['password'] = make_password(raw_password)
        validated_data['rol'] = validated_data.get('rol', 'cliente')
        validated_data['grupo'] = nuevo_grupo
        
        return super().create(validated_data)
    
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'correo', 'usuario_seccion', 'rol']
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['id_usuario'] = self.user.id_usuario
        return data