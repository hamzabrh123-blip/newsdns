from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

def create_admin():
    User = get_user_model()
    username = "hamzabrh1"
    email = "hamzabrh@gmail.com"
    password = "Hamza@4443"

    try:
        if not User.objects.filter(username=username).exists():
            print(">>> Creating admin user...")
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        else:
            print(">>> Admin already exists.")
    except OperationalError:
        # Database isn't ready yet (first migrate), ignore
        print(">>> Database not ready for admin creation.")
