from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from decimal import Decimal
from orders.models import Order
from django.conf import settings
import yookassa
from yookassa import Configuration, Payment

# Настройка конфигурации Yookassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(
            reverse('payment:completed')
        )
        cancel_url = request.build_absolute_uri(
            reverse('payment:canceled')
        )
        
        # Создаем описание заказа
        description = f"Заказ №{order.id}"
        
        # Создаем список товаров для Yookassa
        items = []
        for item in order.items.all():
            discounted_price = item.product.sell_price()
            items.append({
                "description": item.product.name,
                "quantity": str(item.quantity),
                "amount": {
                    "value": str(round(float(discounted_price), 2)),
                    "currency": "RUB"  # Yookassa работает с рублями
                },
                "vat_code": "1",  # НДС по ставке 20%
            })
        
        # Создаем платеж в Yookassa
        payment = Payment.create({
            "amount": {
                "value": str(round(float(order.get_total_cost()), 2)),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": success_url
            },
            "capture": True,
            "description": description,
            "metadata": {
                "order_id": order.id
            },
            "receipt": {
                "customer": {
                    "email": order.email
                },
                "items": items
            }
        }, idempotency_key=str(order.id))
        
        # Перенаправляем пользователя на страницу оплаты Yookassa
        return redirect(payment.confirmation.confirmation_url, code=303)
    else:
        return render(request, 'payment/process.html', locals())
    

def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')