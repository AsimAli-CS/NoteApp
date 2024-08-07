from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet
from .views import CommentViewSet
from .views import ArchiveNoteListView
from .views import VersionControlListView
from .views import NoteRestoreView
from .views import ArchiveNoteView
from .views import ShareNoteView
from .views import UnArchiveNoteView

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'notes/(?P<note_pk>\d+)/comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('nnotes/aarchivelist/', ArchiveNoteListView.as_view(), name='archive-list'),
    path('notes/<int:pk>/archive/', ArchiveNoteView.as_view(), name='archive-note'),
    path('notes/archive/<int:pk>/', ArchiveNoteView.as_view(), name='archive-note-by-id'),
    path('notes/archive/<int:pk>/unarchive/', UnArchiveNoteView.as_view(), name='unarchive-note'),
    path('note/<int:note_id>/share/', ShareNoteView.as_view(), name='share-note'),
    path('notes/<int:pk>/history/', VersionControlListView.as_view(), name='history'),
    path('notes/<int:pk>/history/original/', NoteRestoreView.as_view(), name='original'),
]
