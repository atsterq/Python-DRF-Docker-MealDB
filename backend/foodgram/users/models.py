from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class UserRole(models.TextChoices):
        USER = ("user", "user")
        ADMIN = ("admin", "admin")

    email = models.EmailField(
        "Email",
        max_length=200,
        unique=True,
        error_messages={
            "unique": "This email already used.",
        },
    )
    role = models.CharField(
        max_length=50, choices=UserRole.choices, default=UserRole.USER
    )
    username = models.CharField("username", max_length=200, unique=True)
    first_name = models.TextField("first_name", max_length=200)
    last_name = models.TextField("last_name", max_length=200)
    password = models.TextField("password", max_length=200)

    @property
    def is_admin(self):
        return (self.role == self.UserRole.ADMIN
                or self.is_superuser)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Follower",
        help_text="Follows recipe author",
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name="followed",
        verbose_name="Author",
        help_text="Recipe author",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_subscription"
            )
        ]
