from django.shortcuts import get_object_or_404
from .models import Note
from .serializers import VersionControlSerializer

def create_note_version(id, data, note):

    version_data = {
        'title': data.get('title', ''), 
        'text': data.get('text', ''),
        'user': id,
        'note': note
    }
   
    serializer = VersionControlSerializer(data=version_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
