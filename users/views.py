from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .models import User, CreditCard
from products.models import Order


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "users/login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect("dashboard")
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "users/login.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        direction = request.POST.get("direction", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not all([username, phone_number, password1, password2]):
            messages.error(request, "The fields marked with * are required.")
            return render(request, "users/register.html")

        if not re.fullmatch(r'[\w]{3,30}', username):
            messages.error(request, "The username must have 3-30 characters and only letters, numbers or _.")
            return render(request, "users/register.html")

        try:
            if not len(email) == 0:
                validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return render(request, "users/register.html")

        if len(email) > 254:
            messages.error(request, "The email cannot exceed 254 characters.")
            return render(request, "users/register.html")

        name_pattern = r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s\-']{1,50}$"
        if first_name and not re.fullmatch(name_pattern, first_name):
            messages.error(request, "The first name can only contain letters.")
            return render(request, "users/register.html")
        if last_name and not re.fullmatch(name_pattern, last_name):
            messages.error(request, "The last name can only contain letters.")
            return render(request, "users/register.html")

        if phone_number and not re.fullmatch(r'^\+?[\d\s\-()]{7,15}$', phone_number):
            messages.error(request, "Invalid phone number format. Example: +358 34 231 9534")
            return render(request, "users/register.html")

        if len(direction) > 255:
            messages.error(request, "The address cannot exceed 255 characters.")
            return render(request, "users/register.html")

        if password1 != password2:
            messages.error(request, "The passwords do not match.")
            return render(request, "users/register.html")

        pwd_errors = []
        if len(password1) < 8:
            pwd_errors.append("at least 8 characters")
        if not re.search(r'[A-Z]', password1):
            pwd_errors.append("an uppercase letter")
        if not re.search(r'[0-9]', password1):
            pwd_errors.append("a number")
        if not re.search(r'[^A-Za-z0-9]', password1):
            pwd_errors.append("a symbol (!@#$...)")
        if pwd_errors:
            messages.error(request, f"The password must contain: {', '.join(pwd_errors)}.")
            return render(request, "users/register.html")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is invalid, try another one.")
            return render(request, "users/register.html")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "The email is already registered, try another one.")
            return render(request, "users/register.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )
        user.phone_number = phone_number
        user.direction = direction
        user.save()

        b1 = f"{random.randint(4000, 5999)}" 
        b2 = f"{random.randint(1000, 9999)}"
        b3 = f"{random.randint(1000, 9999)}"
        b4 = f"{random.randint(1000, 9999)}"
        
        raw_number = f"{b1} {b2} {b3} {b4}"
        month = f"{random.randint(1, 12):02d}"
        year = f"{random.randint(27, 32)}"
        
        # FLAW A02 (Cryptographic Failures): 
        # Storing raw credit card data in the database is a critical security flaw.
        card_data_to_save = raw_number
        
        # FIX A02 (Cryptographic Failures): 
        # Store credit card data securely by hashing the full number and only keeping the last 4 digits visible.
        # In a real application, we never store raw credit card numbers. Instead, we would use a payment gateway or encrypt the data. 
        # Here, we will hash the full number and only keep the last 4 digits for the display.

        # card_data_to_save = make_password(raw_number)

        CreditCard.objects.create(
            user=user,
            cardholder_name=user.username.upper(),
            card_number_secure=card_data_to_save,
            card_last_four=b4,
            expiration_date=f"{month}/{year}",
            card_type=random.choice(['VISA', 'MASTERCARD'])
        )
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "users/register.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def user_profile(request):
    user = request.user
    credit_card = getattr(user, 'credit_card', None)

    recent_orders = Order.objects.filter(
        user=request.user, 
        is_completed=True
    ).order_by('-created_at')[:3]

    context = {
        "user": user,
        "credit_card": credit_card,
        "recent_orders": recent_orders,
    }
    return render(request, "users/profile.html", context)