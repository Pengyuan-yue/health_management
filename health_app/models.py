from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    用户个人信息模型
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)  #  修改： 添加了 blank=True
    birth_date = models.DateField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # 单位：米
    weight = models.FloatField(null=True, blank=True)  # 单位：公斤
    gender_choices = (
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    )
    gender = models.CharField(max_length=1, choices=gender_choices, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)

class HealthData(models.Model):
    """
    用户健康数据模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.FloatField(null=True, blank=True)  # 单位：公斤
    blood_pressure_sys = models.IntegerField(null=True, blank=True)  # 收缩压
    blood_pressure_dia = models.IntegerField(null=True, blank=True)  # 舒张压
    steps = models.IntegerField(null=True, blank=True)  # 步数
    heart_rate = models.IntegerField(null=True, blank=True)  # 心率
    blood_sugar = models.FloatField(null=True, blank=True)  # 血糖