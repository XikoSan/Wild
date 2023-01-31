from django.db import models


class ActualManager(models.Manager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().defer("shape").filter(is_off=False)
