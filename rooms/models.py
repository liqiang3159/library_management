from django.db import models

class Hotel(models.Model):
    name = models.CharField(max_length=100, verbose_name='酒店名称')
    address = models.CharField(max_length=200, verbose_name='地址')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    business_hours = models.CharField(max_length=50, default='全天', verbose_name='营业时间')
    logo = models.ImageField(upload_to='hotel/', blank=True, verbose_name='门店LOGO')
    check_in_time = models.TimeField(default='14:00', verbose_name='默认入住时间')
    check_out_time = models.TimeField(default='12:00', verbose_name='默认退房时间')
    overtime_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=50, verbose_name='超时每小时加收')
    holiday_surcharge_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.3, verbose_name='节假日溢价比例')
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2, default=200, verbose_name='默认押金')

    class Meta:
        db_table = 'hotel'
        verbose_name = '酒店信息'
        verbose_name_plural = '酒店信息'

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=50, verbose_name='房型名称')
    capacity = models.IntegerField(default=2, verbose_name='容纳人数')
    bed_type = models.CharField(max_length=50, verbose_name='床型')
    area = models.CharField(max_length=20, blank=True, verbose_name='面积')
    facilities = models.TextField(blank=True, verbose_name='配套设施')
    has_breakfast = models.BooleanField(default=False, verbose_name='含早餐')
    description = models.TextField(blank=True, verbose_name='介绍')
    image = models.ImageField(upload_to='room_types/', blank=True, verbose_name='展示图')
    daily_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='日常价')
    member_price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='会员价')
    weekend_price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='周末价')
    holiday_price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='节假日价')
    long_stay_discount = models.DecimalField(max_digits=3, decimal_places=2, default=0.9, verbose_name='长住折扣')
    sort_order = models.IntegerField(default=0, verbose_name='排序权重')
    is_active = models.BooleanField(default=True, verbose_name='启用')

    class Meta:
        db_table = 'room_type'
        verbose_name = '房型'
        verbose_name_plural = '房型'

    def __str__(self):
        return self.name


class Room(models.Model):
    STATUS_CHOICES = [
        ('available', '空房'),
        ('booked', '已预订'),
        ('occupied', '入住中'),
        ('dirty', '脏房'),
        ('maintenance', '维修中'),
        ('reserved', '预留'),
        ('paused', '停用'),
    ]
    room_number = models.CharField(max_length=10, unique=True, verbose_name='房号')
    floor = models.CharField(max_length=10, verbose_name='楼层')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, verbose_name='房型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='房间状态')
    is_bookable = models.BooleanField(default=True, verbose_name='可预订')
    facilities_status = models.TextField(default='正常', verbose_name='设施状态')
    description = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        db_table = 'room'
        verbose_name = '客房'
        verbose_name_plural = '客房'

    def __str__(self):
        return f'{self.room_number}({self.room_type.name})'
