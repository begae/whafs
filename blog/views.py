from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from .models import Post


def post_list(request):
    all_posts = Post.published_objects.all()
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug=slug)
    return render(request, 'blog/post/detail.html', {'post': post})