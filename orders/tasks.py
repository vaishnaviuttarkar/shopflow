from celery import shared_task


@shared_task
def send_order_confirmation(order_id):

    print(
        f"Order confirmation sent for Order #{order_id}"
    )

    return {
        "order_id": order_id,
        "status": "confirmation_sent",
    }