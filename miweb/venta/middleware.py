from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, permission_required


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [
            '/',
            '/admin/login/',
            '/logout',

        ]

    def __call__(self, request):
        if self.is_public_url(request.path):
            response = self.get_response(request)
            return response
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        response = self.get_response(request)
        return response

    def is_public_url(self, path):
        if path in self.public_urls:
            return True
        return False