from django.core.management.base import BaseCommand
from accounts.models import User
from rooms.models import Hotel

class Command(BaseCommand):
    help = "初始化酒店管理系统基础数据"

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", password="admin123",
                real_name="超级管理员", phone="13800000000", role="super_admin"
            )
            self.stdout.write(self.style.SUCCESS("超级管理员创建成功: admin / admin123"))

        if not User.objects.filter(username="front").exists():
            User.objects.create_user(
                username="front", password="front123",
                real_name="前台张三", phone="13800000001", role="front_desk"
            )
            self.stdout.write(self.style.SUCCESS("前台员工创建成功: front / front123"))

        if not User.objects.filter(username="clean").exists():
            User.objects.create_user(
                username="clean", password="clean123",
                real_name="保洁李四", phone="13800000002", role="housekeeping"
            )
            self.stdout.write(self.style.SUCCESS("保洁员工创建成功: clean / clean123"))

        Hotel.objects.get_or_create(id=1, defaults={
            "name": "示例酒店", "address": "北京市朝阳区xxx路88号",
            "phone": "010-88888888"
        })
        self.stdout.write(self.style.SUCCESS("初始化完成！"))
