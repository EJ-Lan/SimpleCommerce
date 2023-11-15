from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watched_by")

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=64, blank=True)
    image_url = models.URLField(max_length=200, blank=True)
    start_bid = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_listing")

    def __str__(self):
       return f"Title: {self.title}, Description: {self.description}, Start Bid: {self.start_bid}"
    
class Bid(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Owner: {self.owner.username}, Listing: {self.listing.title}, Bid: {self.bid_amount}"
    

class Comments(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField()

    def __str__(self):
        return f"User: {self.owner.username}, Comment: {self.comment_text}"