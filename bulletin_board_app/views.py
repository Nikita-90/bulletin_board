# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .models import Advert, Tag, AdvertTag, Contact
from .forms import AdvertForm, ContactForm, AdvertFormPre

import datetime
import random


def get_page(page, adverts):
    """
    Pagination
    """
    page_next = (page + 1) if ((page + 1) <= len(adverts)/5) else page
    page_prev = (page - 1) if ((page - 1) >= 0) else page
    return page_next, page_prev


def adverts_filter(adverts, request):
    """
    Filters:  date_sort, is_active, tag, text
    Returns adverts, start_date, end_date
    """
    start_date = None
    end_date = None
    error = dict()
    if request.GET.get('date_sort'):
        adverts = date_sort_adverts(request.GET.get('date_sort'), adverts)
    if request.GET.get('start_date'):
        adverts, start_date = date_filter_adverts(request.GET.get('start_date'), request.GET.get('start_time'),
                                                  adverts, 'start')
    elif request.GET.get('start_time'):
        error['start'] = 'Заполните поле Дата'
    if request.GET.get('end_date'):
        adverts, end_date = date_filter_adverts(request.GET.get('end_date'), request.GET.get('end_time'),
                                                adverts, 'end')
    elif request.GET.get('end_time'):
        error['end'] = 'Заполните поле Дата'
    if request.GET.get('is_active'):
        adverts = active_adverts(request.GET.get('is_active'), adverts)
    if request.GET.get('tag'):
        adverts = adverts.filter(tag=Tag.objects.filter(title=request.GET.get('tag')))
    if request.GET.get('text'):
        adverts = adverts.filter(text__contains=request.GET.get('text'))
    return adverts, start_date, end_date, error


def active_adverts(active_param, adverts):
    """
    Filter by is_active.
    """
    if active_param == 'true':
        return adverts.filter(is_active=True)
    elif active_param == 'false':
        return adverts.filter(is_active=False)
    else:
        return adverts.filter(is_active__in=[True, False])


def date_filter_adverts(date_filter, time_filter, adverts, param_filter):
    """
    Parses date. Returns the filtered advert and pars_date.
    """
    date = "{} {}".format(date_filter, time_filter)
    try:
        pars_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
    except ValueError:
        pars_date = datetime.datetime.strptime(date, '%Y-%m-%d ')
    return filter_adverts(pars_date, adverts, param_filter), pars_date


def filter_adverts(date, adverts, param_filter):
    """
    Returns the filtered Adverts QuerySet by date or call error
    """
    if param_filter == 'start':
        return adverts.filter(active_until__gte=date)
    elif param_filter == 'end':
        return adverts.filter(created_at__lte=date)
    else:
        raise ValueError("Can't read param_filter.")


def date_sort_adverts(date_sort, adverts):
    """
    Return the sorted Adverts QuerySet by date.
    """
    if date_sort == 'old':
        return adverts.order_by('created_at')
    else:
        return adverts.order_by('-created_at')


def save_tags(tags, advert_id):
    """
    Saves tag and add its to AdvertTag model.
    """
    for title in tags:
        tag = Tag.objects.get_or_create(title=title)
        AdvertTag.objects.get_or_create(tag_id=tag[0].id, advert_id=advert_id)


def check_save_anonymous(request, form_cont, form_ad):
    """
    Checks data (form_cont, form_ad) when user is anonymous.
    Assigns unique token.
    """
    form_pre = AdvertFormPre(request.POST)
    if form_pre.is_valid():
        token = get_token()
        form_cont.data._mutable = True
        form_cont.data['token'] = token
        request.session['token'] = token
        request.session.set_expiry(600)
        if form_cont.is_valid():
            form_cont.save()
            form_ad.data['contact'] = form_cont.instance.id
            if form_ad.is_valid():
                form_ad.save()


def get_token():
    """
    Get unique token fo Contact
    """
    token = random.randint(10000000, 99999999)
    while True:
        if not Contact.objects.filter(token=token).exists():
            break
    return token


@require_http_methods(["GET"])
def index(request, page=0):
    """
    Page: main
    """
    page = int(page)
    adverts = Advert.objects.all().order_by('-created_at')
    adverts, start_date, end_date, error = adverts_filter(adverts, request)
    page_next, page_prev = get_page(page, adverts)
    adverts = adverts[page*5:page*5+5]
    return render(request, 'bulletin_board_app/index.html', {'adverts': adverts, 'start_date': start_date,
                                                             'end_date': end_date,
                                                             'page': page,
                                                             'page_next': page_next,
                                                             'page_prev': page_prev,
                                                             'error': error})


@require_http_methods(["GET"])
def view_advert_detail(request, advert_pk):
    """
    Page: view advert detail
    """
    advert = Advert.objects.get(pk=advert_pk)
    contact_user = advert.user if advert.user else advert.contact
    return render(request, 'bulletin_board_app/view_advert_detail.html', {'advert': advert,
                                                                          'contact_user': contact_user})


def post_add_advert(request):
    form_cont = ContactForm(request.POST)
    form_ad = AdvertForm(request.POST)
    user = request.user
    form_ad.data._mutable = True
    if user.is_authenticated:
        form_ad.data['user'] = user.id
        if form_ad.is_valid():
            form_ad.save()
    else:
        check_save_anonymous(request, form_cont, form_ad)
    save_tags(request.POST.get('tags').split(), form_ad.instance.id)


@require_http_methods(["GET", "POST"])
def add_advert(request):
    """
    Page: add advert.
    """
    user = request.user
    if request.method == 'POST':
        post_add_advert(request)
        return redirect('bulletin_board_app:index', 0)
    else:
        try:
            form_cont = ContactForm(instance=Contact.objects.get(token=request.session.get('token')))
        except ObjectDoesNotExist:
            form_cont = ContactForm()
        form_ad = AdvertForm()
        return render(request, 'bulletin_board_app/add_advert.html', {'form_ad': form_ad, 'form_cont': form_cont,
                                                                      'user': user})


@require_http_methods(["GET"])
@login_required(login_url='/authentication_user/')
def home_page(request, page):
    """
    Page: Home
    """
    page = int(page)
    user = request.user
    adverts = Advert.objects.filter(user=user).order_by('-created_at')
    adverts, start_date, end_date, error = adverts_filter(adverts, request)
    page_next, page_prev = get_page(page, adverts)
    adverts = adverts[page * 5:page * 5 + 5]
    return render(request, 'bulletin_board_app/home_page.html', {'adverts': adverts, 'start_date': start_date,
                                                                 'end_date': end_date,
                                                                 'page': page,
                                                                 'page_next': page_next,
                                                                 'page_prev': page_prev,
                                                                 'error': error})


@require_http_methods(["GET", "POST"])
@login_required(login_url='/authentication_user/')
def edit_my_advert(request, advert_pk):
    """
    Page: edit user's advert.
    """
    user = request.user
    advert = Advert.objects.get(user=user, pk=advert_pk)
    tags = ' '.join([title[0] for title in advert.tag.all().values_list('title')])
    if request.method == 'POST':
        form = AdvertForm(request.POST, instance=advert)
        if form.is_valid():
            form.save()
            save_tags(request.POST.get('tags').split(), form.instance.id)
    else:
        form = AdvertForm(instance=advert)
    return render(request, 'bulletin_board_app/edit_my_advert.html', {'form': form,
                                                                      'advert_pk': advert_pk,
                                                                      'tags': tags})


def docs(request):
    return render(request, 'bulletin_board_app/docs.html', {})
