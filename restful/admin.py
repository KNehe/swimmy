from django.contrib import admin

from restful.models import Booking, FileUpload, Pool, Rating

from django.contrib import admin

admin.site.register(Pool)
admin.site.register(Booking)
admin.site.register(Rating)
admin.site.register(FileUpload)
