from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class PageView(models.Model):

    CLIENT = 'client'
    WEBSITE = 'website'
    PLATFORM_CHOICES = [
        (CLIENT, 'Client'),
        (WEBSITE, 'Website')
    ]

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE
    )

    uri = models.CharField(max_length=250)
    time = models.DateTimeField()

    platform = models.CharField(max_length=20, null=True)
    version = models.CharField(max_length=15, null=True)
    build = models.CharField(max_length=15, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            summary = PageViewSummary.objects.get(
                user = self.user
            )
        except PageViewSummary.DoesNotExist:
            summary = PageViewSummary.objects.create(
                user = self.user
            )
        summary.last_page_view = self
        summary.save()

class PageViewSummary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = '+'
    )

    first_page_view = models.ForeignKey(
        PageView,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )
    last_page_view = models.ForeignKey(
        PageView,
        null = True,
        on_delete = models.SET_NULL,
        related_name = '+'
    )

    def update(self):
        page_view_query = PageView.objects.filter(user=self.user) \
        .order_by('time')

        self.first_page_view = page_view_query.first()
        self.last_page_view = page_view_query.last()
        self.save()
