from __future__ import unicode_literals
import django.conf
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetCompleteView, PasswordContextMixin
from django.core.exceptions import ValidationError
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, TemplateView
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from re import compile

import cart.forms
from epc.forms import RegistrationUserForm, LoginForm, RestorePasswordForm, ResetPasswordForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView, BaseFormView
from django.contrib.auth.tokens import default_token_generator

from ipware import get_client_ip
from epc.models import *
from django.core import serializers
from django.db.models import IntegerField, TextField
from django.db.models.functions import Cast
from django.db.models.expressions import F, Value, Func, Q
from django.contrib.postgres.fields import ArrayField
import json
from django.db import connection, reset_queries
import time
import functools


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func

# import logging

# log = logging.getLogger('django.db.backends')
# log.setLevel(logging.DEBUG)
# log.addHandler(logging.StreamHandler())


UserModel = get_user_model()


def ajax_get_generations(request):
    print('Entry on epc/views > ajax_get_generations')
    model = request.POST.get('model')
    data_to_send = {}
    try:
        if model:
            generation_query = Generation.objects.filter(model_id=model)
            # data_to_send = {m.model: m.generation for m in full_data_m2m}
            data_to_send = serializers.serialize('json', list(generation_query))
    except ObjectDoesNotExist:
        print('ERROR: epc/views > ajax_get_generations')
    print(data_to_send)
    return JsonResponse(data=data_to_send, safe=False)


def ajax_get_component(request):
    print('Entry on epc/views > ajax_get_component')
    component_group = request.POST.get('component_group')
    data_to_send = {}
    try:
        if component_group:
            generation_query = Component.objects.filter(component_group_id=component_group)
            # data_to_send = {m.model: m.generation for m in full_data_m2m}
            data_to_send = serializers.serialize('json', list(generation_query))
    except ObjectDoesNotExist:
        print('ERROR: epc/views > ajax_get_component')
    print(data_to_send)
    return JsonResponse(data=data_to_send, safe=False)


def ajax_get_part_group(request):
    print('Entry on epc/views > ajax_get_part_group')
    component = request.POST.get('component')
    data_to_send = {}
    try:
        if component:
            print('DEPRECATED UNTIL REFACTORING')
            # TODO Change component_id=component to c_code and cg_code and search in m2m
            generation_query = PartGroup.objects.filter(component_id=component, )
            # data_to_send = {m.model: m.generation for m in full_data_m2m}
            data_to_send = serializers.serialize('json', list(generation_query))
    except ObjectDoesNotExist:
        print('ERROR: epc/views > ajax_get_part_group')
    print(data_to_send)
    return JsonResponse(data=data_to_send, safe=False)


def ajax_get_models(request):
    print('Entry on epc/views > ajax_get_models')
    # brand = request.POST.get('brand')
    # models = {}
    # try:
    #     if brand:
    #         models_query = Model.objects.filter(brand_id=brand)
    #         # models = {m.name: m.pk for m in models_query}
    #         models = serializers.serialize('json', list(models_query))
    # except ObjectDoesNotExist:
    #     print('ERROR: epc/views > ajax_get_models')
    #
    # return JsonResponse(data=models, safe=False)


def ajax_get_parts_admin(request):
    print('Entry on epc/views > ajax_get_parts_admin')
    code = request.POST.get('code')
    parts = []

    try:
        if code:
            full_data_m2m = Part.objects.filter(
                part_code__icontains=code
            )[:10]

            for m2m in full_data_m2m:
                parts.append({
                    'id': m2m.pk,
                })

    except ObjectDoesNotExist:
        print('ERROR: epc/views > ajax_get_parts_admin')

    return JsonResponse(data=json.dumps(parts), safe=False)


@query_debugger
def ajax_get_parts_by_code(request):
    print('Entry on epc/views > ajax_get_parts_by_code')
    code = request.POST.get('code')
    model = request.POST.get('model')
    generation = request.POST.get('generation')
    parts = []
    try:
        if code:
            if model and generation:
                full_data_m2m = M2MPartGroupToPart.objects.select_related(
                    'model',
                    'generation',
                    'component_group',
                    'component',
                    'part_group'
                ).filter(
                    Q(part__part_code__icontains=code) | Q(part__part_name__icontains=code),
                    model__name__iexact=model,
                    generation__name__startswith=generation,
                )[:10]
            else:
                full_data_m2m = M2MPartGroupToPart.objects.select_related(
                    'model',
                    'generation',
                    'component_group',
                    'component',
                    'part_group'
                ).filter(
                    Q(part__part_code__icontains=code) | Q(part__part_name__icontains=code)
                )[:10]

            for m2m in full_data_m2m:
                parts.append({
                    'id': m2m.part.id,
                    'name': m2m.part.part_name,
                    'code': m2m.part.part_code,
                    'model': m2m.model.name,
                    'model_url': m2m.model.url_code,
                    'generation': m2m.generation.name,
                    'generation_url': m2m.generation.code,
                    'component_group': m2m.component_group.name,
                    'component': m2m.component.name,
                    'component_url': m2m.component.url_code,
                    'part_group': m2m.part_group.name,
                    'part_group_url': m2m.part_group.pk,
                })

    except ObjectDoesNotExist:
        print('ERROR: epc/views > ajax_get_models')

    return JsonResponse(data=json.dumps(parts), safe=False)


