from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Workspace
from .models import Project
from .forms import ProjectForm


def home(request):
    return render(request, "core/home.html")


def _workspace_for_user(user):
    workspace, _ = Workspace.objects.get_or_create(
        owner=user,
        defaults={"name": f"{user.username}'s Workspace"},
    )
    return workspace


@login_required
def dashboard(request):
    ws = _workspace_for_user(request.user)
    projects = Project.objects.filter(workspace=ws).order_by("-created_at")
    return render(request, "core/dashboard.html", {"workspace": ws, "projects": projects})


@login_required
def project_list(request):
    ws = _workspace_for_user(request.user)
    projects = Project.objects.filter(workspace=ws).order_by("-created_at")
    return render(request, "core/projects/list.html", {"workspace": ws, "projects": projects})


@login_required
def project_create(request):
    ws = _workspace_for_user(request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.workspace = ws  # <-- critical for isolation
            project.save()
            return redirect("project_list")
    else:
        form = ProjectForm()

    return render(request, "core/projects/form.html", {"form": form, "title": "New project"})


@login_required
def project_update(request, pk):
    ws = _workspace_for_user(request.user)

    # <-- critical: fetch by pk AND workspace to prevent hijacking
    project = get_object_or_404(Project, pk=pk, workspace=ws)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_list")
    else:
        form = ProjectForm(instance=project)

    return render(request, "core/projects/form.html", {"form": form, "title": "Edit project"})


@login_required
def project_delete(request, pk):
    ws = _workspace_for_user(request.user)
    project = get_object_or_404(Project, pk=pk, workspace=ws)

    if request.method == "POST":
        project.delete()
        return redirect("project_list")

    return render(request, "core/projects/confirm_delete.html", {"project": project})
