from django.contrib import admin
from .models import Username, Answer, Recommend

# Register your models here.
admin.site.register(Username)
admin.site.register(Recommend)
admin.site.register(Answer)
