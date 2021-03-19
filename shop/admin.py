from django.contrib import admin
from .models import *

from import_export.admin import ImportExportActionModelAdmin
from import_export import resources
from import_export import fields
from import_export.widgets import ForeignKeyWidget


class ProductInOrderInline(admin.TabularInline):
    model = ProductInOrder
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class EmailSendingFactInline(admin.TabularInline):
    model = EmailSendingFact
    extra = 0


class StatusAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Status._meta.fields]

    class Meta:
        model = Status


class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]
    inlines = [ProductInOrderInline]

    class Meta:
        model = Order


class ProductInOrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductInOrder._meta.fields]

    class Meta:
        model = ProductInOrder


class SubscriberAdmin(admin.ModelAdmin):
    # list_display = ["name", "email"]
    list_display = [field.name for field in Subscriber._meta.fields]
    list_filter = ["name"]
    search_fields = ["name", "email"]

    class Meta:
        model = Subscriber


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductCategory._meta.fields]

    class Meta:
        model = ProductCategory


class ProductResource(resources.ModelResource):
    category = fields.Field(column_name="category", attribute="category",
                            widget=ForeignKeyWidget(ProductCategory, "name"))

    class Meta:
        model = Product


class ProductAdmin(ImportExportActionModelAdmin):
    resource_class = ProductResource
    list_display = [field.name for field in Product._meta.fields if field.name != "id"]
    inlines = [ProductImageInline]

    class Meta:
        model = Product


class ProductImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductImage._meta.fields]

    class Meta:
        model = ProductImage


class ProductInBasketAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductInBasket._meta.fields]

    class Meta:
        model = ProductInBasket


class EmailSendingFactAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EmailSendingFact._meta.fields]
    list_filter = ["email", "type__name"]
    search_fields = ["email", "type__name"]

    class Meta:
        model = EmailSendingFact


class EmailTypeAdmin(admin.ModelAdmin):
    include = ["name"]
    inlines = [EmailSendingFactInline]

    class Meta:
        model = EmailType


admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductInOrder, ProductInOrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductInBasket, ProductInBasketAdmin)
admin.site.register(EmailSendingFact, EmailSendingFactAdmin)
admin.site.register(EmailType, EmailTypeAdmin)
