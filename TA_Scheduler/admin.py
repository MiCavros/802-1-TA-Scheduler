from django.contrib import admin
from .models import User, userPublicInfo, userPrivateInfo, Class, Section

admin.site.register(User)
admin.site.register(userPublicInfo)
admin.site.register(userPrivateInfo)
admin.site.register(Class)
admin.site.register(Section)


