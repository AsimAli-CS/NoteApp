from rest_framework.permissions import BasePermission
from .models import Note

class SharedPermision(BasePermission):
    def has_object_permission(self, request, view, obj):

        if obj.user == request.user:
            return True

        if obj.share_with.filter(id=request.user.id).exists() and not obj.archive:
            return True
        
        return False
       