from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Image(models.Model):
    img = models.ImageField(upload_to="pictures", blank=True, null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    blur = models.IntegerField(null=False, default=9)
    threshold_percentage = models.IntegerField(null=False, default=60)
    arz = models.FloatField(null=False, default=122.2)
    tool = models.FloatField(null=False, default=89.7)
    epsilon = models.IntegerField(null=False, default=4)
    grid_size = models.FloatField(null=False, default=10.0)
    small_things = models.IntegerField(null=False, default=3)
    spline = models.BooleanField(null=False, default=True)
    degree_threshold = models.IntegerField(null=False, default=150)
    methods_spline_choices = (
        ('normal', 'Normal'),
        ('centripetal', 'Centripetal'),
        ('chord', 'Chord'),
    )
    methods_spline = models.CharField(null=False, choices=methods_spline_choices, default='normal', max_length=100)
    optimized_url = models.CharField(null=False, max_length=500, default="none")

