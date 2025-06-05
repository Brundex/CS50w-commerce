from django.contrib.auth.models import AbstractUser
from django.db import models

# AGREGAR FIELDS Y TYPES

class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watching")
class Listing(models.Model):
    CATEGORY_CHOICES = {
        "Motors": "Motors",
        "Electronics": "Electronics",
        "Clothing": "Clothing & Accesories",
        "Furniture": "Furniture",
        "Sports": "Sporting Goods",
        "Other": "Other"        
    }
    # Core Details
    owner = models.ForeignKey("User", on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=64)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    img_url = models.URLField(blank=True, null=True, verbose_name="image URL")
    
    # Bidding
    starting_bid = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="starting bid")
    current_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    
    # State
    is_open = models.BooleanField(default=True)
    
    def highest_bidder(self):
        return Bid.objects.get(listing=self, amount=self.current_bid).user if self.current_bid > 0 else None
    
    
    

class Bid(models.Model):
    # References
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE)
    
    # Bid values
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    
    

class Comment(models.Model):
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE)
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
