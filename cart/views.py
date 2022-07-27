from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from epc.models import Part
from .cart import Cart
from django.http import JsonResponse
from epc.templatetags.currency import currency
from orders.forms import OrderCreateForm


@require_POST
def cart_add(request):
    try:
        product_id = request.POST.get('part_id')
        quantity = request.POST.get('quantity')
        update = request.POST.get('update')
        cart = Cart(request)
        product = get_object_or_404(Part, id=product_id)
        cart.add(
            product=product,
            quantity=int(quantity),
            update_quantity=update
        )
        return JsonResponse(
            {
                'info': 'item_added',
                'status': 'success',
                'cart-length': cart.__len__(),
                'total-price': currency(cart.get_total_price()),
                'inline-total-price': currency(cart.get_total_price_by_item_id(product_id)),
            }
        )
    except Exception as error:
        print(error)
        return JsonResponse({'info': error.__str__(), 'status': 'error'})


@require_POST
def cart_remove(request):
    try:
        product_id = request.POST.get('part_id')
        cart = Cart(request)
        product = get_object_or_404(Part, id=product_id)
        cart.remove(product)
        return JsonResponse(
            {
                'info': 'item_deleted',
                'status': 'success',
                'cart-length': cart.__len__(),
                'total-price': currency(cart.get_total_price())
            }
        )
    except Exception as error:
        print(error)
        return JsonResponse({'info': error.__str__(), 'status': 'error'})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/detail.html', {'cart': cart, 'form': OrderCreateForm})
