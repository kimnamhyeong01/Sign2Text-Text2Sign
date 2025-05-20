from django.db import models

class SignVideo(models.Model):
    gloss = models.CharField(max_length=45)
    sign_video_url = models.TextField()
    sign_description = models.TextField()
    sign_images = models.TextField()

    class Meta:
        managed = False  # 마이그레이션으로 관리하지 않음
        db_table = 'sign_video'
