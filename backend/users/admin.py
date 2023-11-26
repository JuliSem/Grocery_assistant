from django.contrib import admin

from users.models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    )
    search_fields = ('email', 'username')


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'author')
    list_display_links = ('user',)
    search_fields = ('user',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
