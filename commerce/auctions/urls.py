from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:id>", views.listing , name="listing"),
    path("listing/<int:id>/to_watchlist", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:id>/bid", views.place_bid, name="place_bid"),
    path("listing/<int:id>/close", views.close_listing, name="close_listing"),
    path("listing/<int:id>/add_comment", views.add_comment, name="add_comment")
]
