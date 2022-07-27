from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.http import HttpResponseNotFound
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


# https://stackoverflow.com/questions/2809547/creating-email-templates-with-django
def send_mail_format(form, cart, order_id):
    d = {
        'email': form.cleaned_data['email'],
        'name': f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
        'phone': form.cleaned_data['phone'],
        'order_id': order_id,
        'cart': cart,
        'total': cart.get_total_price()
    }
    subject, from_email, to = 'EVC Group | New Order', 'info@evc.group', ['mitchburneo@gmail.com', 'parts@evc.group']

    html_message = get_template('epc/order_info_email.html')
    msg = EmailMultiAlternatives(subject, '', from_email, to)
    msg.attach_alternative(html_message.render(d), "text/html")
    msg.send()


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid() and (cart.__len__() > 0):
            order = form.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    cost=item['price'],
                    quantity=item['quantity']
                )

            # Mail to Admins
            send_mail_format(form, cart, order.pk)
            # TODO Mail to Client

            # Clear Cart
            cart.clear()
            return render(request, 'orders/created.html',
                          {'order': order})
    return HttpResponseNotFound()
