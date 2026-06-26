
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('front_desk', '前台员工'),
        ('housekeeping', '保洁员工'),
        ('finance', '财务人员'),
    ]
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='front_desk', verbose_name='角色')
    real_name = models.CharField(max_length=50, blank=True, verbose_name='真实姓名')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    login_failed_count = models.IntegerField(default=0, verbose_name='登录失败次数')
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name='锁定截至时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'employee'
        verbose_name = '员工'
        verbose_name_plural = '员工'

    def __str__(self):
        return f'{self.username}({self.get_role_display()})'


class Customer(models.Model):
    LEVEL_CHOICES = [
        ('normal', '普通会员'),
        ('silver', '银卡会员'),
        ('gold', '金卡会员'),
        ('diamond', '钻石会员'),
    ]
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    real_name = models.CharField(max_length=50, blank=True, verbose_name='真实姓名')
    id_card = models.CharField(max_length=18, blank=True, verbose_name='身份证号')
    member_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='normal', verbose_name='会员等级')
    points = models.IntegerField(default=0, verbose_name='积分')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='消费总额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    class Meta:
        db_table = 'customer'
        verbose_name = '客户'
        verbose_name_plural = '客户'

    def __str__(self):
        return f'{self.real_name or self.phone}'


class OperationLog(models.Model):
    ACTION_CHOICES = [
        ('login', '登录'),
        ('create', '新增'),
        ('update', '修改'),
        ('delete', '删除'),
        ('audit', '审核'),
        ('settle', '结算'),
    ]
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    content = models.TextField(verbose_name='操作内容')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']


class PointsRecord(models.Model):
    TYPE_CHOICES = [
        ('earn', '获取'),
        ('redeem', '兑换'),
        ('expire', '过期'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    change_amount = models.IntegerField(verbose_name='积分变动')
    change_type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='变动类型')
    remaining = models.IntegerField(verbose_name='剩余积分')
    description = models.CharField(max_length=200, blank=True, verbose_name='说明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='变动时间')

    class Meta:
        db_table = 'points_record'
        verbose_name = '积分记录'
        verbose_name_plural = '积分记录'
