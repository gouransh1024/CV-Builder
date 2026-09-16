# Generated to configure default Admin and User accounts
from django.db import migrations

def create_default_users(apps, schema_editor):
    from django.contrib.auth.models import User
    
    # Remove any existing users to ensure a clean state
    User.objects.all().delete()
    
    # Create Admin superuser
    User.objects.create_superuser(
        username='Admin',
        email='admin@example.com',
        password='Admin1234'
    )
    
    # Create regular User
    User.objects.create_user(
        username='User',
        email='user@example.com',
        password='User1234'
    )

def reverse_default_users(apps, schema_editor):
    from django.contrib.auth.models import User
    User.objects.filter(username__in=['Admin', 'User']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('career_app', '0004_resumedraft'),
    ]

    operations = [
        migrations.RunPython(create_default_users, reverse_default_users),
    ]
