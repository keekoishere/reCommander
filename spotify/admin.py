from django.contrib import admin

from .models import Username, Recommend, Answer

# adding models to appear on the admin interface
admin.site.register(Username)
admin.site.register(Recommend)
admin.site.register(Answer)
