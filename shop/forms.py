from django.forms import ModelForm
from .models import *
from django import forms


class SubscriberForm(ModelForm):
    class Meta:
        model = Subscriber
        exclude = [""]


class CheckoutForm(forms.Form):
    name = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=True)
