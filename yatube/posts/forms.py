from django import forms
from .models import Post, Group


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label="Текст",
        required=True
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Группа"
    )

    class Meta:
        model = Post
        fields = ("text", "group")

    def clean_text(self):
        data = self.cleaned_data['text']
        if data.replace(" ", "") == "":
            raise forms.ValidationError('Это поле должно быть заполнено.')
        return data
