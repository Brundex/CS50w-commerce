from django.shortcuts import render
from django.contrib import messages

from ..models import Listing

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