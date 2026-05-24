from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from django.utils.html import escape

@login_required
def home(request):
    query = request.GET.get('product', '').strip()

    if query:
        # FLAW A03 (SQL Injection) (this is the first step with A02):
        # The raw SQL query is constructed by directly embedding the user input (query) into the SQL statement
        # without proper sanitization or parameterization.
        products = Product.objects.raw( f"SELECT * FROM products_product WHERE name LIKE '%{query}%'")
        
        # FIX A03 (SQL Injection):
        # The raw SQL query is constructed using parameterized queries, which safely handle user input and 
        # prevent SQL injection attacks. 

        # products = Product.objects.filter(name__icontains=query).order_by("-created_at")
    else:
        products = Product.objects.all().order_by("-created_at")
    return render(request, "products/home.html", {"products": products})

@login_required
def add_to_cart_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # FLAW A04 (INSECURE DESIGN):
        # The application allows users to specify the quantity of a product to add to their cart without any validation,
        # which can lead to issues such as negative quantities or excessively large numbers.
        # Please, comment the all code related to the validation of the quantity input and 
        # uncomment the code that allows any quantity, including negative and excessively large numbers.

        quantity = int(request.POST.get('quantity', 1))
        
        order, created = Order.objects.get_or_create(
            user=request.user, 
            is_completed=False
        )
        
        order_item, item_created = OrderItem.objects.get_or_create(
            order=order, 
            product=product
        )
        
        if not item_created:
            order_item.quantity += quantity
        else:
            order_item.quantity = quantity
        
        if order_item.quantity == 0:
            order_item.delete()
        else:
            order_item.save()

        # FIX A04 (INSECURE DESIGN):
        # The application should validate the quantity input to ensure it is a positive integer and 
        # within a reasonable range.
        # This prevents users from adding negative quantities or excessively large numbers to their cart, 
        # which could lead to inventory issues or other unintended consequences.

        # try:
        #     quantity = int(request.POST.get('quantity', 1))
        # except (ValueError, TypeError):
        #     return redirect('home')

        # if quantity < 1:
        #     return redirect('home')

        # if quantity > 50:
        #     return redirect('home')

        # order, created = Order.objects.get_or_create(
        #     user=request.user,
        #     is_completed=False
        # )

        # if created is False and order.items.count() >= 7 and \
        #    not order.items.filter(product=product).exists():
        #     return redirect('home')

        # order_item, item_created = OrderItem.objects.get_or_create(
        #     order=order,
        #     product=product
        # )

        # new_quantity = quantity if item_created else order_item.quantity + quantity

        # if new_quantity > 50:
        #     return redirect('home')

        # order_item.quantity = new_quantity
        # order_item.save()
            
        return redirect('home')
    return redirect('home')

@login_required
def remove_from_cart_view(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
        item.delete()
    return redirect('cart')

@login_required
def cart_detail_view(request):
    cart = Order.objects.filter(user=request.user, is_completed=False).first()
    
    context = {
        'cart': cart,
    }
    return render(request, 'products/cart.html', context)

@login_required
def checkout_view(request):
    if request.method == 'POST':
        cart = Order.objects.filter(user=request.user, is_completed=False).first()
        if cart:
            # FLAW A03 (Stored XSS): 
            # It allows users to input and store malicious scripts in the shipping instructions field, 
            # which can be executed when viewed by others.
            
            cart.shipping_instructions = request.POST.get('shipping_instructions', '')

            # FIX A03 (Stored XSS):
            # The escape function from Django's utils module is used to sanitize the input by converting special characters 
            # to their HTML-safe equivalents, preventing the execution of malicious scripts.

            # cart.shipping_instructions = escape(request.POST.get('shipping_instructions', ''))
            cart.is_completed = True
            cart.save()
            
            return redirect('receipt', order_id=cart.id)
    return redirect('cart')

@login_required
def order_receipt(request, order_id):
    # FLAW A01 (Insecure Direct Object Reference - IDOR): 
    # The view retrieves an order based solely on the provided order_id without verifying that 
    # the order belongs to the authenticated user.
    order = get_object_or_404(Order, id=order_id)

    # FIX A01 (Insecure Direct Object Reference - IDOR):
    # The view should ensure that the order being accessed belongs to the authenticated user.
    
    # order = get_object_or_404(Order, id=order_id, user=request.user, is_completed=True)
    return render(request, 'products/receipt.html', {'order': order})