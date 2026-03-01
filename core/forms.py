from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 "
                        "text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 "
                        "focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                    ),
                    "placeholder": "Project name",
                }
            )
        }
