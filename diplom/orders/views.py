from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart


@login_required(login_url ='/user/login/')
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.save()
            for item in cart:
                discounted_price = item['product'].sell_price()
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=discounted_price,
                    quantity=item['quantity']
                )
            cart.clear()
            return render(
                request,
                'orders/order/created.html',
                {'cart': cart, 'form': form}
            )
    else:
        form = OrderCreateForm(request=request)
    return render(
        request,
        'orders/order/create.html',
        {'cart': cart, 'form': form}
    )