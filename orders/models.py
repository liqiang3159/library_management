from django.db import models
from accounts.models import Customer, User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('booked', '已预订'),
        ('waiting', '待入住'),
        ('in_stay', '在店中'),
        ('extended', '已续住'),
        ('settling', '待结算'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
        ('abnormal', '异常'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name='客户')
    room = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, verbose_name='房间')
    check_in = models.DateTimeField(verbose_name='入住时间')
    check_out = models.DateTimeField(verbose_name='退房时间')
    actual_check_in = models.DateTimeField(null=True, blank=True, verbose_name='实际入住')
    actual_check_out = models.DateTimeField(null=True, blank=True, verbose_name='实际退房')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    room_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='房费')
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='押金')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='优惠金额')
    points_used = models.IntegerField(default=0, verbose_name='使用积分')
    total_consumption = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='额外消费')
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='实付金额')
    guest_count = models.IntegerField(default=1, verbose_name='入住人数')
    guest_names = models.TextField(blank=True, verbose_name='同住人')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='取消时间')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作员工')

    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f'订单{self.id}-{self.customer.phone}'


class ConsumptionBill(models.Model):
    TYPE_CHOICES = [
        ('dining', '餐饮'),
        ('goods', '日用品'),
        ('laundry', '洗衣'),
        ('entertainment', '棋牌'),
        ('other', '其他'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')
    bill_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='消费类型')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    description = models.CharField(max_length=200, blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='消费时间')

    class Meta:
        db_table = 'consumption_bill'
        verbose_name = '消费账单'
        verbose_name_plural = '消费账单'


class CleaningTask(models.Model):
    STATUS_CHOICES = [
        ('pending', '待清洁'),
        ('cleaning', '清洁中'),
        ('cleaned', '已清洁'),
        ('reviewing', '待复检'),
        ('completed', '已完成'),
        ('issue', '问题上报'),
    ]
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, verbose_name='房间')
    cleaner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'housekeeping'}, verbose_name='保洁员')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name='任务状态')
    priority = models.IntegerField(default=0, verbose_name='优先级')
    check_out_time = models.DateTimeField(null=True, blank=True, verbose_name='退房时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    inspection_photo = models.ImageField(upload_to='inspection/', blank=True, verbose_name='巡检照片')
    issue_description = models.TextField(blank=True, verbose_name='问题描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'cleaning_task'
        verbose_name = '清洁任务'
        verbose_name_plural = '清洁任务'
        ordering = ['-priority', '-created_at']
