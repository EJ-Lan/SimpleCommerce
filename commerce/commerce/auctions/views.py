from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages

from .models import Listing, User

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

    return render(request, "auctions/listing_view.html", {
        "listing": listing,
        "bid_form": CreateBidForm(),
        "comment_form": CreateCommentForm()
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html")
