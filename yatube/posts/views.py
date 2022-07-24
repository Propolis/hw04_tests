from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

NUMBER_POSTS = 10


def make_page_obj(request, queryset):
    paginator = Paginator(queryset, NUMBER_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "page_obj": page_obj
    }


def index(request):
    post_list = Post.objects.select_related("author")
    context = make_page_obj(request, post_list)
    template = "posts/index.html"
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("author")
    context = make_page_obj(request, post_list)
    context["group"] = group
    template = "posts/group_list.html"
    return render(request, template, context)


@login_required()
def post_create(request):
    template = "posts/create_post.html"
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", request.user)
    return render(request, template, {"form": form})


@login_required()
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    template = "posts/create_post.html"
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    else:
        return render(request, template, {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    post_list = author.posts.select_related("author")
    context = make_page_obj(request, post_list)
    if user.is_authenticated:
        following: bool = Follow.objects.filter(user=user, author=author).exists()
    else:
        following = False
    context["author"] = author
    context["following"] = following
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    num_pages = post.author.posts.count()
    comments = post.comments.select_related("post")
    context = {
        "post": post,
        "num_pages": num_pages,
        "comments": comments,
        "form": CommentForm(),
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    follows = user.follower.all()
    auhtors_id = [follow.author.id for follow in follows]
    posts = Post.objects.filter(author_id__in=auhtors_id)
    context = make_page_obj(request, posts)
    return render(request, "posts/follow.html", context=context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author).exists()
    user_is_not_author = user == author
    if (not follow) and (not user_is_not_author):
        Follow.objects.create(user=user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = get_object_or_404(Follow, author=author, user=user)
    follow.delete()
    return redirect("posts:profile", username=username)
