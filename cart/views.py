from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def cart_view(request):
    store_code = request.session.get('store_code')
    return render(request, 'Cart.html', {'store_code': store_code})
