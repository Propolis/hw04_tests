from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Group, User
from .forms import PostForm

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
    form = PostForm(request.POST or None)
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
        instance=post,
        files=request.FILES or None,
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    else:
        return render(request, template, {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related("author")
    context = make_page_obj(request, post_list)
    context["author"] = author
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    num_pages = post.author.posts.count()
    context = {
        "post": post,
        "num_pages": num_pages,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)
