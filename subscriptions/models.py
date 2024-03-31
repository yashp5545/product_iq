from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ..apps_iq.models import App


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.app.app_name} Subscription"

class SubscriptionPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Payment for {self.subscription.app.app_name}"
