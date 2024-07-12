from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MovieViewSet, RatingViewSet, UserViewSet, user_ratings, movie_details, 
    add_rating, recommend_movies, top_rated_movies, movies_by_genre, user_profile
)

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user_ratings/<int:user_id>/', user_ratings, name='user-ratings'),
    path('movie_details/<int:movie_id>/', movie_details, name='movie-details'),
    path('add_rating/', add_rating, name='add-rating'),
    path('recommend/', recommend_movies, name='recommend-movies'),
    path('top_rated/', top_rated_movies, name='top-rated-movies'),
    path('movies_by_genre/<str:genre>/', movies_by_genre, name='movies-by-genre'),
    path('user_profile/<int:user_id>/', user_profile, name='user-profile'),
]
