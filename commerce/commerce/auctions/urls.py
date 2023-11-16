from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing_view/<int:pk>", views.listing_view, name='listing_view'),
    path("watchlist", views.watchlist, name="watchlist"),
    path("toggle_watchlist/<int:pk>", views.toggle_watchlist, name="toggle_watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category_listings, name="category_listings"),
    path("submit_bid/<int:pk>", views.submit_bid, name="submit_bid"),
]
