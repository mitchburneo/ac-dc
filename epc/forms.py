from os import urandom
from re import compile
from time import time

from Crypto.Hash import MD5
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UsernameField,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from epc.models import *

UserModel = get_user_model()
hash_algorithm = MD5.new()


class RegistrationUserForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _('Пароли не совпадают'),
    }
    password1 = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': "", 'id': "input-password",
                                          'placeholder': "*********", 'name': "password",
                                          'required': True}),
        # help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': "", 'id': "input-password-confirmation",
                                          'placeholder': "*********", 'name': "password_confirmation",
                                          'required': True}),
        # help_text=_("Please repeat your password."),
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        field_classes = {'username': UsernameField, 'email': forms.EmailField}
        widgets = {
            'username': forms.TextInput(attrs={'type': "text", 'class': "", 'id': "input-username",
                                               'aria-describedby': 'username-help', 'placeholder': "elon",
                                               'name': "username", 'required': True, 'autofocus': True}),
            'email': forms.EmailInput(attrs={'type': "email", 'class': "", 'id': "input-email",
                                             'aria-describedby': "email-help",
                                             'placeholder': "elon@evc.group",
                                             'name': "email", 'required': True})
        }

    def clean(self):
        form_data = self.cleaned_data
        # Validating Username
        re_username = compile(r'^(?=.*?[a-zA-Z0-9_.].*)')
        re_letter = compile(r'^(?=.*?[a-zA-Z]).*')
        re_digit = compile(r'^(?=.*?[0-9]).*')
        username_length = len(form_data['username'])

        if User.objects.filter(username=form_data['username']).count() > 0:
            self._errors['username'] = ["Это имя пользователя уже занято"]  # "This username is already in use"
            del form_data['username']
        elif username_length < 2:
            self._errors['username'] = ["Имя пользователя должно состоять из 2-х и более символов"]
            # "Username have to contain 2 symbols at least"
            del form_data['username']
        elif not re_letter.match(form_data['username']):
            self._errors['username'] = ["Имя пользователя должно содержать как минимум 1 букву"]
            # "Username have to contain at least 1 letter"
            del form_data['username']
        elif not re_username.match(form_data['username']):
            self._errors['username'] = ["В имени пользователя допускается использование только следующих символов: "
                                        "латинские буквы, арабские цифры, _, ."]
            # "Username should contain only latin letters, digits, underscores and dots"
        # Validating E-Mail
        if User.objects.filter(email=form_data['email']).count() > 0:
            self._errors['email'] = ["Указанный e-mail уже используется"]
            # "This e-mail is already in use"
            del form_data['email']

        # Validating Password
        pass_length = len(form_data['password1'])
        # if form_data['password1'] != form_data['password2']:
        #     self._errors['password2'] = ["Passwords don't match"]
        #     del form_data['password2']
        if pass_length < 8:
            self._errors['password1'] = ["Длина пароля должна быть как минимум 8 символов"]
            # "Password length lower than 8 symbols"
            del form_data['password1']
        # elif pass_length > 32:
        #     self._errors['password'] = ["Password Length Greater Than 32 Symbols."]
        #     del form_data['password']
        elif not re_letter.match(form_data['password1']):
            self._errors['password1'] = ["Пароль должен содержать по крайней мере 1 букву"]
            # "Password should have at least one letter"
            del form_data['password1']
        elif not re_digit.match(form_data['password1']):
            self._errors['password1'] = ["Пароль должен содержать по крайней мере 1 цифру"]
            # "Password should have at least one digit"
            del form_data['password1']
        print(self._errors)
        return form_data