class RegisterUserView(CreateView):
    form_class = RegistrationUserForm
    template_name = "epc/registration.html"
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('welcome'))  # kwargs={'username': request.user.username}
        return super(RegisterUserView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # user = form.save(commit=True)
        # user.set_password(form.cleaned_data['password'])
        # ser.save()
        # return redirect()
        return super(RegisterUserView, self).form_valid(form)


class WelcomeView(TemplateView):
    template_name = "epc/welcome.html"

    def dispatch(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
        return super(WelcomeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['models'] = serializers.serialize('json', Model.objects.all())
        # context['generations'] = serializers.serialize('json', Generation.objects.all())
        models_dict = {}
        # for generation in generations:
        #     models_dict =
        # context['models'] = Model.objects.all()
        qs = Generation.objects.all().prefetch_related('model')
        for gen in qs:
            if gen.model in models_dict:
                models_dict[gen.model].append([gen.name, gen.code])
            else:
                models_dict[gen.model] = [[gen.name, gen.code]]
        print(models_dict)
        # qs = Generation.objects.all().annotate(
        #     model_name=F('model__name')).annotate(gen_name=F('name')).values('model_name', 'gen_name')
        # context['generations'] = Generation.objects.raw(
        #     'SELECT m.name, g.name FROM generation g JOIN model m ON m.id = g.model_id;')
        # for generation in context['generations']:
        #     print(generation)
        # for model in qs:
        #     models_dict.
        context['models'] = models_dict
        # context['models_json'] = json.dumps(models_dict)
        return context


class LoginUserView(LoginView):
    form_class = LoginForm
    template_name = "epc/login.html"
    redirect_authenticated_user = True
    # redirect_field_name = 'redirect_to'

    # CUSTOM REDIRECT AFTER SUCCESSFUL AUTH
    # def get_redirect_url(self):
    #     name = self.request.POST.get('username')
    #     if User.objects.filter(username=name).count() == 0 and \
    #             User.objects.filter(email=name).count() == 0:
    #         return super(LoginUserView, self).get_redirect_url()
    #     if name is None:
    #         return ''
    #     re_email = compile(r'(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    #     if re_email.match(name):
    #         user = User.objects.get(email=name)
    #     else:
    #         user = User.objects.get(username=name)
    #     redirect_to = user.username
    #     url_is_safe = is_safe_url(
    #         url=redirect_to,
    #         allowed_hosts=self.get_success_url_allowed_hosts(),
    #         require_https=self.request.is_secure(),
    #     )
    #     return redirect_to if url_is_safe else ''


@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'epc/dashboard.html'

    # FOR EXTRA CHECKS LIKE IS USER AUTHENTICATED
    # def dispatch(self, request, *args, **kwargs):
    #     print('DASH DISPATCH')
    #     if not User.is_authenticated:
    #         return render(request, template_name='epc/404.html')
    #     if User.objects.filter(username=self.kwargs['username']).count() == 0:
    #         return render(request, template_name='epc/404.html')
    #     return super(DashboardView, self).dispatch(request, *args, **kwargs)
    #
    # def get_context_data(self, **kwargs):
    #     context = super(DashboardView, self).get_context_data(**kwargs)
    #     context['message'] = ''
    #     return context


class NotFoundView(TemplateView):
    template_name = 'epc/404.html'

    def dispatch(self, request, *args, **kwargs):
        # Custom block
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class LogoutUserView(LogoutView):
    pass


class PasswordRestoreUserView(PasswordResetView):
    template_name = 'epc/restore_password.html'
    email_template_name = 'epc/reset_password_email.html'
    subject_template_name = 'epc/reset_password_email_subject.txt'

    form_class = RestorePasswordForm
    success_url = reverse_lazy('restore_password_success')

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('dashboard', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        client_ip, is_routable = get_client_ip(self.request)
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': 'postmaster@evc.group',  # self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
            'ip_address': client_ip,
        }
        form.save(**opts)
        return super(BaseFormView, self).form_valid(form)


class PasswordRestoreSuccessUserView(PasswordResetDoneView):
    template_name = 'epc/restore_password_success.html'

    def dispatch(self, request, *args, **kwargs):
        # if request.method != 'POST':
        #     return redirect(reverse_lazy('login'))
        return super().dispatch(request, *args, **kwargs)


class PasswordResetSuccessUserView(PasswordResetCompleteView):
    template_name = 'epc/reset_password_success.html'


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'
INTERNAL_RESET_SESSION_HASH = '_password_reset_hash'
LINK_VALIDITY_SECONDS = 3000


class PasswordResetUserView(PasswordContextMixin, FormView):
    form_class = ResetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'recover'
    success_url = reverse_lazy('login')
    template_name = 'epc/reset_password.html'
    title = 'Shield | EVC Parts'
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('login'))
        assert 'token' in kwargs
        self.validlink = False
        token = kwargs['token']

        if token == self.reset_url_token:
            session_hash = self.request.session.get(INTERNAL_RESET_SESSION_HASH)

            if not session_hash:
                return redirect(reverse_lazy('login'))
            self.user = self.get_user(session_hash)

            if self.user is not None:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(request, *args, **kwargs)
        else:
            try:
                assert 'hash_b64' in kwargs
            except AssertionError:
                return redirect(reverse_lazy('login'))
            hash_b64 = kwargs['hash_b64']
            self.user = self.get_user(hash_b64)

            if self.user is not None:
                if self.token_generator.check_token(self.user, token):
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    self.request.session[INTERNAL_RESET_SESSION_HASH] = hash_b64
                    redirect_url = self.request.path.replace(hash_b64 + '-' + token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)
        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    @staticmethod
    def get_user(hash_b64):
        try:
            session = RestorePasswordSessions.objects.get(hash_slice=urlsafe_base64_decode(hash_b64).decode())
            if int(time.time()) - session.time_of_request < LINK_VALIDITY_SECONDS:
                user = User.objects.get(pk=session.user.pk)
            else:
                user = None
                session.delete()
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError, ObjectDoesNotExist):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        # user = form.save()
        form.save()
        RestorePasswordSessions.objects.get(hash_slice=urlsafe_base64_decode(
            self.request.session[INTERNAL_RESET_SESSION_HASH]).decode()).delete()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        del self.request.session[INTERNAL_RESET_SESSION_HASH]
        # if self.post_reset_login:
        #     auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': 'Password reset unsuccessful',
                'validlink': False,
            })
        return context


