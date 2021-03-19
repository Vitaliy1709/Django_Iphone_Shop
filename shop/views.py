from django.contrib import messages
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import reverse

from .forms import SubscriberForm, CheckoutForm
from .models import *
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .emails import SendingEmail
from .uploading import UploadingProducts
import json
from decimal import Decimal
from datetime import date, datetime


def landing(request):
    template_name = "shop/landing.html"
    form = SubscriberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        new_form = form.save()

    return render(request, template_name, locals())


def index(request):
    template_name = "shop/index.html"
    products_images = ProductImage.objects.filter(is_active=True, is_main=True, product__is_active=True)
    products_images_phones = products_images.filter(product__category__id=1)
    products_images_laptops = products_images.filter(product__category__id=2)
    return render(request, template_name, locals())


def product(request, product_id):
    template_name = "shop/product.html"
    products = Product.objects.get(id=product_id)

    session_key = request.session.session_key
    if not session_key:
        request.session.cycle_key()

    return render(request, template_name, locals())


def basket_adding(request):
    return_dict = dict()
    session_key = request.session.session_key

    data = request.POST
    product_id = data.get("product_id")
    nmb = data.get("nmb")
    is_delete = data.get("is_delete")

    if is_delete == "true":
        ProductInBasket.objects.filter(id=product_id).update(is_active=False)
    else:
        new_product, created = ProductInBasket.objects.get_or_create(session_key=session_key, product_id=product_id,
                                                                     is_active=True,
                                                                     defaults={"nmb": nmb})  # , order=None)
        if not created:
            new_product.nmb += int(nmb)
            new_product.save(force_update=True)

    # common code for 2 cases

    products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True, order__isnull=True)
    products_total_nmb = products_in_basket.count()
    return_dict["products_total_nmb"] = products_total_nmb

    return_dict["products"] = list()

    for item in products_in_basket:
        product_dict = dict()
        product_dict["id"] = item.id
        product_dict["name"] = item.product.name
        product_dict["price_per_item"] = item.price_per_item
        product_dict["nmb"] = item.nmb
        return_dict["products"].append(product_dict)

    return JsonResponse(return_dict)


def checkout(request):
    template_name = "shop/checkout.html"
    session_key = request.session.session_key
    products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True, order__isnull=True)

    for item in products_in_basket:
        print(f"Order: {item.order}{item.product}")

    form = CheckoutForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            data = request.POST
            name = data.get("name")
            phone = data.get("phone")
            email = data.get("email")
            user, created = User.objects.get_or_create(username=phone, defaults={"first_name": name, "email": email})

            order = Order.objects.create(user=user, customer_name=name, customer_phone=phone,
                                         customer_email=email, status_id=1)

            for name, value in data.items():
                if name.startswith("product_in_basket_"):
                    product_in_basket_id = name.split("product_in_basket_")[1]
                    product_in_basket = ProductInBasket.objects.get(id=product_in_basket_id)
                    product_in_basket.nmb = value
                    product_in_basket.order = order
                    product_in_basket.save(force_update=True)

                    ProductInOrder.objects.create(product=product_in_basket.product, nmb=product_in_basket.nmb,
                                                  price_per_item=product_in_basket.price_per_item,
                                                  total_price=product_in_basket.total_price, order=order)

            # sending notification emails

            email = SendingEmail()
            email.sending_email(type_id=1, order=order)
            email.sending_email(type_id=2, email=order.customer_email, order=order)

            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    return render(request, template_name, locals())


def merging_dicts(l1, l2, key1, key2):
    merged = {}
    for item in l1:
        merged[item[key1]] = item
    for item in l2:
        try:
            if "products" in merged[item[key2]]:
                merged[item[key2]]["products"].append(item)
            else:
                merged[item[key2]] = [item]

        except Exception as e:
            return True

    orders = [val for (_, val) in merged.items()]
    return orders


def admin_orders(request):
    user = request.user
    template_name = "shop/admin_orders.html"

    if user.is_superuser:

        orders = Order.objects.all().annotate(products_nmb=Count("productinorder")).values()
        order_ids = [order["id"] for order in orders]

        # counting of number of products
        products_in_order = ProductInOrder.objects.filter(is_active=True, order_id__in=order_ids).values(
            "order_id", "product__name", "nmb", "price_per_item", "total_price")

        orders = merging_dicts(list(orders), list(products_in_order), "id", "order_id")
        return render(request, template_name, locals())
    else:
        return HttpResponseRedirect(reverse("index"))


