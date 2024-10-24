from django.shortcuts import render

from .models import EmailAccount


def index(request):
    email_accounts = EmailAccount.objects.all()
    return render(
        request, 'main_page.html', {'email_accounts': email_accounts}
    )

def login(request):
    return render(request, 'login_page.html')