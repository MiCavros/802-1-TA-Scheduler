from django.db.models.fields import return_None
from django.shortcuts import render, redirect
from django.views import View
from .models import User, userPublicInfo, userPrivateInfo, Class, Section

class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        noUser = False
        badPassword = False
        blankEntry = False
        if request.POST['email'] == "" or request.POST['password'] == "":
            return render(request, "login.html", {"message": "Email and/or Password cannot be blank"})
        try:
            user = User.objects.get(email=request.POST['email'])
            badPassword = (user.password != request.POST['password'])
        except:
            noUser = True

        if noUser:
            return render(request, "login.html", {"message": "No User with this Email"})
        elif badPassword:
            return render(request,"login.html",{"message":"Incorrect Password"})
        else:
            request.session["id"] = user.id
            return redirect("/home/")

class Home(View):
    def get(self, request):
        return render(request, 'home.html')
    def post(self, request):
        return render(request, 'home.html')