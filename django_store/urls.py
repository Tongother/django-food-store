from django.urls import path
from products.views import home, add_to_cart_view, cart_detail_view, order_receipt, checkout_view, remove_from_cart_view
from users.views import login_view, register_view, logout_view, user_profile
from django.contrib import admin
from dashboard.views import dashboard, add_product, delete_product
from evil.views import collect

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
    path("dashboard/", dashboard, name="dashboard"),
    path('profile/', user_profile, name='profile'),
    path("products/add/", add_product, name="add_product"),
    path("products/<int:product_id>/delete/", delete_product, name="delete_product"),
    path("products/<int:product_id>/add-to-cart/", add_to_cart_view, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", remove_from_cart_view, name="remove_from_cart"),
    path("checkout/", checkout_view, name="checkout"),
    path("receipt/<int:order_id>/", order_receipt, name="receipt"),
    path("cart/", cart_detail_view,  name="cart"),
    path("evil/", collect, name="collect"),
]