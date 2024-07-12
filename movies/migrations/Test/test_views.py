from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ...models import Movie, Rating

class MovieTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.movie = Movie.objects.create(title='Test Movie', description='A test movie', genre='Action', release_date='2020-01-01')
        self.rating = Rating.objects.create(movie=self.movie, user=self.user, rating=5)

    def test_list_movies(self):
        url = reverse('movie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_rating(self):
        url = reverse('add-rating')
        data = {'user': self.user.id, 'movie': self.movie.id, 'rating': 4}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_recommend_movies(self):
        url = reverse('recommend-movies')
        response = self.client.get(url, {'user_id': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_top_rated_movies(self):
        url = reverse('top-rated-movies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
