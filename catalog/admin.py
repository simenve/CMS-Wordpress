from django.contrib import admin
from .models import Tag, Article, User, Request
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


admin.site.register(Tag)


class UserAdmin(DjangoUserAdmin):

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_pic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',  'bool_is_author', 'bool_is_editor', 'bool_is_executive_editor',
                                    'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
        ('Subscriptions', {'fields': ('favorites', 'subscribe_author', 'subscribe_tag')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'bool_is_author', 'bool_is_editor', 'bool_is_executive_editor')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)



admin.site.register(Article)
admin.site.register(User, UserAdmin)
admin.site.register(Request)

# Register your models here.