def download_products(request):
    template_name = "shop/download_products.html"
    if request.POST:
        file = request.FILES["file"]
        uploading_file = UploadingProducts({"file": file})
        if uploading_file:
            messages.success(request, "Успешная загрузка!")
        else:
            messages.error(request, "Ошибка при загрузке!")
    return render(request, template_name, locals())


def dashboard(request):
    user = request.user
    if not user.is_superuser:
        return HttpResponseRedirect(reverse("index"))

    all_orders_by_dates = Order.objects.all() \
        .annotate(date_item=TruncDate("created")) \
        .values("date_item", "status__name", "status_id") \
        .annotate(orders_amount=Sum("total_price")) \
        .order_by("date_item")

    dates_list = list()
    all_orders_by_dates_dict = dict()
    cancelled_orders_by_dates_dict = dict()

    for order_by_dates in all_orders_by_dates:
        if not order_by_dates["date_item"] in dates_list:
            dates_list.append(order_by_dates["date_item"])

        if order_by_dates["date_item"] in all_orders_by_dates_dict:
            all_orders_by_dates_dict[order_by_dates["date_item"]] += order_by_dates["orders_amount"]
        else:
            all_orders_by_dates_dict[order_by_dates["date_item"]] = order_by_dates["orders_amount"]

        if order_by_dates["status_id"] == 4:
            if order_by_dates["date_item"] in cancelled_orders_by_dates_dict:
                cancelled_orders_by_dates_dict[order_by_dates["date_item"]] += order_by_dates["orders_amount"]
            else:
                cancelled_orders_by_dates_dict[order_by_dates["date_item"]] = order_by_dates["orders_amount"]

    all_orders_by_dates_data = list()
    for date_item in dates_list:
        if date_item in all_orders_by_dates_dict:
            all_orders_by_dates_data.append(all_orders_by_dates_dict[date_item])
        else:
            all_orders_by_dates_data.append(0)

    cancelled_orders_by_dates_data = list()
    for date_item in dates_list:
        if date_item in cancelled_orders_by_dates_dict:
            cancelled_orders_by_dates_data.append(cancelled_orders_by_dates_dict[date_item])
        else:
            cancelled_orders_by_dates_data.append(0)

    charts_data = dict()
    charts_data["chart_orders"] = dict()
    charts_data["chart_orders"]["dates_list"] = dates_list
    charts_data["chart_orders"]["series"] = [
        {"name": "все заказы", "data": all_orders_by_dates_data},
        {"name": "отмененные заказы", "data": cancelled_orders_by_dates_data},
    ]

    # SECOND CHART
    products_in_orders_by_dates = ProductInOrder.objects.all() \
        .annotate(date_item=TruncDate("created")) \
        .values("date_item", "product__name") \
        .annotate(orders_amount=Sum("total_price")) \
        .order_by("date_item")

    products_in_orders_by_dates_dict = dict()
    for product_in_orders in products_in_orders_by_dates:
        if product_in_orders["product__name"] in products_in_orders_by_dates_dict:
            products_in_orders_by_dates_dict[product_in_orders["product__name"]][product_in_orders["date_item"]] = \
                product_in_orders["orders_amount"]
        else:
            products_in_orders_by_dates_dict[product_in_orders["product__name"]] = {
                product_in_orders["date_item"]: product_in_orders["orders_amount"]
            }

    charts_data["chart_products_in_orders"] = dict()
    charts_data["chart_products_in_orders"]["dates_list"] = dates_list
    charts_data["chart_products_in_orders"]["series"] = []

    for products, data in products_in_orders_by_dates_dict.items():

        data_list = list()
        for item_data in data_list:
            data_value = data.get(item_data, 0)
            data_list.append(data_value)

        charts_data["chart_products_in_orders"]["series"].append \
                (
                {"name": products,
                 "data": data_list}
            )

    def custom_serializer(obj):
        if isinstance(obj, (datetime, date)):
            serial = obj.isoformat()
            return serial
        elif isinstance(obj, Decimal):
            return float(obj)

    charts_data = json.dumps(charts_data, default=custom_serializer)

    return render(request, "shop/dashboard.html", locals())