'''
class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'id': "input-password",
                                                                 'placeholder': "*********", 'name': "password",
                                                                 # 'minlength': "6", 'maxlength': "32",
                                                                 'required': True}))
    password_confirmation = forms.CharField(label="Repeat Password",
                                            widget=forms.PasswordInput(attrs={'class': "form-control",
                                                                              'id': "input-password-confirmation",
                                                                              'placeholder': "*********",
                                                                              'name': "password_confirmation",
                                                                              # 'minlength': "6", # 'maxlength': "32",
                                                                              'required': True}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'type': "text", 'class': "form-control", 'id': "input-username",
                                               'aria-describedby': 'username-help', 'placeholder': "mitchburneo",
                                               'name': "username", 'required': True, 'autofocus': True}),
            'email': forms.EmailInput(attrs={'type': "email", 'class': "form-control", 'id': "input-email",
                                             'aria-describedby': "email-help",
                                             'placeholder': "mitchburneo@aftermath.com",
                                             'name': "email", 'required': True})
        }

    def clean(self):
        form_data = self.cleaned_data
        # Validating Username
        re_username = compile(r'^(?=.*?[a-zA-Z0-9_.].*)')

        if User.objects.filter(username=form_data['username']).count() > 0:
            self._errors['username'] = ["User With This Login Already Registered!"]
            del form_data['username']
        elif not re_username.match(form_data['username']):
            self._errors['username'] = ["Username Should Contain Only Latin Letters, Digits, Underscores and Dots!"]
        # Validating E-Mail
        if User.objects.filter(email=form_data['email']).count() > 0:
            self._errors['email'] = ["User With This Email Already Registered!"]
            del form_data['email']
        # Validating Password
        re_letter = compile(r'^(?=.*?[a-zA-Z]).*')
        re_digit = compile(r'^(?=.*?[0-9]).*')
        pass_length = len(form_data['password'])
        if form_data['password'] != form_data['password_confirmation']:
            self._errors['password_confirmation'] = ["Passwords Don't Match. Try Again."]
            del form_data['password_confirmation']
        elif pass_length < 6:
            self._errors['password'] = ["Password Length Lower Than 6 Symbols."]
            del form_data['password']
        elif pass_length > 32:
            self._errors['password'] = ["Password Length Greater Than 32 Symbols."]
            del form_data['password']
        elif not re_letter.match(form_data['password']):
            self._errors['password'] = ["Password Should Have At Least One Letter."]
            del form_data['password']
        elif not re_digit.match(form_data['password']):
            self._errors['password'] = ["Password Should Have At Least One Digit."]
            del form_data['password']
        return form_data
'''


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'type': "text", 'class': "", 'id': "input-username",
                                      'aria-describedby': "username-help", 'placeholder': "elon@evc.group",
                                      'name': "username", 'required': True}))
    password = forms.CharField(strip=False,
                               widget=forms.PasswordInput(attrs={'class': "", 'id': "input-password",
                                                                 'placeholder': "*********", 'name': "password",
                                                                 'required': True}))

    error_messages = {
        'invalid_login': _(
            # "Please enter a correct %(username)s and password (both "
            # "fields may be case-sensitive)"
            "Пожалуйста, введите корректные данные для входа"
        ),
        'inactive': _("Этот аккаунт был деактивирован, обратитесь в службу поддержки сервиса"),
        #  "This account is deactivated"
    }


class RestorePasswordForm(PasswordResetForm):
    email = UsernameField(widget=forms.TextInput(attrs={'type': "text", 'class': "",
                                                        'id': "input-email",
                                                        'aria-describedby': 'email-help',
                                                        'placeholder': "elon@evc.group",
                                                        'name': "email", 'required': True, 'autofocus': True}))

    def clean(self):
        form_data = self.cleaned_data
        re_email = compile(r'(^|\s)[-a-zA-Z0-9_.]+@([-a-zA-Z0-9]+\.)+[a-zA-Z]{2,6}(\s|$)')
        if re_email.match(form_data['email']):
            if User.objects.filter(email__iexact=form_data['email']).count() == 0:
                self._errors['email'] = ["Нет аккаунтов, связанных с указанным E-Mail"]
                #  ["There's No Account Associated With This E-Mail"]
                del form_data['email']
        else:
            try:
                form_data['email'] = User.objects.get(username__iexact=form_data['email']).email
            except ObjectDoesNotExist:
                self._errors['email'] = ["Нет аккаунтов, связанных с указанным именем пользователя"]
                #  ["There's No Account Associated With This Username"]
                del form_data['email']
        return form_data

    def save(self, domain_override=None, subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html', use_https=False,
             token_generator=default_token_generator, from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None, ip_address='0.0.0.0'):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            try:
                RestorePasswordSessions.objects.get(user_id=user.pk).delete()
            except ObjectDoesNotExist:
                pass
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            user_email = getattr(user, email_field_name)
            hash_algorithm.update(force_bytes(user.username) + urandom(32))
            hash_slice = hash_algorithm.hexdigest()[:16]
            RestorePasswordSessions.objects.create(user=user, hash_slice=hash_slice, time_of_request=int(time()),
                                                   ip_address=ip_address).save()
            context = {
                'email': user_email,
                'domain': domain,
                'site_name': site_name,
                # 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'hash_b64': urlsafe_base64_encode(force_bytes(hash_slice)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user_email, html_email_template_name=html_email_template_name,
            )


