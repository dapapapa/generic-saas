from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = (
            "mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 "
            "text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 "
            "focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
        )
        for field in self.fields.values():
            field.widget.attrs.update({"class": input_classes})

