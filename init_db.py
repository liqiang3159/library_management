from rooms.models import Hotel, RoomType, Room
from accounts.models import User

# 酒店信息
Hotel.objects.create(name="测试酒店", address="北京市朝阳区测试路1号", phone="010-12345678")

# 房型
rt1 = RoomType.objects.create(name="标准大床房", capacity=2, bed_type="大床", area="25m2", daily_price=288, member_price=258, weekend_price=328, facilities="WiFi、空调、电视", has_breakfast=True, sort_order=1)
rt2 = RoomType.objects.create(name="豪华双床房", capacity=2, bed_type="双床", area="35m2", daily_price=388, member_price=348, weekend_price=428, facilities="WiFi、空调、电视、浴缸", has_breakfast=True, sort_order=2)
rt3 = RoomType.objects.create(name="商务套房", capacity=2, bed_type="大床", area="50m2", daily_price=588, member_price=528, weekend_price=628, facilities="WiFi、空调、电视、浴缸、客厅", has_breakfast=True, sort_order=3)

# 房间
for i in range(1, 4):
    Room.objects.create(room_number=f"10{i:02d}", floor="1F", room_type=rt1)
    Room.objects.create(room_number=f"20{i:02d}", floor="2F", room_type=rt2)
    Room.objects.create(room_number=f"30{i:02d}", floor="3F", room_type=rt3)

# 管理员
User.objects.create_superuser(username="admin", password="admin123", phone="13800000001", role="super_admin", real_name="系统管理员")

# 清洁工
User.objects.create_user(username="cleaner", password="cleaner123", phone="13800000002", role="housekeeping", real_name="保洁员小王")

print("初始化数据创建完成！")
print("管理员: admin / admin123")
print("清洁工: cleaner / cleaner123")