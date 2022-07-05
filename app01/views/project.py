from django.shortcuts import render


def project_list(request):
    return render(request, 'app01/project_list.html')