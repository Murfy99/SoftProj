import numpy as np
from scipy.sparse.linalg import svds
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Movie, Rating
from .serializers import MovieSerializer, RatingSerializer, UserSerializer

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['GET'])
def user_ratings(request, user_id):
    user = get_object_or_404(User, id=user_id)
    ratings = Rating.objects.filter(user=user)
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def movie_details(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

@api_view(['POST'])
def add_rating(request):
    serializer = RatingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def recommend_movies(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"error": "User ID not provided"}, status=400)

    # Get all ratings
    ratings = Rating.objects.all().values()
    if not ratings:
        return Response({"error": "No ratings available"}, status=404)

    # Create a user-item ratings matrix
    user_ids = list(set([rating['user_id'] for rating in ratings]))
    movie_ids = list(set([rating['movie_id'] for rating in ratings]))
    user_idx = {user_id: idx for idx, user_id in enumerate(user_ids)}
    movie_idx = {movie_id: idx for idx, movie_id in enumerate(movie_ids)}

    ratings_matrix = np.zeros((len(user_ids), len(movie_ids)))
    for rating in ratings:
        user_index = user_idx[rating['user_id']]
        movie_index = movie_idx[rating['movie_id']]
        ratings_matrix[user_index, movie_index] = rating['rating']

    # Apply collaborative filtering using Singular Value Decomposition (SVD)
    u, s, vt = svds(ratings_matrix, k=min(len(user_ids), len(movie_ids)) - 1)
    s_diag_matrix = np.diag(s)
    predicted_ratings = np.dot(np.dot(u, s_diag_matrix), vt)

    # Recommend movies that the user hasn't rated yet, sorted by predicted rating
    user_row = predicted_ratings[user_idx[int(user_id)]]
    unrated_movies_indices = [i for i in range(len(user_row)) if ratings_matrix[user_idx[int(user_id)], i] == 0]
    recommended_movie_indices = sorted(unrated_movies_indices, key=lambda x: -user_row[x])[:10]
    recommended_movie_ids = [movie_ids[i] for i in recommended_movie_indices]
    recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)
    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def top_rated_movies(request):
    top_movies = Movie.objects.annotate(average_rating=Avg('rating__rating')).order_by('-average_rating')[:10]
    serializer = MovieSerializer(top_movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def movies_by_genre(request, genre):
    genre_movies = Movie.objects.filter(genre__iexact=genre)
    if not genre_movies:
        return Response({"error": "No movies found for this genre"}, status=404)
    serializer = MovieSerializer(genre_movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data)
