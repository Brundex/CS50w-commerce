from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponseNotAllowed

from ..models import Listing

@login_required
def watchlist(request):
    user = request.user
    watchlist_items = user.watchlist.all()
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist_items,
        "user": user
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