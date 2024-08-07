from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class UserAuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def get_authentication_token(self):
        response = self.client.post('/users/api/token/', {
            'username': 'testuser',
            'password': 'testpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']
    
    def get_invalid_authentication_token(self):
        response = self.client.post('/users/api/token/', {
            'username': 'invaliduser',
            'password': 'invalidpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        return ''

    def authenticate_user(self):
        token = self.get_authentication_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_authenticated_request(self):
        self.authenticate_user()
        
        response = self.client.get('/api/notes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_request_with_invalid_token(self):
        invalid_token = self.get_invalid_authentication_token()
        print(invalid_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + invalid_token)
        
        response = self.client.get('/api/notes/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_request_without_token(self):
        response = self.client.get('/api/notes/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
