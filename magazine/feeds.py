import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Article


class LatestArticlesFeed(Feed):
    title = 'Our magazine'
    link = reverse_lazy('magazine:article_list')
    description = 'New articles of our magazine.'
    
    def items(self):
        return Article.published_objects.all()[:5]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)
    
    def item_pubdate(self, item):
        return item.published