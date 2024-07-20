from django.contrib import admin
from .models import User  # Import your custom User model

# Register the User model with the admin site
admin.site.register(User)
