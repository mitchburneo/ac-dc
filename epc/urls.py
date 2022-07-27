from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    url(r'^$', view=WelcomeView.as_view(), name='welcome'),
    url(r'^join/?$', view=RegisterUserView.as_view(), name='registration'),
    url(r'^login/?$', view=LoginUserView.as_view(), name='login'),
    url(r'^restore/?$', view=PasswordRestoreUserView.as_view(), name='restore_password'),
    url(r'^restore/success/?$', view=PasswordRestoreSuccessUserView.as_view(),
        name='restore_password_success'),
    url(r'^shield/(?P<hash_b64>[0-9A-Za-z]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,50})/?$',
        view=PasswordResetUserView.as_view(), name='reset_password_check'),
    # path('login/reset_password/<uidb64>/<token>/', view=PasswordResetUserView.as_view(), name='reset_password'),
    url(r'^shield/(?P<token>[a-z]{1,8})/?$', view=PasswordResetUserView.as_view(), name='reset_password_form'),
    # url(r'^reset/success/?$', view=PasswordResetSuccessUserView.as_view(), name='reset_password_success'),
    url(r'^logout/?$', view=LogoutView.as_view(), name='logout'),
    # url(r'^dashboard/?$', view=DashboardView.as_view(), name='dashboard'),
    url(r'^dash/?$', view=DashboardView.as_view(), name='dashboard'),
    url(r'^dash/(?P<username>[a-z0-9_.]{1,150})/?$', view=DashboardView.as_view(), name='dashboard'),
    url(r'^ajax/models/', view=ajax_get_models, name='ajax_get_models'),
    url(r'^ajax/parts/', view=ajax_get_parts_by_code, name='ajax_get_parts_by_code'),
    url(r'^ajax/get-parts-admin/', view=ajax_get_parts_admin, name='ajax_get_parts_admin'),
    url(r'^ajax/get-generation-admin/', view=ajax_get_generations, name='ajax_get_generations'),
    url(r'^ajax/get-component-admin/', view=ajax_get_component, name='ajax_get_component'),
    url(r'^ajax/get-part-group-admin/', view=ajax_get_part_group, name='ajax_get_part_group'),
    url(r'^catalogue/(?P<model>[a-z0-9]{1,5})/(?P<generation>[0-9]{1,4})/?$',
        view=ComponentGroupView.as_view(),
        name='components'),
    url(r'^catalogue/(?P<model>[a-z0-9]{1,5})/(?P<generation>[0-9]{1,4})/(?P<component>[0-9]{1,4})/?$',
        view=PartGroupView.as_view(),
        name='part_groups'),
    url(r'^catalogue/(?P<model>[a-z0-9]{1,5})/(?P<generation>[0-9]{1,4})/(?P<component>[0-9]{1,4})/'
        r'(?P<part_group>[0-9]{1,3})/?$',
        view=PartView.as_view(),
        name='parts'),
    url(r'^privacy/?', PrivacyView.as_view(), name='privacy')
    # url(r'^(?P<model>[a-z0-9_.]{1,20})/(?P<generation>[a-z0-9_.]{1,20})/?$', view=ComponentGroupView.as_view(),
    #     name=''),

    # path('<str:username>', view=DashboardView.as_view(), name='dashboard'),

    # url(r'^about/$', view=about, name='about'),
    # url(r'^edit/$', view=edit, name='edit'),
    # url(r'^$', view=home, name='home'),

    # url(r'', view=NotFoundView.as_view(), name='not_found'),
]
