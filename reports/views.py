from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
from orders.models import Order
from rooms.models import Room

@login_required
def revenue_report(request):
    today = timezone.now().date()
    start = request.GET.get("start", str(today))
    end = request.GET.get("end", str(today))
    orders = Order.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
    total_revenue = orders.filter(status="completed").aggregate(s=Sum("final_amount"))["s"] or 0
    total_orders = orders.count()
    completed = orders.filter(status="completed").count()
    cancelled = orders.filter(status="cancelled").count()
    refunded = orders.filter(status="refunded").count()
    return render(request, "reports/revenue.html", {
        "total_revenue": total_revenue, "total_orders": total_orders,
        "completed": completed, "cancelled": cancelled, "refunded": refunded,
        "start": start, "end": end
    })

@login_required
def room_report(request):
    rooms = Room.objects.all()
    total = rooms.count()
    stats = {s[0]: rooms.filter(status=s[0]).count() for s in Room.STATUS_CHOICES}
    occupancy_rate = (stats.get("occupied", 0) + stats.get("booked", 0)) / max(total, 1) * 100
    return render(request, "reports/room.html", {
        "total": total, "stats": stats, "occupancy_rate": round(occupancy_rate, 1),
        "status_choices": Room.STATUS_CHOICES
    })

@login_required
def order_report(request):
    today = timezone.now().date()
    start = request.GET.get("start", str(today))
    end = request.GET.get("end", str(today))
    orders = Order.objects.filter(created_at__date__gte=start, created_at__date__lte=end)
    status_counts = {s[0]: orders.filter(status=s[0]).count() for s in Order.STATUS_CHOICES[:7]}
    return render(request, "reports/order.html", {
        "status_counts": status_counts, "total": orders.count(),
        "start": start, "end": end, "status_choices": Order.STATUS_CHOICES[:7]
    })
