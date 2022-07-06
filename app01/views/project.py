from app01.forms.project import ProjectForm
from django.http import JsonResponse


def project_list(request):
    if request.method == 'GET':
        form = ProjectForm()
        return render(request, 'app01/project_list.html', {'form': form})
    form = ProjectForm(request.POST)
    if form.is_valid():
        pass
    else:
        return JsonResponse({"status": 0, "msg": form.errors})
