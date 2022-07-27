from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from re import compile


class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = compile(r'(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
        try:
            if email.match(username):
                user = User.objects.get(email=username)
                if user.check_password(password):
                    return user
                else:
                    return None
            else:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
                else:
                    return None
        except ObjectDoesNotExist:
            raise ValidationError("Неверные данные")
            # "Invalid Credentials"

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None
