from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("landing/", views.landing, name="landing"),
    path("product/<int:product_id>/", views.product, name="product"),
    path("basket_adding/", views.basket_adding, name="basket_adding"),
    path("checkout/", views.checkout, name="checkout"),
    path("admin_orders/", views.admin_orders, name="admin_orders"),
    path("download_products/", views.download_products, name="download_products"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
