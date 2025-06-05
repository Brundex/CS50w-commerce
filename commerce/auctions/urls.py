from django.urls import path
from .views import (
    login_view, logout_view, register, index, new_listing, listing_detail, close_listing, place_bid,
    toggle_watchlist, watchlist, add_comment, categories, category_listings
)

urlpatterns = [
    path("", index, name="index"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),
    path("new_listing", new_listing, name="new_listing"),
    path("listing/<int:id>", listing_detail , name="listing_detail"),
    path("listing/<int:id>/to_watchlist", toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:id>/bid", place_bid, name="place_bid"),
    path("listing/<int:id>/close", close_listing, name="close_listing"),
    path("listing/<int:id>/add_comment", add_comment, name="add_comment"),
    path("watchlist", watchlist, name="watchlist"),
    path("categories", categories, name="categories"),
    path("categories/<str:category>", category_listings, name="category_listings")
]
