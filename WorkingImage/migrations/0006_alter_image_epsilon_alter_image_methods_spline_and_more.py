# Generated by Django 5.0.6 on 2024-05-27 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkingImage', '0005_alter_image_methods_spline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='epsilon',
            field=models.IntegerField(default=4),
        ),
        migrations.AlterField(
            model_name='image',
            name='methods_spline',
            field=models.CharField(choices=[('normal', 'Normal'), ('centripetal', 'Centripetal'), ('chord', 'Chord')], default='normal', max_length=100),
        ),
        migrations.AlterField(
            model_name='image',
            name='spline',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='tool',
            field=models.FloatField(default=89.7),
        ),
    ]
