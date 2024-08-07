from rest_framework import generics, status
from .models import User, Note, Comment, VersionControl
from .serializers import NoteSerializer 
from .serializers import CommentSerializer
from .serializers import ShareNoteSerializer
from .serializers import VersionControlSerializer
from .serializers import NoteArchiveSerializer
from .serializers import NoteUnArchiveSerializer
from .serializers import NoteRestoreSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from .permisions import SharedPermision
from django.utils import timezone
from .pagination import StandardResultsSetPagination
from .helper import create_note_version
from rest_framework import viewsets


class NoteViewSet(viewsets.ModelViewSet):

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ('title', 'text')
    search_fields = ('title', 'text')
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        notes_to_archive = Note.objects.filter(archive_date__lte=now, archive=False)
        notes_to_archive.update(archive=True)

        created_notes = Note.objects.filter(user=user, archive=False)
        shared_notes = Note.objects.filter(share_with=user, archive=False)

        return created_notes | shared_notes 

    def perform_create(self, serializer):
        note = serializer.save(user=self.request.user)
        create_note_version(self.request.user.id, serializer.validated_data, note.id)
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        now = timezone.now()

        if not instance.archive and instance.archive_date <= now:
            instance.archive = True
            instance.save()
            return Response({"detail": "Note is archived or expired"}, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if 200 <= response.status_code < 300:
            note_id = kwargs.get('pk')
            create_note_version(request.user.id, request.data, note_id)
        return response

    
class ArchiveNoteListView(generics.ListAPIView):

    serializer_class = NoteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ('title', 'text')
    search_fields = ('title', 'text')
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        created_notes = Note.objects.filter(user=user, archive=True)
        shared_notes = Note.objects.filter(share_with=user, archive=True)

        return created_notes | shared_notes 

class UnArchiveNoteView(generics.UpdateAPIView):

    queryset = Note.objects.all()
    serializer_class = NoteUnArchiveSerializer
    permission_classes = [IsAuthenticated, SharedPermision]

class ArchiveNoteView(generics.UpdateAPIView):

    queryset = Note.objects.all()
    serializer_class = NoteArchiveSerializer
    permission_classes = [IsAuthenticated, SharedPermision]


class ShareNoteView(generics.UpdateAPIView):

    queryset = Note.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ShareNoteSerializer
    lookup_field ='note_id'
   

class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
   

    def get_queryset(self):
        note_id = self.kwargs.get('note_pk')
        note = get_object_or_404(Note, id=note_id)
        comments = Comment.objects.filter(note=note)
        return comments

    def perform_create(self, serializer):
        note_id = self.kwargs.get('note_pk')
        note = get_object_or_404(Note, id=note_id)
        serializer.save(user=self.request.user, note=note)




class VersionControlListView(generics.ListAPIView):

    serializer_class = VersionControlSerializer  
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        note_id = self.kwargs['pk']
        history = VersionControl.objects.filter(note_id=note_id)
        return history
    

class NoteRestoreView(generics.UpdateAPIView):

    queryset = Note.objects.all()
    serializer_class = NoteRestoreSerializer  
    permission_classes = [IsAuthenticated]

