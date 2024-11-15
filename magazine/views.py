from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from taggit.models import Tag
from .models import Article
from .forms import EmailArticleForm, CommentForm, SearchForm


def article_list(request, tag_slug=None):
    all_articles = Article.published_objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_articles = all_articles.filter(tags__in=[tag])
    paginator = Paginator(all_articles, 5)
    page_number = request.GET.get('page', 1)
    try:
        articles = paginator.page(page_number)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    return render(request, 'magazine/article/list.html', {'articles': articles, 'tag': tag})


def article_detail(request, article_id, slug):
    article = get_object_or_404(Article, id=article_id, status=Article.Status.PUBLISHED)
    comments = article.comments.filter(active=True)
    form = CommentForm()
    article_tags_ids = article.tags.values_list('id', flat=True)
    related_articles = Article.published_objects.filter(tags__in=article_tags_ids).exclude(id=article.id)
    related_articles = related_articles.annotate(same_tags=Count('tags')).order_by('-same_tags', '-published')[:5]
    return render(request, 'magazine/article/detail.html', 
                  {'article': article, 'comments': comments, 'form': form, 'related_articles': related_articles})


def article_share(request, article_id):
    article = get_object_or_404(Article, id=article_id, status=Article.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailArticleForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            article_url = request.build_absolute_uri(article.get_absolute_url())
            subject = (f'{cd['your_name']} ({cd['your_email']}) recommends you read "{article.title}"')
            message = (f'Read "{article.title}" at {article_url}\n\n{cd['your_name']}\'s comments: {cd['comments']}')
            send_mail(subject=subject, message=message, from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailArticleForm()
    return render(request, 'magazine/article/share.html', {'article': article, 'form': form, 'sent': sent})


@require_POST
def article_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id, status=Article.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.on_article = article
        comment.save()
    return render(request, 'magazine/article/comment.html', {'article': article, 'form': form, 'comment': comment})


@login_required
@require_POST
def article_like(request):
    article_id = request.POST.get('id')
    action = request.POST.get('action')
    if article_id and action:
        try:
            article = Article.published_objects.get(id=article_id)
            if action == 'Like':
                article.users_liked.add(request.user)
            else:
                article.users_liked.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Article.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


def article_search(request):
    form = SearchForm()
    keywords = None
    results = []
    if 'keywords' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_keywords = SearchQuery(keywords)
            results = Article.published_objects.annotate(
                search=search_vector, 
                rank=SearchRank(search_vector, search_keywords)).filter(rank__gte=0.3).order_by('-rank')
    return render(request, 'magazine/article/search.html', {'form': form, 'keywords': keywords, 'results': results})