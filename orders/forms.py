from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'city']

        widgets = {
            'first_name': forms.TextInput(attrs={'type': "text", 'class': "", 'placeholder': "Илон",
                                                 'required': True, 'autofocus': True}),
            'last_name': forms.TextInput(attrs={'type': "text", 'class': "", 'placeholder': "Маск",
                                                'required': True}),
            'email': forms.EmailInput(attrs={'type': "email", 'class': "", 'placeholder': "elonmusk@evc.group",
                                             'required': True}),
            'phone': forms.TextInput(attrs={'type': "text", 'class': "", 'required': True}),
            'address': forms.TextInput(attrs={'required': False}),
            'postal_code': forms.TextInput(attrs={'required': False}),
            'city': forms.TextInput(attrs={'required': False}),
        }
