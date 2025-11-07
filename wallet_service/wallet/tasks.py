from celery import shared_task


@shared_task
def flush_kafka():
    from .producers import producer

    producer.flush(timeout=5)
