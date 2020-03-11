from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .forms import SignUpForm
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.models import Group
from .models import Picture
from django.db import connection


def signup(request):
    if request.method == 'GET':
        return render(request, 'accounts/signup.html')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'accounts/signup_confirm.html',)
        else:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO accounts_picture (title, URL_way) VALUES ('Красная роза на фоне поляны', 'static/images/rose.png')")
            cursor.execute("INSERT INTO accounts_picture (title, URL_way) VALUES ('Море в плохую погоду', 'static/images/sea.png')")
            cursor.execute("SELECT * FROM accounts_picture WHERE title = 'Море в плохую погоду'")
            row = cursor.fetchall()
            print(row)
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        user.groups.add(Group.objects.get(name='Service Users'))
        return render(request, 'accounts/signup_success.html',)
    else:
        return render(request, 'accounts/signup_failed.html',)