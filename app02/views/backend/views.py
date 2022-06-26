from django.shortcuts import render


def backend(request):
    return render(request, 'backend/app02/main.html')