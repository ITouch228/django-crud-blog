from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title or title.strip() == "":
            raise forms.ValidationError("Заголовок не может быть пустым.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if not content or len(content.strip()) < 10:
            raise forms.ValidationError(
                "Содержание должно содержать не менее 10 символов."
            )
        return content
