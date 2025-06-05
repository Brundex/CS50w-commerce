from django import forms
from auctions.models import *

class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ["owner", "current_bid", "is_open"]
        
class BiddingForm(forms.ModelForm):
    class Meta:
        model = Bid
        exclude = ["user", "listing"]