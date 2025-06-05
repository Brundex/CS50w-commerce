from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib import messages
from decimal import Decimal, ROUND_DOWN, InvalidOperation

from ..models import Listing, Comment, User
from ..forms import NewListingForm, BiddingForm, CommentForm



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter()
    })
 
def listing_detail(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except Listing.DoesNotExist:
        return HttpResponse("Listing not found", status=404)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "user": User.objects.get(id=request.user.id),
        "form": BiddingForm(),
        "comments": Comment.objects.filter(listing__id=id).order_by("-timestamp"),
        "comment_form": CommentForm()
        })

@login_required   
def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            print(f"Listing created successfully by {request.user}: {listing}")
            return redirect("listing_detail", id=listing.id)
        
        else:
            return render(request, "auctions/new_listing.html", {
                "form": NewListingForm()
            })  
        
    return render(request, "auctions/new_listing.html", {
        "form": NewListingForm()
    })

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
