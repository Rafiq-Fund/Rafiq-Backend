from django.contrib import admin
from account.models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    
class ProfileAdmin(admin.ModelAdmin):
    list_editable = [ 'verified']
    list_display = ['user', 'full_name', 'verified']
    
admin.site.register(User, UserAdmin)
