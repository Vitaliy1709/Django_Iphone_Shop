from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


# from .main import disable_for_loaddata


class Subscriber(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField()

    class Meta:
        verbose_name = "subscriber"
        verbose_name_plural = "a lot of subscribers"

    def __str__(self):
        return f"Пользователь: {self.name}, email: {self.email}"


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "категория товара"
        verbose_name_plural = "категории товаров"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True, default=None)
    shot_description = models.TextField(blank=True, null=True, default=None)
    discount = models.IntegerField(default=0)
    category = models.ForeignKey(ProductCategory, blank=True, null=True, default=None, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return f"{self.name}, цена товара: {self.price}"

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/")
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"

    def __str__(self):
        return f"Фотография продукта: {self.id}. {self.image}"


class Status(models.Model):
    name = models.CharField(max_length=30, blank=True)
    in_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "статус заказа"
        verbose_name_plural = "статус заказов"

    def __str__(self):
        return f"Статус заказа: {self.name}"


class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # total_price for products in order
    customer_name = models.CharField(max_length=64, blank=True, null=True, default=None)
    customer_email = models.EmailField(blank=True, null=True, default=None)
    customer_phone = models.CharField(max_length=9, blank=True, null=True, default=None)
    customer_address = models.CharField(max_length=128, blank=True, null=True, default=None)
    comments = models.TextField(verbose_name="комментарий к заказу", blank=True)
    status = models.ForeignKey(Status, verbose_name="статус", blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "заказы"

    def __str__(self):
        return f"Покупатель: {self.customer_name}, email: {self.customer_email}, phone: {self.customer_phone}\n" \
               f"Заказ №: {self.id}, Статус заказа: {self.status.name}."

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)


def order_post_save(sender, instance, created, **kwargs):
    pass


post_save.connect(order_post_save, sender=Order)


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, blank=True, null=True, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.CASCADE)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # price * nmb
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "товар в заказе"
        verbose_name_plural = "товары в заказе"

    def __str__(self):
        return f"Заказанные товары: {self.product.name}"

    def save(self, *args, **kwargs):
        price_per_item = self.product.price
        self.price_per_item = price_per_item
        self.total_price = int(self.nmb) * self.price_per_item

        super(ProductInOrder, self).save(*args, **kwargs)


# @disable_for_loaddata
def product_in_order_post_save(sender, instance, created, **kwargs):
    order = instance.order
    all_products_in_order = ProductInOrder.objects.filter(order=order, is_active=True)

    order_total_price = 0
    for item in all_products_in_order:
        order_total_price += item.total_price

    instance.order.total_price = order_total_price

    instance.order.save(force_update=True)

    post_save.connect(product_in_order_post_save, sender=ProductInOrder)


class ProductInBasket(models.Model):
    session_key = models.CharField(max_length=255, blank=True, null=True, default=None)
    order = models.ForeignKey(Order, blank=True, null=True, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, blank=True, null=True, default=None, on_delete=models.CASCADE)
    nmb = models.IntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # price * nmb
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "товар в корзине"
        verbose_name_plural = "товары в корзине"

    def __str__(self):
        return f"Заказанные товары: {self.product.name}"

    def save(self, *args, **kwargs):
        price_per_item = self.product.price
        self.price_per_item = price_per_item
        self.total_price = int(self.nmb) * self.price_per_item
        super(ProductInBasket, self).save(*args, **kwargs)


class EmailType(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, default=None)
    in_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "тип имейла"
        verbose_name_plural = "типы имейлов"

    def __str__(self):
        return self.name


class EmailSendingFact(models.Model):
    type = models.ForeignKey(EmailType, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, blank=True, null=True, default=None,
                              on_delete=models.CASCADE)  # if email is related to any order
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "отправленный имейл"
        verbose_name_plural = "отправленные имейлы"

    def __str__(self):
        return self.type.name
