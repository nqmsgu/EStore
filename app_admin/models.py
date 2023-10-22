from django.db import models
from django.contrib.auth.models import User

class UserProfileInfo(models.Model):
    user=models.OneToOneField(User,on_delete=models.PROTECT)
    portfolio=models.URLField(blank=True,null=True)
    image=models.ImageField(upload_to='user/',default='user/no_avatar.png')

    def __str__(self) -> str:
        return self.user.username

