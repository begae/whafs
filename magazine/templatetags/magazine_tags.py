from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from ..models import Article


register = template.Library()


@register.simple_tag
def total_articles():
    return Article.published_objects.count()


@register.inclusion_tag('magazine/article/featured_articles.html')
def show_featured_articles(count=5):
    latest_articles = Article.published_objects.order_by('-published')[:count]
    most_commented_articles = Article.published_objects.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
    return {'latest_articles': latest_articles, 'most_commented_articles': most_commented_articles}


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.filter
def modulo(num, val):
    return num % val