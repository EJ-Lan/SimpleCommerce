from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Bid, Listing, User

class CreateListingForm(forms.Form):
    title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    starting_bid = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    category = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    image_url = forms.URLField(max_length=200,required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))

class CreateBidForm(forms.Form):
    bid_amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class CreateCommentForm(forms.Form):
    comment_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))


def index(request):
    all_listings = Listing.objects.all()

    return render(request, "auctions/index.html", {
        "listings": all_listings
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

@login_required
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
def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            new_listing = Listing(
                owner = request.user,
                title = form.cleaned_data['title'],
                description = form.cleaned_data['content'],
                start_bid = form.cleaned_data['starting_bid'],
                current_bid = form.cleaned_data['starting_bid'],
                category = form.cleaned_data['category'],
                image_url = form.cleaned_data['image_url']
            )

            new_listing.save()
            messages.success(request, 'Your listing has been created successfully!')
            return HttpResponseRedirect(reverse("index"))
    else:
        form = CreateListingForm()

    return render(request, "auctions/create.html", {
        "create_form": form
    })    

def listing_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = listing in request.user.watchlist.all()

    return render(request, "auctions/listing_view.html", {
        "listing": listing,
        "bid_form": CreateBidForm(),
        "comment_form": CreateCommentForm(),
        "in_watchlist": in_watchlist
    })

@login_required
@require_POST
def toggle_watchlist(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)

    return HttpResponseRedirect(reverse('listing_view', args=[pk]))

@login_required
def watchlist(request):
    # Get listings in the user's watchlist
    user_watchlist = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "listings": user_watchlist
    })


def categories(request):
    categories = Listing.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_name):
    listings = Listing.objects.filter(category=category_name, is_active=True)
    return render(request, "auctions/category_listings.html", {
        "listings": listings,
        "category": category_name
    })

@login_required
@require_POST
def submit_bid(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    form = CreateBidForm(request.POST)

    if form.is_valid():
        bid_amount = form.cleaned_data['bid_amount']

        # Check if the bid is higher than the starting bid and the current highest bid
        if bid_amount >= listing.start_bid and (listing.current_bid == 0 or bid_amount > listing.current_bid):
            listing.current_bid = bid_amount
            listing.save()

            new_bid = Bid(
                owner = request.user,
                listing = listing,
                bid_amount = bid_amount
            )
            new_bid.save()
            messages.success(request, 'Bid placed succesfully!')
        else:
            messages.error(request, 'Bid must be at least as large as the starting bid and higher than the current bid')

    return HttpResponseRedirect(reverse('listing_view', args=[pk]))

def close_auction(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.user != listing.owner:
        messages.error(request, 'You are not authorized to close this auction.')
        return HttpResponseRedirect(reverse('listing_view'), args=[pk])
    
    listing.is_active = False
    # Assuming the highest bid is the current bid on the listing
    highest_bid = Bid.objects.filter(listing=listing).order_by('-bid_amount').first()
    if highest_bid:
        listing.winner = highest_bid.owner

    listing.save()
    messages.success(request, 'Auction closes successfully.')
    return HttpResponseRedirect(reverse('listing_view', args=[pk]))
