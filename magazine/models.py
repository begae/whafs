from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Article.Status.PUBLISHED)


class Article(models.Model):
    
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    body = models.TextField()
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status, default=Status.DRAFT)
    tags = TaggableManager()
    users_liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='articles_liked', blank=True)

    objects = models.Manager()
    published_objects = PublishedManager()

    class Meta:
        ordering = ['-published']
        indexes = [models.Index(fields=['-published']),]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("magazine:article_detail", args=[self.id, self.slug])
    

class Comment(models.Model):
    on_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    by_name = models.CharField(max_length=80)
    by_email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created']),]

    def __str__(self):
        return f'Comment on {self.on_article} by {self.by_name}'