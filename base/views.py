from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Abstract, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rest_framework import generics, mixins, permissions, authentication
from .serializers import AbstractSerializer, MessageSerializer, UserSerializer, TopicSerializer


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.add_message(request, messages.ERROR, "User Does Not Exist")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist")
    context = {'page': page}
    return render(request, "login_register.html", context)


def logout_user(request):
    logout(request)
    return redirect("home")


def register_user(request):
    form = MyUserCreateForm()

    if request.method == "POST":
        form = MyUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")
    return render(request, 'login_register.html', {'form': form})


# Create your views here.
def home(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""
    rooms = Abstract.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'home.html', context)


def room(request, pk):
    room = Abstract.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, "room.html", context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_message': room_message}
    return render(request, "profile.html", context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Abstract.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, "room_form.html", context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Abstract.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, "room_form.html", context)


@login_required(login_url='login')
def delete_room(request, pk):
    room = Abstract.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "delete.html", {'obj': room})


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed to edit here!!")
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "delete.html", {'obj': message})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'update-user.html', {'form': form})


def topics_page(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'topics.html', {'topics': topics})


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, 'activity.html', {'room_messages': room_messages})





class AbstractListCreateAPIView(generics.ListCreateAPIView):
    queryset = Abstract.objects.all()
    serializer_class = AbstractSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # print(serializer.validated_data)


abstract_list_create_view = AbstractListCreateAPIView.as_view()


class AbstractDetailView(generics.RetrieveAPIView):
    queryset = Abstract.objects.all()
    serializer_class = AbstractSerializer
    # lookup_field = pk


abstract_detail_view = AbstractDetailView.as_view()


class AbstractUpdateAPIView(generics.UpdateAPIView):
    queryset = Abstract.objects.all()
    serializer_class = AbstractSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()


abstract_update_view = AbstractUpdateAPIView.as_view()


class AbstractDeleteAPIView(generics.DestroyAPIView):
    queryset = Abstract.objects.all()
    serializer_class = AbstractSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


abstract_delete_view = AbstractDeleteAPIView.as_view()


# TOPICS API VIEW
class TopicListCreateAPIView(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()


topic_list_create_view = TopicListCreateAPIView.as_view()


class TopicDetailView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    # lookup_field = pk


topic_detail_view = TopicDetailView.as_view()


class TopicUpdateAPIView(generics.UpdateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()


topic_update_view = TopicUpdateAPIView.as_view()


class TopicDeleteAPIView(generics.DestroyAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


topic_delete_view = TopicDeleteAPIView.as_view()


# USERS API VIEW
class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()


user_list_create_view = UserListCreateAPIView.as_view()


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = pk


user_detail_view = UserDetailView.as_view()


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        instance = serializer.save()


user_update_view = UserUpdateAPIView.as_view()


class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


user_delete_view = UserDeleteAPIView.as_view()


# MESSAGE API VIEW
class MessageListCreateAPIView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()


message_list_create_view = MessageListCreateAPIView.as_view()


class MessageDetailView(generics.RetrieveAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    # lookup_field = pk


message_detail_view = MessageDetailView.as_view()


class MessageDeleteAPIView(generics.DestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        super().perform_destroy(instance)


message_delete_view = MessageDeleteAPIView.as_view()
