from django.forms import ModelForm
from .models import Abstract, User
from django.contrib.auth.forms import UserCreationForm


class MyUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'course', 'reg_number', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Abstract
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email']
