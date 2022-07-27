from django import forms
from django.contrib.auth.forms import (
    UsernameField,
    UserCreationForm
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 100)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


# class CheckoutForm(UserCreationForm):
#     error_messages = {
#
#     }
#
#     class Meta:
#         model = User
#         fields = ['username', 'email']
#         field_classes = {'username': UsernameField, 'email': forms.EmailField}
#         widgets = {
#             'username': forms.TextInput(attrs={'type': "text", 'class': "", 'id': "input-username",
#                                                'aria-describedby': 'username-help', 'placeholder': "mitchburneo",
#                                                'name': "username", 'required': True, 'autofocus': True}),
#             'email': forms.EmailInput(attrs={'type': "email", 'class': "", 'id': "input-email",
#                                              'aria-describedby': "email-help",
#                                              'placeholder': "mitchburneo@evc.group",
#                                              'name': "email", 'required': True})
#         }
#
#     def clean(self):
#         form_data = self.cleaned_data
#         # Validating Username
#         re_username = compile(r'^(?=.*?[a-zA-Z0-9_.].*)')
#         re_letter = compile(r'^(?=.*?[a-zA-Z]).*')
#         re_digit = compile(r'^(?=.*?[0-9]).*')
#         username_length = len(form_data['username'])
#
#         if User.objects.filter(username=form_data['username']).count() > 0:
#             self._errors['username'] = ["This username is already in use"]
#             del form_data['username']
#         elif username_length < 2:
#             self._errors['username'] = ["Username have to contain 2 symbols at least"]
#             del form_data['username']
#         elif not re_letter.match(form_data['username']):
#             self._errors['username'] = ["Username have to contain at least 1 letter"]
#             del form_data['username']
#         elif not re_username.match(form_data['username']):
#             self._errors['username'] = ["Username should contain only latin letters, digits, underscores and dots"]
#         # Validating E-Mail
#         if User.objects.filter(email=form_data['email']).count() > 0:
#             self._errors['email'] = ["This e-mail is already in use"]
#             del form_data['email']
#
#
#         return form_data
#
