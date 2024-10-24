from django.contrib import admin
from .models import EmailAccount, EmailMessage

class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)
    ordering = ('email',)

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_email', 'sent_date', 'receive_date', 'email_account')
    search_fields = ('subject', 'from_email', 'email_account__email')
    list_filter = ('sent_date', 'receive_date', 'email_account')
    ordering = ('-sent_date',)

admin.site.register(EmailAccount, EmailAccountAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)
