from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse
from decimal import InvalidOperation, Decimal, ROUND_DOWN

from auctions.forms import *

from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter()
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

def listing_detail(request, id):
    return render(request, "auctions/listing.html", {
        "listing": Listing.objects.get(id=id),
        "user": User.objects.get(id=request.user.id),
        "form": BiddingForm(),
        "comments": Comment.objects.filter(listing__id=id).order_by("-timestamp"),
        "comment_form": CommentForm()
        })

@login_required
def toggle_watchlist(request, id):
    if request.method == "POST":
        listing = Listing.objects.get(id=id)
        user = request.user
        
        if listing not in user.watchlist.all():
            user.watchlist.add(listing)
            print(user.watchlist.all())

        else:
            user.watchlist.remove(listing)
            print(user.watchlist.all())

        return redirect("listing_detail", id=listing.id)
    
    else:
        return HttpResponseNotAllowed(["POST"])            
        
@login_required
def place_bid(request, id):
    if request.method == "POST":
        form = BiddingForm(request.POST)
        try:
            listing = Listing.objects.get(id=id)
        except InvalidOperation:
            return HttpResponse("Invalid value", status=500)
        
        if not listing.is_open:
            messages.error(request, "You cannot place a bid on a closed listing.")
            return redirect("listing_detail", id=listing.id)
        
        if listing.owner == request.user:
            messages.error(request, "You cannot place a bid on your own listing.")
            return redirect("listing_detail", id=listing.id)
        
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            amount = Decimal(amount).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
            if (listing.current_bid == 0 and amount >= listing.starting_bid) or (listing.current_bid != 0 and amount > listing.current_bid):
                bid = form.save(commit=False)
                bid.listing = listing
                bid.user = request.user
                listing.current_bid = amount
                bid.save()
                
                listing.save()
                return redirect("listing_detail", id=listing.id)
            else:
                messages.error(request, "Your bid must be higher than the current bid.")
        else:
            messages.error(request, "Invalid form submission.")
        
        return redirect("listing_detail", id=listing.id)

@login_required
def close_listing(request, id):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(id=id)
        except Listing.DoesNotExist:
            return HttpResponse("Listing not found", status=404)
        
        if request.user != listing.owner:
            return HttpResponse("You are not allowed to close this listing.", status=403)

        if listing.current_bid == 0:
            messages.error(request, "Cannot close a listing without bids.")
            return redirect("listing_detail", id=listing.id)

        listing.is_open = False
        listing.save()
        
        return redirect("listing_detail", id=listing.id)
    else:
        return HttpResponseNotAllowed(["POST"])
    
@login_required
def add_comment(request, id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        try:
            listing = Listing.objects.get(id=id)
        except Listing.DoesNotExist:
            return HttpResponse("Listing not found", status=404)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.author = request.user
            comment.save()
            return redirect("listing_detail", id=listing.id)
        else:
            messages.error(request, "Invalid comment submission.")
            return redirect("listing_detail", id=listing.id)
    return HttpResponseNotAllowed(["POST"])

@login_required
def watchlist(request):
    user = request.user
    watchlist_items = user.watchlist.all()
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist_items,
        "user": user
    })
    
def categories(request):
    categories = Listing.CATEGORY_CHOICES
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
    
def category_listings(request, category):
    listings = Listing.objects.filter(category=category, is_open=True)
    
    if not listings:
        messages.info(request, f"No listings found in the '{category}' category.")
    return render(request, "auctions/category_listings.html", {
        "listings": listings,
        "category": category
    })