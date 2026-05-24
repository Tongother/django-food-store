from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User
from products.models import Product
from products.models import Order
from django.contrib import messages

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin, login_url="home")
def dashboard(request):
    recent_orders = Order.objects.filter(is_completed=True).select_related('user').order_by('-created_at')[:15]
    context = {
        "total_users": User.objects.count(),
        "total_products": Product.objects.count(),
        "users_with_card": User.objects.filter(credit_card__isnull=False).count(),
        "users": User.objects.all().order_by("date_joined"),
        "products": Product.objects.all().order_by("-created_at"),
        "recent_orders": recent_orders,
    }
    return render(request, "dashboard/dashboard.html", context)

@login_required
@user_passes_test(is_admin, login_url="home")
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price", "").strip()
        image_url = request.POST.get("image_url", "").strip()
        description = request.POST.get("description", "").strip()

        if not name or not price:
            messages.error(request, "The name and price fields are required.")
            return redirect("dashboard")

        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "The price must be a positive number.")
            return redirect("dashboard")

        Product.objects.create(
            name=name,
            price=price,
            image_url=image_url or None,
            description=description or None,
        )
        messages.success(request, f'Product "{name}" added successfully.')

    return redirect("dashboard")


@login_required
@user_passes_test(is_admin, login_url="home")
def delete_product(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')

    return redirect("dashboard")