from .models import Cart
def cart_item_count(request):
    if request.user.is_authenticated:
        # Replace with actual cart retrieval logic
        cart_items = []  # Fetch actual cart items for the user
        count = len(cart_items)
    else:
        count = 0
    return {'cart_item_count': count}
