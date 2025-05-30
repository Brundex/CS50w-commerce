from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from auctions.forms import *

from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_open=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
 
@login_required   
def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            print(f"Listing created successfully by {request.user}: {listing}")
            return redirect("index") #TODO: This should render the listing's page.
        
        else:
            return render(request, "auctions/new_listing.html", {
                "form": NewListingForm()
            })  
        
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })

def listing(request, id):
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(id=id)
    })
    
def toggle_watchlist(request, id):
    # Si 
    return

def place_bid(request, id):
    # Tiene que ser mayor a current_bid. SI no hay bids, tiene que ser mayor o igual a starting_bid
    # Actualiza current_bid
    # El owner no puede pujar
    return

def close_listing(request, id):
    # Solo puede ser hecho por el owner
    # Tiene que haber al menos un bid. Busco el User Id que puso el current_bid
    # is_open cambia a False
    return

def add_comment(request, id):
    return   