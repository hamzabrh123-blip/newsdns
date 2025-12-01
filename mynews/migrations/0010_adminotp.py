from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model("auth", "User")
    username = "hamzabrh1"
    email = "hamzabrh@gmail.com"
    password = "Hamza@4443"

    if not User.objects.filter(username=username).exists():
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )

class Migration(migrations.Migration):
    dependencies = [
        ('mynews', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
