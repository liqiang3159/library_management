from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum, Q
from .models import Order, ConsumptionBill, CleaningTask
from rooms.models import Room
from accounts.models import Customer

@login_required
def order_list(request):
    orders = Order.objects.select_related("customer", "room").all().order_by("-created_at")
    sf = request.GET.get("status", "")
    search = request.GET.get("search", "")
    if sf:
        orders = orders.filter(status=sf)
    if search:
        orders = orders.filter(Q(customer__phone__icontains=search) | Q(customer__real_name__icontains=search) | Q(id__icontains=search))
    paginator = Paginator(orders, 20)
    page = request.GET.get("page", 1)
    return render(request, "orders/order_list.html", {
        "orders": paginator.get_page(page), "status_filter": sf, "search": search,
        "status_choices": Order.STATUS_CHOICES
    })

@login_required
def order_create(request):
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限"); return redirect("order_list")
    if request.method == "POST":
        phone = request.POST.get("phone")
        customer, _ = Customer.objects.get_or_create(phone=phone, defaults={"real_name": request.POST.get("real_name", "")})
        room = get_object_or_404(Room, pk=request.POST["room_id"])
        check_in = timezone.datetime.strptime(request.POST["check_in"], "%Y-%m-%dT%H:%M")
        check_out = timezone.datetime.strptime(request.POST["check_out"], "%Y-%m-%dT%H:%M")
        nights = max(1, (check_out - check_in).days)
        room_fee = float(room.room_type.daily_price) * nights
        deposit = float(request.POST.get("deposit", 200))
        order = Order.objects.create(
            customer=customer, room=room, check_in=check_in, check_out=check_out,
            room_fee=room_fee, deposit=deposit, final_amount=room_fee + deposit,
            guest_count=request.POST.get("guest_count", 1),
            guest_names=request.POST.get("guest_names", ""),
            remark=request.POST.get("remark", ""), status="booked",
            operator=request.user
        )
        room.status = "booked"; room.save()
        messages.success(request, f"订单 {order.id} 创建成功")
        return redirect("order_list")
    rooms = Room.objects.filter(status="available", is_bookable=True).select_related("room_type")
    return render(request, "orders/order_form.html", {"rooms": rooms})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related("customer", "room", "operator"), pk=pk)
    bills = ConsumptionBill.objects.filter(order=order)
    return render(request, "orders/order_detail.html", {"order": order, "bills": bills})

@login_required
def order_check_in(request, pk):
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限"); return redirect("order_detail", pk=pk)
    order = get_object_or_404(Order, pk=pk)
    if order.status in ["booked", "waiting"]:
        order.status = "in_stay"
        order.actual_check_in = timezone.now()
        order.save()
        if order.room:
            order.room.status = "occupied"; order.room.save()
        messages.success(request, "入住办理成功")
    return redirect("order_detail", pk=pk)

@login_required
def order_check_out(request, pk):
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限"); return redirect("order_detail", pk=pk)
    order = get_object_or_404(Order, pk=pk)
    if order.status in ["in_stay", "extended"]:
        order.actual_check_out = timezone.now()
        order.status = "settling"
        order.save()
        return redirect("order_settle", pk=pk)
    messages.error(request, "当前状态不可退房")
    return redirect("order_detail", pk=pk)

@login_required
def order_settle(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限"); return redirect("order_detail", pk=pk)
    bills = ConsumptionBill.objects.filter(order=order)
    if request.method == "POST":
        total = float(order.room_fee) + float(order.total_consumption) - float(order.discount)
        order.final_amount = max(0, total)
        order.status = "completed"
        order.save()
        if order.room:
            order.room.status = "dirty"
            order.room.save()
            CleaningTask.objects.create(room=order.room, check_out_time=timezone.now())
        if order.customer:
            order.customer.total_spent += order.final_amount
            order.customer.points += int(order.final_amount)
            order.customer.save()
        if float(order.deposit) > float(order.final_amount):
            messages.success(request, f"结算完成，退还押金 {(float(order.deposit) - float(order.final_amount)):.2f} 元")
        else:
            messages.success(request, "结算完成")
        return redirect("order_detail", pk=pk)
    total_consumption = sum(float(b.amount) for b in bills)
    order.total_consumption = total_consumption; order.save()
    return render(request, "orders/order_settle.html", {"order": order, "bills": bills})

@login_required
def order_cancel(request, pk):
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限"); return redirect("order_detail", pk=pk)
    order = get_object_or_404(Order, pk=pk)
    if order.status in ["pending", "booked", "waiting"]:
        order.status = "cancelled"
        order.cancelled_at = timezone.now()
        order.save()
        if order.room:
            order.room.status = "available"; order.room.save()
        messages.success(request, "订单已取消")
    return redirect("order_detail", pk=pk)

@login_required
def add_consumption(request, pk):
    if request.user.role not in ["super_admin", "front_desk"]:
        messages.error(request, "无权限"); return redirect("order_detail", pk=pk)
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        ConsumptionBill.objects.create(
            order=order, bill_type=request.POST["bill_type"],
            amount=request.POST["amount"], description=request.POST.get("description", "")
        )
        messages.success(request, "消费记录已添加")
    return redirect("order_detail", pk=pk)

@login_required
def cleaning_list(request):
    if request.user.role not in ["super_admin", "housekeeping"]:
        messages.error(request, "无权限"); return redirect("dashboard")
    tasks = CleaningTask.objects.select_related("room", "cleaner").all().order_by("-priority", "-created_at")
    sf = request.GET.get("status", "")
    if sf: tasks = tasks.filter(status=sf)
    paginator = Paginator(tasks, 20)
    page = request.GET.get("page", 1)
    return render(request, "orders/cleaning_list.html", {"tasks": paginator.get_page(page), "status_filter": sf})

@login_required
def cleaning_update(request, pk):
    task = get_object_or_404(CleaningTask, pk=pk)
    if request.method == "POST":
        task.status = request.POST.get("status", task.status)
        if task.status == "cleaning": task.cleaner = request.user
        if task.status in ["cleaned", "completed"]: task.completed_at = timezone.now()
        task.issue_description = request.POST.get("issue_description", "")
        if "inspection_photo" in request.FILES:
            task.inspection_photo = request.FILES["inspection_photo"]
        task.save()
        if task.status == "completed":
            task.room.status = "available"; task.room.save()
        messages.success(request, "任务已更新")
        return redirect("cleaning_list")
    return render(request, "orders/cleaning_update.html", {"task": task})
