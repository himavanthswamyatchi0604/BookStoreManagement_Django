from .models import CartItem


def cart_item_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        count = len(cart_items)
    else:
        count = 0
    return {'cart_item_count': count}