class ResetPasswordForm(SetPasswordForm):
    error_messages = {
        'password_mismatch': _('Пароли не совпадают.'),
    }
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': "form-control", 'id': "input-password",
                                                                      'placeholder': "*********", 'name': "password",
                                                                      # 'minlength': "6", 'maxlength': "32",
                                                                      'required': True, 'autofocus': True}))
    new_password2 = forms.CharField(label="Repeat Password",
                                    widget=forms.PasswordInput(attrs={'class': "form-control",
                                                                      'id': "input-password-confirmation",
                                                                      'placeholder': "*********",
                                                                      'name': "password_confirmation",
                                                                      # 'minlength': "6", # 'maxlength': "32",
                                                                      'required': True}))

    def clean(self):
        form_data = self.cleaned_data
        # Validating Password
        re_letter = compile(r'^(?=.*?[a-zA-Z]).*')
        re_digit = compile(r'^(?=.*?[0-9]).*')
        pass_length = len(form_data['new_password1'])
        # if form_data['new_password1'] != self.cleaned_data['new_password2']:
        #     self._errors['new_password2'] = ["Passwords Don't Match. Try Again."]
        if pass_length < 8:
            self._errors['new_password1'] = ["Длина нового пароля меньше 8 символов."]
            # "Password Length Lower Than 8 Symbols."
            del form_data['new_password1']
        # elif pass_length > 32:
        #     self._errors['new_password1'] = [""]
        #     "Password Length Greater Than 32 Symbols."
        #     del form_data['new_password1']
        elif not re_letter.match(form_data['new_password1']):
            self._errors['new_password1'] = ["Пароль должен содержать хотя бы одну букву."]
            # "Password Should Have At Least One Letter."
            del form_data['new_password1']
        elif not re_digit.match(form_data['new_password1']):
            self._errors['new_password1'] = ["Пароль должен содержать хотя бы одну цифру."]
            # "Password Should Have At Least One Digit."
            del form_data['new_password1']
        return form_data


# class CustomGenerationAdminForm(forms.ModelForm):
#     brand = forms.ModelChoiceField(Brand.objects.all())
#
#     class Meta:
#         model = Generation
#         fields = [
#             'name',
#             'model',
#         ]
#
#     # Tried to order fields in admin "Add" page, but done this in admin.py easily
#     # field_order = ['brand', 'model', 'name']
#     def __init__(self, *args, **kwargs):
#         # qs = kwargs.pop('models')
#         super(CustomGenerationAdminForm, self).__init__(*args, **kwargs)
#         # self.fields['model'].queryset = qs
#         self.fields['model'].queryset = Model.objects
#
#     # def is_valid(self):
#     #     print('IS VALID')
#
#     def clean(self):
#         form_data = self.cleaned_data
#         print(form_data)


class CustomM2MPartGroupToPartAdminForm(forms.ModelForm):
    part_filter = forms.CharField(label="Part Filter", required=False)

    class Meta:
        model = M2MPartGroupToPart
        fields = '__all__'
