from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from ..models import Post


register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published_objects.count()


@register.inclusion_tag('blog/post/featured_posts.html')
def show_featured_posts(count=5):
    latest_posts = Post.published_objects.order_by('-published')[:count]
    most_commented_posts = Post.published_objects.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
    return {'latest_posts': latest_posts, 'most_commented_posts': most_commented_posts}


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.filter
def modulo(num, val):
    return num % val