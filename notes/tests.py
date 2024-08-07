from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Note
from django.utils import timezone
from datetime import timedelta

class NoteTest(APITestCase):
    URL = '/api/notes/'

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        
        self.note1 = Note.objects.create(
            title="Note 1",
            text="Text for note 1",
            user=self.user1,
            archive_date=timezone.now() + timedelta(days=7)
        )

        self.note2 = Note.objects.create(
            title="Note 2",
            text="Text for note 2",
            user=self.user1,
            archive_date=timezone.now() - timedelta(days=8)  # This note should be archived
        )

        self.note3 = Note.objects.create(
            title="Note 3",
            text="Text for note 3",
            user=self.user1,
            archive_date=timezone.now() + timedelta(days=7)
        )
        
        self.note2.share_with.add(self.user2)

    def get_authentication_token(self, username, password):
        response = self.client.post('/users/api/token/', {
            'username': username,
            'password': password
        }, format='json')
        
        if response.status_code == status.HTTP_200_OK:
            return response.data['access']
        else:
            return ''
        
    def authenticate_user(self, username, password):
        token = self.get_authentication_token(username, password)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_create_note_authenticated(self):
        self.authenticate_user('user1', 'password1')
        
        response = self.client.post(self.URL, {
            'title': 'New Note',
            'text': 'This is a new note',
            'archive_date': timezone.now() + timedelta(days=7)
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_note_authenticated(self):
        self.authenticate_user('user1', 'password1')
        
        response = self.client.get(f'{self.URL}{self.note1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User does not have access to that note
        response_with_wrongId = self.client.get(f'{self.URL}10/')
        self.assertEqual(response_with_wrongId.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_note_authenticated(self):
        self.authenticate_user('user1', 'password1')
        
        response = self.client.put(f'{self.URL}{self.note1.id}/', {
            'title': 'Updated Note Title',
            'text': 'Updated text for note 1',
            'archive_date': timezone.now() + timedelta(days=7)
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Updated Note Title')

        # Invalid note ID
        response1 = self.client.put(f'{self.URL}8/', {
            'title': 'Updated Note Title',
            'text': 'Updated text for note 1',
            'archive_date': timezone.now() + timedelta(days=7)
        }, format='json')
        
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_note_authenticated(self):
        self.authenticate_user('user1', 'password1')
        
        response = self.client.delete(f'{self.URL}{self.note3.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Invalid note ID
        response1 = self.client.delete(f'{self.URL}7/')

        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)

    def test_note_list_authenticated(self):
        self.authenticate_user('user1', 'password1')
        
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_note_list_unauthenticated(self):
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_note_unauthorized(self):
        self.authenticate_user('user2', 'password2')
        
        response = self.client.delete(f'{self.URL}{self.note3.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Should be forbidden as user2 does not own note3

        # Invalid note ID
        response1 = self.client.delete(f'{self.URL}7/')

        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_note_unauthenticated(self):
        response = self.client.get(f'{self.URL}{self.note1.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # User does not have access to that note
        response_with_wrongId = self.client.get(f'{self.URL}10/')
        self.assertEqual(response_with_wrongId.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_archive(self):
        self.authenticate_user('user1', 'password1')

        self.note4 = Note.objects.create(
            title="Note 4",
            text="Text for note 4",
            user=self.user1,
            archive_date=timezone.now() - timedelta(days=10)
        )

        response = self.client.get(f'{self.URL}{self.note4.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.note4.refresh_from_db()

        self.assertTrue(self.note4.archive)
