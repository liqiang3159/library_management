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
        'dirty_rooms': Room.objects.filter(status='dirty').count(),
        'today_orders': Order.objects.filter(created_at__date=timezone.now().date()).count(),
        'pending_tasks': CleaningTask.objects.filter(status='pending').count(),
        'total_customers': Customer.objects.count(),
        'total_employees': User.objects.count(),
    }
    return render(request, 'accounts/dashboard.html', context)

# ========== 员工管理 ==========

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
        User.objects.create_user(username=username, password=password, real_name=real_name, phone=phone, role=role)
        OperationLog.objects.create(operator=request.user, action_type='create', content='新增员工:' + username)
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
        employee.is_active = request.POST.get('is_active') == 'on'
        new_password = request.POST.get('password')
        if new_password:
            employee.set_password(new_password)
        employee.save()
        OperationLog.objects.create(operator=request.user, action_type='update', content='编辑员工:' + employee.username)
        messages.success(request, '更新成功')
        return redirect('employee_list')
    return render(request, 'accounts/employee_form.html', {'employee': employee})

@login_required
@user_passes_test(is_super_admin)
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk)
    username = employee.username
    employee.delete()
    OperationLog.objects.create(operator=request.user, action_type='delete', content='删除员工:' + username)
    messages.success(request, '员工已删除')
    return redirect('employee_list')

# ========== 客户管理 ==========

@login_required
@user_passes_test(is_super_admin)
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')
    paginator = Paginator(customers, 20)
    page = request.GET.get('page', 1)
    return render(request, 'accounts/customer_list.html', {'customers': paginator.get_page(page)})

@login_required
@user_passes_test(is_super_admin)
def customer_create(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, '该手机号已存在')
            return render(request, 'accounts/customer_form.html')
        c = Customer.objects.create(
            real_name=request.POST.get('real_name', ''),
            phone=phone,
            id_card=request.POST.get('id_card', ''),
            member_level=request.POST.get('member_level', 'normal'),
            points=request.POST.get('points', 0),
        )
        OperationLog.objects.create(operator=request.user, action_type='create', content='新增客户:' + (c.real_name or phone))
        messages.success(request, '客户创建成功')
        return redirect('customer_list')
    return render(request, 'accounts/customer_form.html')

@login_required
@user_passes_test(is_super_admin)
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.real_name = request.POST.get('real_name', '')
        phone = request.POST.get('phone')
        if Customer.objects.filter(phone=phone).exclude(pk=pk).exists():
            messages.error(request, '该手机号已被其他客户使用')
            return render(request, 'accounts/customer_form.html', {'customer': customer})
        customer.phone = phone
        customer.id_card = request.POST.get('id_card', '')
        customer.member_level = request.POST.get('member_level', 'normal')
        customer.points = request.POST.get('points', 0)
        customer.save()
        OperationLog.objects.create(operator=request.user, action_type='update', content='编辑客户:' + (customer.real_name or phone))
        messages.success(request, '更新成功')
        return redirect('customer_list')
    return render(request, 'accounts/customer_form.html', {'customer': customer})

@login_required
@user_passes_test(is_super_admin)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    info = customer.real_name or customer.phone
    customer.delete()
    OperationLog.objects.create(operator=request.user, action_type='delete', content='删除客户:' + info)
    messages.success(request, '客户已删除')
    return redirect('customer_list')

# ========== 操作日志 ==========

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