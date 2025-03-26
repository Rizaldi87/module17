from django.contrib.auth.models import User
from django.views.generic import DetailView, View
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404

# from django.shortcuts import render, redirect

from .models import Profile
from feed.models import Post
from followers.models import Follower
from .forms import UserProfileForm


# Create your views here.
class ProfileDetailView(DetailView):
    http_method_names = ["get"]
    template_name = "profiles/detail.html"
    model = User
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.get_object()
        context = super().get_context_data(**kwargs)
        context["total_posts"] = Post.objects.filter(author=user).count()
        context["total_followers"] = Follower.objects.filter(following=user).count()
        if self.request.user.is_authenticated:
            context["you_follow"] = Follower.objects.filter(
                followed_by=self.request.user, following=user
            ).exists()
        return context


class FollowView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        if "action" not in data or "username" not in data:
            return HttpResponseBadRequest("missing data")

        try:
            other_user = User.objects.get(username=data["username"])
        except User.DoesNotExist:
            return HttpResponseBadRequest("user not found")

        if data["action"] == "follow":
            follower, created = Follower.objects.get_or_create(
                followed_by=request.user, following=other_user
            )
        else:
            try:
                follower = Follower.objects.get(
                    followed_by=request.user, following=other_user
                )
            except Follower.DoesNotExist:
                follower = None
            if follower:
                follower.delete()
        return JsonResponse(
            {
                "success": True,
                "wording": "Unfollow" if data["action"] == "follow" else "Follow",
            }
        )


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "profiles/edit.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["username"])

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = self.request.user.profile
        new_image = form.cleaned_data.get("image")

        if not new_image or new_image == profile.image:
            return response

        profile.image = new_image
        profile.save()
        return response

    def get_success_url(self):
        return reverse_lazy(
            "profiles:edit", kwargs={"username": self.request.user.username}
        )
