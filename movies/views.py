import numpy as np
from .models import Movie, Rating
from .serializers import MovieSerializer, RatingSerializer
from scipy.sparse.linalg import svds
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Movie, Rating
from .serializers import MovieSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer



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
