from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    CharField,
    EmailField,
    ForeignKey,
    Model,
    TextField,
    UniqueConstraint,
)


class User(AbstractUser):
    """
    User model based on abstract user class.

    All fields are required. Username and email are unique.
    """

    email = EmailField(
        "Email",
        max_length=200,
        unique=True,
        error_messages={
            "unique": "This email already used.",
        },
    )

    username = CharField("username", max_length=200, unique=True)
    first_name = TextField("first_name", max_length=200)
    last_name = TextField("last_name", max_length=200)
    password = TextField("password", max_length=200)

    def __str__(self):
        return self.username


class Subscription(Model):
    """
    Subscription model based on abstract model.

    It represents user's subscriptions to recipe author.

    User's subscriptions are unique.
    """

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="subscriber",
        verbose_name="Subscriber",
        help_text="Subscribed on recipe author",
    )
    author = ForeignKey(
        User,
        null=True,
        on_delete=CASCADE,
        related_name="author",
        verbose_name="Author",
        help_text="Recipe author",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["author", "user"], name="unique_subscription"
            )
        ]
