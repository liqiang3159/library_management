from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from .models import User, Customer, OperationLog, PointsRecord
from orders.models import Order

def is_super_admin(user):
    return user.is_authenticated and user.role == 'super_admin'

def is_front_desk(user):
    return user.is_authenticated and user.role in ['super_admin', 'front_desk']

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(request, '账号已被禁用')
                return render(request, 'accounts/login.html')
            if user.locked_until and user.locked_until > timezone.now():
                messages.error(request, '账号已被锁定，请稍后再试')
                return render(request, 'accounts/login.html')
            login(request, user)
            user.login_failed_count = 0
            user.locked_until = None
            user.save()
            OperationLog.objects.create(operator=user, action_type='login', content='登录系统')
            return redirect('dashboard')
        else:
            try:
                u = User.objects.get(username=username)
                u.login_failed_count += 1
                if u.login_failed_count >= 5:
                    u.locked_until = timezone.now() + timezone.timedelta(minutes=30)
                u.save()
            except User.DoesNotExist:
                pass
            messages.error(request, '用户名或密码错误')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    from rooms.models import Room, RoomType
    from orders.models import Order, CleaningTask
    context = {
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(status='available').count(),
        'occupied_rooms': Room.objects.filter(status='occupied').count(),
        'booked_rooms': Room.objects.filter(status='booked').count(),
        'dirty_rooms': Room.objects.filter(status='dirty').count(),
        'maintenance_rooms': Room.objects.filter(status='maintenance').count(),
        'today_orders': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'pending_tasks': CleaningTask.objects.filter(status='pending').count(),
        'total_room_types': RoomType.objects.count(),
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
@user_passes_test(is_super_admin)
def employee_list(request):
    employees = User.objects.all().order_by('-created_at')
    paginator = Paginator(employees, 20)
    page = request.GET.get('page', 1)
    return render(request, 'accounts/employee_list.html', {'employees': paginator.get_page(page)})

@login_required
@user_passes_test(is_super_admin)
def employee_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        real_name = request.POST.get('real_name')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        if User.objects.filter(username=username).exists():
            messages.error(request, '账号已存在')
            return render(request, 'accounts/employee_form.html')
        user = User.objects.create_user(username=username, password=password, real_name=real_name, phone=phone, role=role)
        OperationLog.objects.create(operator=request.user, action_type='create', content=f'新增员工:{username}')
        messages.success(request, '员工创建成功')
        return redirect('employee_list')
    return render(request, 'accounts/employee_form.html')

@login_required
@user_passes_test(is_super_admin)
def employee_edit(request, pk):
    employee = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        employee.real_name = request.POST.get('real_name', employee.real_name)
        employee.phone = request.POST.get('phone', employee.phone)
        employee.role = request.POST.get('role', employee.role)
        is_active = request.POST.get('is_active')
        employee.is_active = is_active == 'on'
        new_password = request.POST.get('password')
        if new_password:
            employee.set_password(new_password)
        employee.save()
        OperationLog.objects.create(operator=request.user, action_type='update', content=f'编辑员工:{employee.username}')
        messages.success(request, '更新成功')
        return redirect('employee_list')
    return render(request, 'accounts/employee_form.html', {'employee': employee})

@login_required
@user_passes_test(is_super_admin)
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    paginator = Paginator(customers, 20)
    page = request.GET.get('page', 1)
    return render(request, 'accounts/customer_list.html', {'customers': paginator.get_page(page)})

@login_required
@user_passes_test(is_super_admin)
def operation_log_list(request):
    logs = OperationLog.objects.all()
    action = request.GET.get('action_type', '')
    search = request.GET.get('search', '')
    if action:
        logs = logs.filter(action_type=action)
    if search:
        logs = logs.filter(content__icontains=search)
    paginator = Paginator(logs, 30)
    page = request.GET.get('page', 1)
    return render(request, 'accounts/log_list.html', {'logs': paginator.get_page(page)})
