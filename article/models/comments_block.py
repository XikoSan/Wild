from django.db import models
from article.models.article import Article

# комментарии статьи, сохраненные в БД
class CommentsBlock(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)

    messages = models.TextField()

    def __str__(self):
        return str(f'Комментарии к статье {self.article.pk} "{self.article.title}"')

    # Свойства класса
    class Meta:
        verbose_name = "Блок комментариев"
        verbose_name_plural = "Блоки комментариев"
