from django.contrib import admin
from .models import Note, Comment, VersionControl
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


admin.site.unregister(User)


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email','is_staff')
    search_fields = ('email',)


class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'archive', 'date_created', 'date_updated')
    search_fields = ('title', 'text')
    list_filter = ('date_created', 'date_updated')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'user', 'text', 'date_created')
    search_fields = ('text',)
    list_filter = ('date_created', 'user')


class VersionControlAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'title', 'text', 'date_created')
    search_fields = ('title', 'text')
    list_filter = ('date_created', 'user')

admin.site.register(User, UserAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(VersionControl, VersionControlAdmin)
