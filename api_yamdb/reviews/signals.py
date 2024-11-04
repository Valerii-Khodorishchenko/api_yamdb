from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Review


@receiver(post_save, sender=Review)
def update_rating_on_review_save(sender, instance, **kwargs):
    title = instance.title
    reviews = Review.objects.filter(title=title)
    if reviews.exists():
        total_score = sum(review.score for review in reviews)
        average_score = total_score / reviews.count()
        title.rating = round(average_score)
        title.save()


@receiver(post_delete, sender=Review)
def update_rating_on_review_delete(sender, instance, **kwargs):
    title = instance.title
    reviews = Review.objects.filter(title=title)
    if reviews.exists():
        total_score = sum(review.score for review in reviews)
        average_score = total_score / reviews.count()
        title.rating = round(average_score)
        title.save()
    else:
        title.rating = None
        title.save()
