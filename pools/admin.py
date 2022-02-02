from django.contrib import admin

from pools.models import Booking, FileUpload, Pool, Rating, User

from django.contrib import admin

admin.site.register(Pool)
admin.site.register(Booking)
admin.site.register(Rating)
admin.site.register(FileUpload)
admin.site.register(User)