class ComponentGroupView(TemplateView):
    template_name = "epc/generation_components.html"

    def dispatch(self, request, *args, **kwargs):
        # for key, value in request.POST.items():
        #     print(f'Key: {key}')
        #     print(f'Value: {value}')
        # if request.user.is_authenticated:
        return super(ComponentGroupView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            model = Model.objects.get(name__icontains=self.kwargs['model'].replace('_', ' '))
        except ObjectDoesNotExist:
            return context
        pics = PicComponentGroup.objects.filter(model_id=model.pk, generation__name__startswith=self.kwargs['generation']).order_by('component_group__code')
        cg_ids = M2MPartGroupToPart.objects.filter(
            model_id=model.pk, generation__name__startswith=self.kwargs['generation']).values('component_group_id').distinct()
        c_ids = M2MPartGroupToPart.objects.filter(
            model_id=model.pk, generation__name__startswith=self.kwargs['generation']).values('component_id').distinct()
        component_groups = ComponentGroup.objects.filter(
            pk__in=cg_ids).order_by('code')
        components = Component.objects.filter(
            component_group_id__in=cg_ids).filter(pk__in=c_ids).distinct().order_by('component_group__code')

        context['pics'] = pics
        context['generation'] = self.kwargs['generation']
        context['component_groups'] = component_groups
        context['components'] = components
        context['model'] = self.kwargs['model']  # .replace('_', ' ')
        context['model_breadcrumbs'] = model.name
        return context


class PartGroupView(TemplateView):
    template_name = "epc/part_groups.html"

    def dispatch(self, request, *args, **kwargs):
        # for key, value in request.POST.items():
        #     print(f'Key: {key}')
        #     print(f'Value: {value}')
        # if request.user.is_authenticated:
        return super(PartGroupView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            model = Model.objects.get(name__icontains=self.kwargs['model'].replace('_', ' '))
        except ObjectDoesNotExist:
            return context
        # pics = PicComponentGroup.objects.filter(model_id=model.pk, generation__name__startswith=self.kwargs['generation']).order_by('component_group__code')
        pg_ids = M2MPartGroupToPart.objects.filter(
            model_id=model.pk,
            generation__name__startswith=self.kwargs['generation'],
            component__code=self.kwargs['component'][2:],
            component_group__code=self.kwargs['component'][:2],
        ).values('part_group_id').distinct()
        # cg_ids = M2MPartGroupToPart.objects.filter(
        #     model_id=model.pk, generation__name__startswith=self.kwargs['generation']).values(
        #     'component_group_id').distinct()
        # c_ids = M2MPartGroupToPart.objects.filter(
        #     model_id=model.pk, generation__name__startswith=self.kwargs['generation']).values('component_id').distinct()
        # m2m_part_groups = M2MPartGroupToPart.objects.filter(
        #     component__code=self.kwargs['component'][2:],
        #     component_group__code=self.kwargs['component'][:2],
        #     model_id=model.pk,
        #     generation__name__startswith=self.kwargs['generation']
        # ).filter().distinct()
        part_groups = PartGroup.objects.filter(pk__in=pg_ids).distinct()
        cg_name = M2MPartGroupToPart.objects.filter(
            brand__name__icontains='Tesla',
            model_id=model.pk,
            generation__name__istartswith=self.kwargs['generation'],
            component_group__code=self.kwargs['component'][:2],
            component__code=self.kwargs['component'][2:],
        ).distinct().values_list('component__name', flat=True)[0]
        # cg_name = Component.objects.filter(code=self.kwargs['component'][2:],
        #                                    component_group__code=self.kwargs['component'][:2])[0]
        # context['pics'] = pics
        context['generation'] = self.kwargs['generation']
        context['component_full_code'] = self.kwargs['component']
        context['component'] = cg_name
        context['part_groups'] = part_groups
        # context['components'] = components
        context['model_spaceless'] = self.kwargs['model']
        context['model'] = self.kwargs['model']  # .replace('_', ' ')
        context['model_breadcrumbs'] = model.name

        generation = Generation.objects.get(name__startswith=self.kwargs['generation'])

        svg = PicPartGroup.objects.filter(brand__name__iexact='Tesla',
                                          model=model,
                                          generation=generation,
                                          part_group__in=part_groups)
        context['svg'] = svg
        return context


class PartView(FormView):
    template_name = "epc/parts.html"
    form_class = cart.forms.CartAddProductForm

    def dispatch(self, request, *args, **kwargs):
        return super(PartView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            model = Model.objects.get(name__icontains=self.kwargs['model'].replace('_', ' '))
            generation = Generation.objects.get(name__startswith=self.kwargs['generation'])
            component_group_code = self.kwargs['component'][:2]
            component_code = self.kwargs['component'][2:]
            cg_name = M2MPartGroupToPart.objects.filter(
                brand__name__icontains='Tesla',
                model_id=model.pk,
                generation__name__istartswith=self.kwargs['generation'],
                component_group__code=self.kwargs['component'][:2],
                component__code=self.kwargs['component'][2:],
            ).distinct().values_list('component__name', flat=True)[0]
            part_group = PartGroup.objects.get(pk=self.kwargs['part_group'])
        except Exception as e:
            print(e)
            return context

        try:
            svg = PicPartGroup.objects.get(brand__name__iexact='Tesla',
                                           model=model,
                                           generation=generation,
                                           part_group=part_group)
            context['svg_url'] = svg.picture.__str__().replace('.svg', '')
        except PicPartGroup.DoesNotExist:
            context['svg_url'] = None

        context['model_spaceless'] = self.kwargs['model']
        context['model_breadcrumbs'] = model.name
        context['generation'] = generation.code
        context['component'] = cg_name
        context['component_full_code'] = self.kwargs['component']
        context['part_group'] = part_group.name

        context['parts'] = M2MPartGroupToPart.objects.filter(brand__name__iexact='Tesla',
                                                             model=model,
                                                             generation=generation,
                                                             component__code=component_code,
                                                             component_group__code=component_group_code,
                                                             part_group=part_group).annotate(
            num=Cast(Func(F('number'), Value(r"\d+"), function='regexp_matches'),
                     output_field=ArrayField(IntegerField())),
            char=Func(F('number'), Value(r"\D+"), function='regexp_matches',
                      output_field=ArrayField(TextField()))).order_by('num', 'char')
        return context


class PrivacyView(TemplateView):
    template_name = "epc/privacy.html"
