# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from .forms import UserCreatorForm, LoginForm

from bulletin_board_app.models import Contact


@require_http_methods(["GET", "POST"])
def registration(request):
    if request.method == 'POST':
        form = UserCreatorForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=request.POST['email'], password=request.POST['password1'])
            login(request, user)
            return redirect('bulletin_board_app:home_page', 0)
    else:
        if request.session.get('token'):
            try:
                form = UserCreatorForm(instance=Contact.objects.get(token=request.session.get('token')))
            except ObjectDoesNotExist:
                form = UserCreatorForm(request.POST)
        else:
            form = UserCreatorForm()
    return render(request, 'common/registration.html', {'create_user': form})


@require_http_methods(["GET", "POST"])
def authentication_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['email'], password=request.POST['password'])
            login(request, user)
            return redirect('bulletin_board_app:home_page', 0)
    else:

        form = LoginForm()
    return render(request, 'common/login.html', {'auth_user': form})


def logout_view(request):
    logout(request)
    return redirect('bulletin_board_app:index', 0)
