from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


# Create your models here.
class DishType(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Dish type name",
        help_text="Enter the name of the dish type (e.g. Soup, Dessert)."
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "dish type"
        verbose_name_plural = "dish types"

    def __str__(self):
        return self.name


class Cook(AbstractUser):
    years_of_experience = models.IntegerField(
        default=0,
        verbose_name="Years of experience",
        help_text="Enter the years of experience.",
        validators=[
            MinValueValidator(
                0,
                message="Years Of Experience can`t be negative."
        ),
            MaxValueValidator(
                40,
                message="Experience cannot exceed 40 years.")
        ]
    )

    class Meta:
        verbose_name = "cook"
        verbose_name_plural = "cooks"

    def get_absolute_url(self):
        return reverse(
            "kitchen:cook-detail",
            kwargs={"pk": self.pk}
        )

    def __str__(self):
        return (f"{self.username} ({self.first_name} {self.last_name}), "
                f"years of experience: {self.years_of_experience}")


class Dish(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Dish name",
        help_text="Enter the name of the dish.",
    )
    description = models.TextField(
        max_length=500,
        verbose_name="Dish description",
        help_text="Enter the description of the dish.",)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        verbose_name="Dish price",
        help_text="Enter the price of the dish.",
        validators=[
            MinValueValidator(
                0.01,
                message="Price must be greater than 0"
            )
        ]
    )
    dish_type = models.ForeignKey(
        DishType,
        on_delete=models.SET_NULL,
        null=True,
    )
    cooks = models.ManyToManyField(Cook, related_name="dishes")

    class Meta:
        ordering = ("-price",)

    def __str__(self):
        return self.name
