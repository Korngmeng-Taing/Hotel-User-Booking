from django.http import HttpResponse
from django.shortcuts import render, redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request,*args,**kwargs)
    return wrapper_func

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('dashboard')
        else:
            return redirect('login')
    return wrapper_func