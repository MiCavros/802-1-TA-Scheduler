from django.db.models.fields import return_None
from django.shortcuts import render, redirect
from django.views import View
from .models import User, userPublicInfo, userPrivateInfo, Class, Section

class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        return render(request, 'login.html')

class Home(View):
    def get(self, request):
        return render(request, 'home.html')
    def post(self, request):
        return render(request, 'home.html')