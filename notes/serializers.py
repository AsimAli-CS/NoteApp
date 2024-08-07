from rest_framework import serializers
from .models import Note, Comment, VersionControl
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) 
    note = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['text', 'date_created', 'note', 'user']

class NoteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ['title', 'text', 'date_created', 'user', 'archive']

class VersionControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionControl
        fields = ['id', 'title', 'text', 'user', 'note']

class NoteArchiveSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Note
        fields = ['title', 'text', 'date_created', 'user', 'archive']
        read_only_fields = [field.name for field in Note._meta.fields]

    def update(self, instance, validated_data):
        if instance.archive == False:
            instance.archive = True

        instance.save()
        return instance
    

class NoteUnArchiveSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Note
        fields = ['title', 'text', 'date_created', 'user', 'archive']
        read_only_fields = [field.name for field in Note._meta.fields]

    def update(self, instance, validated_data):
        if instance.archive == True:
            instance.archive = False

        instance.save()
        return instance
    

class ShareNoteSerializer(serializers.ModelSerializer):
    shared_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Note
        fields = ['title', 'text', 'date_created', 'user', 'archive']

    def update(self, instance, validated_data):
        user_id = validated_data.get('shared_user_id')
        user = get_object_or_404(User, id=user_id)

        if instance.user.id == user_id:
            raise serializers.ValidationError("Cannot share the note with itself.")

        instance.share_with.add(user)
        instance.save()
        return instance
    

class NoteRestoreSerializer(serializers.ModelSerializer):
    note_history_version = serializers.IntegerField(write_only=True)
    class Meta:
        model = Note
        fields = ['title', 'text', 'date_created', 'user', 'archive']
        read_only_fields = [field.name for field in Note._meta.fields]

    def update(self, instance, validated_data):
        note_history_version = validated_data.get('note_history_version')
        version = VersionControl.objects.get(id=note_history_version)
        
        instance.title = version.title
        instance.text = version.text
        instance.save()

        return instance
