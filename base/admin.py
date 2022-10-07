from django.contrib import admin
from .models import Abstract, Topic, Message
# Register your models here.
admin.site.register(Abstract)
admin.site.register(Topic)
admin.site.register(Message)
