from rest_framework import serializers
from authentication.models import Language
from superadmin.models import Resources
from users.models import ChatMessage, ChatRoom
import os

class ResourceSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    class Meta:
        model = Resources
        fields = ['uuid', 'name', 'type', 'file', 'link', 'thumbnail', 'created_at', 'updated_at']
        
     
    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url)
        return None        
    
    def get_file_name(self, obj):
        if obj.file:
            return os.path.basename(obj.file.name)
        return None
    

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['uuid', 'code', 'name']
        
        


class RoomsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = ['uuid', 'name', 'user', 'is_saved', 'type', 'created_at', 'updated_at']
        
    def get_user(self, obj):
        return str(obj.user.uuid) if obj.user else ''
    

class RoomMessagesSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['uuid', 'user', 'room','room_name', 'prompt', 'response', 'created_at', 'updated_at']
        
    def get_user(self, obj):
        return str(obj.user.uuid) if obj.user else ''
    
    def get_room(self, obj):
        return str(obj.room.uuid) if obj.room else ''
    
    def get_room_name(self, obj):
        return str(obj.room.name) if obj.room else ''