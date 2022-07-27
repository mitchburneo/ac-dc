from .cart import Cart


def cart(request):
    __cart__ = Cart(request)
    return {'cart': __cart__, 'cart_ids': __cart__.get_id_list()}
