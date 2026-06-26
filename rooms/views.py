from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Hotel, RoomType, Room

def is_super_admin(user):
    return user.is_authenticated and user.role == "super_admin"

@login_required
def hotel_config(request):
    hotel, _ = Hotel.objects.get_or_create(id=1, defaults={"name": "我的酒店"})
    is_admin = request.user.role == "super_admin"
    if request.method == "POST" and is_admin:
        hotel.name = request.POST.get("name", hotel.name)
        hotel.address = request.POST.get("address", hotel.address)
        hotel.phone = request.POST.get("phone", hotel.phone)
        hotel.business_hours = request.POST.get("business_hours", hotel.business_hours)
        hotel.overtime_hourly_rate = request.POST.get("overtime_hourly_rate", hotel.overtime_hourly_rate)
        hotel.holiday_surcharge_rate = request.POST.get("holiday_surcharge_rate", hotel.holiday_surcharge_rate)
        hotel.deposit_amount = request.POST.get("deposit_amount", hotel.deposit_amount)
        if "logo" in request.FILES:
            hotel.logo = request.FILES["logo"]
        hotel.save()
        messages.success(request, "酒店信息已更新")
        return redirect("hotel_config")
    return render(request, "rooms/hotel_config.html", {"hotel": hotel, "is_admin": is_admin})

@login_required
def room_type_list(request):
    types = RoomType.objects.all().order_by("sort_order")
    is_admin = request.user.role == "super_admin"
    return render(request, "rooms/room_type_list.html", {"types": types, "is_admin": is_admin})

@login_required
@user_passes_test(is_super_admin)
def room_type_create(request):
    if request.method == "POST":
        rt = RoomType(
            name=request.POST["name"], capacity=request.POST["capacity"],
            bed_type=request.POST["bed_type"], area=request.POST.get("area", ""),
            facilities=request.POST.get("facilities", ""),
            has_breakfast=request.POST.get("has_breakfast") == "on",
            description=request.POST.get("description", ""),
            daily_price=request.POST["daily_price"],
            member_price=request.POST.get("member_price", 0),
            weekend_price=request.POST.get("weekend_price", 0),
            holiday_price=request.POST.get("holiday_price", 0),
            long_stay_discount=request.POST.get("long_stay_discount", 0.9),
            sort_order=request.POST.get("sort_order", 0)
        )
        if "image" in request.FILES:
            rt.image = request.FILES["image"]
        rt.save()
        messages.success(request, "房型创建成功")
        return redirect("room_type_list")
    return render(request, "rooms/room_type_form.html")

@login_required
@user_passes_test(is_super_admin)
def room_type_edit(request, pk):
    rt = get_object_or_404(RoomType, pk=pk)
    if request.method == "POST":
        rt.name = request.POST["name"]
        rt.capacity = request.POST["capacity"]
        rt.bed_type = request.POST["bed_type"]
        rt.area = request.POST.get("area", "")
        rt.facilities = request.POST.get("facilities", "")
        rt.has_breakfast = request.POST.get("has_breakfast") == "on"
        rt.description = request.POST.get("description", "")
        rt.daily_price = request.POST["daily_price"]
        rt.member_price = request.POST.get("member_price", 0)
        rt.weekend_price = request.POST.get("weekend_price", 0)
        rt.holiday_price = request.POST.get("holiday_price", 0)
        rt.long_stay_discount = request.POST.get("long_stay_discount", 0.9)
        rt.sort_order = request.POST.get("sort_order", 0)
        rt.is_active = request.POST.get("is_active") == "on"
        if "image" in request.FILES:
            rt.image = request.FILES["image"]
        rt.save()
        messages.success(request, "房型更新成功")
        return redirect("room_type_list")
    return render(request, "rooms/room_type_form.html", {"type": rt})

@login_required
def room_list(request):
    rooms = Room.objects.select_related("room_type").all().order_by("room_number")
    sf = request.GET.get("status", "")
    if sf:
        rooms = rooms.filter(status=sf)
    paginator = Paginator(rooms, 20)
    page = request.GET.get("page", 1)
    return render(request, "rooms/room_list.html", {
        "rooms": paginator.get_page(page), "status_filter": sf,
        "status_choices": Room.STATUS_CHOICES
    })

@login_required
@user_passes_test(is_super_admin)
def room_create(request):
    if request.method == "POST":
        room = Room(
            room_number=request.POST["room_number"],
            floor=request.POST["floor"],
            room_type_id=request.POST["room_type"],
            status=request.POST.get("status", "available"),
            is_bookable=request.POST.get("is_bookable") == "on",
            facilities_status=request.POST.get("facilities_status", "正常"),
            description=request.POST.get("description", "")
        )
        room.save()
        messages.success(request, "房间创建成功")
        return redirect("room_list")
    types = RoomType.objects.filter(is_active=True)
    return render(request, "rooms/room_form.html", {"types": types, "status_choices": Room.STATUS_CHOICES})

@login_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    is_admin = request.user.role == "super_admin"
    if request.method == "POST" and is_admin:
        room.room_number = request.POST["room_number"]
        room.floor = request.POST["floor"]
        room.room_type_id = request.POST["room_type"]
        room.status = request.POST.get("status", room.status)
        room.is_bookable = request.POST.get("is_bookable") == "on"
        room.facilities_status = request.POST.get("facilities_status", room.facilities_status)
        room.description = request.POST.get("description", "")
        room.save()
        messages.success(request, "更新成功")
        return redirect("room_list")
    types = RoomType.objects.filter(is_active=True)
    return render(request, "rooms/room_form.html", {
        "room": room, "types": types, "is_admin": is_admin, "status_choices": Room.STATUS_CHOICES
    })

@login_required
def room_status_update(request, pk):
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限")
        return redirect("room_list")
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status:
            room.status = new_status
            room.save()
        messages.success(request, "房态已更新")
        return redirect("room_list")
    return render(request, "rooms/room_status_update.html", {"room": room, "status_choices": Room.STATUS_CHOICES})
