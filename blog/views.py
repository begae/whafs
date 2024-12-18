from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from taggit.models import Tag
from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
    all_posts = Post.published_objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags__in=[tag])
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, post_id, slug):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    related_posts = Post.published_objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    related_posts = related_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:5]
    return render(request, 'blog/post/detail.html', 
                  {'post': post, 'comments': comments, 'form': form, 'related_posts': related_posts})


@login_required
@require_POST
def post_like(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            article = Post.published_objects.get(id=post_id)
            if action == 'Like':
                article.users_liked.add(request.user)
            else:
                article.users_liked.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (f'{cd['your_name']} ({cd['your_email']}) recommends you read "{post.title}"')
            message = (f'Read "{post.title}" at {post_url}\n\n{cd['your_name']}\'s comments: {cd['comments']}')
            send_mail(subject=subject, message=message, from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.on_post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    keywords = None
    results = []
    if 'keywords' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_keywords = SearchQuery(keywords)
            results = Post.published_objects.annotate(
                search=search_vector, 
                rank=SearchRank(search_vector, search_keywords)).filter(rank__gte=0.3).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form, 'keywords': keywords, 'results': results})