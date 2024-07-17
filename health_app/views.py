from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, HealthData
from .forms import UserProfileForm, HealthDataForm
from datetime import datetime


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # 直接保存 user 对象
            UserProfile.objects.create(user=user) #  创建并关联 UserProfile 对象
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            # 获取表单数据
            user_profile = form.save(commit=False)

            # 打印 birth_date 数据类型
            print(f"birth_date type: {type(user_profile.birth_date)}")
            print(f"birth_date value: {user_profile.birth_date}")

            # 转换日期为字符串
            birth_date = form.cleaned_data['birth_date']
            user_profile.birth_date = birth_date

            # 保存用户资料
            user_profile.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'profile.html', {'profile_form': form})

@login_required
def data(request):
    user_profile = request.user.userprofile # 获取用户个人信息

    #  检查是否填写了身高信息
    if user_profile.height is None:
        return render(request, 'data.html', {'profile_incomplete': True}) #  传递 profile_incomplete 变量给模板

    # 如果填写了身高信息，则继续执行原来的逻辑
    health_data = HealthData.objects.filter(user=request.user).order_by('-date')
    if request.method == 'POST':
        form = HealthDataForm(request.POST)
        if form.is_valid():
            new_data = form.save(commit=False)
            new_data.user = request.user
            new_data.save()

            # 设置 Cookie
            response = redirect('data')
            response.set_cookie('last_date', new_data.date.strftime('%Y-%m-%d'))
            response.set_cookie('last_weight', new_data.weight)
            response.set_cookie('last_blood_pressure_sys', new_data.blood_pressure_sys)
            response.set_cookie('last_blood_pressure_dia', new_data.blood_pressure_dia)
            response.set_cookie('last_steps', new_data.steps)
            response.set_cookie('last_heart_rate', new_data.heart_rate)
            response.set_cookie('last_blood_sugar', new_data.blood_sugar)

            return response  # 返回重定向响应
    else:
        # 获取 Cookie 中的数据
        initial_data = {
            'date': request.COOKIES.get('last_date'),
            'weight': request.COOKIES.get('last_weight'),
            'blood_pressure_sys': request.COOKIES.get('last_blood_pressure_sys'),
            'blood_pressure_dia': request.COOKIES.get('last_blood_pressure_dia'),
            'steps': request.COOKIES.get('last_steps'),
            'heart_rate': request.COOKIES.get('last_heart_rate'),
            'blood_sugar': request.COOKIES.get('last_blood_sugar'),
        }
        form = HealthDataForm(request.POST or None, initial=initial_data)

        # 健康评估和提示
        if request.user.is_authenticated:
            latest_health_data = HealthData.objects.filter(user=request.user).order_by('-date').first()
            user_profile = request.user.userprofile  # 获取用户个人信息

            if latest_health_data:
                # 计算评分，忽略未填写数据的指标
                health_scores = {}
                if latest_health_data.weight and user_profile.height:
                    health_scores['weight'] = calculate_weight_score(latest_health_data.weight,
                                                                      user_profile.height)
                if latest_health_data.blood_pressure_sys and latest_health_data.blood_pressure_dia:
                    health_scores['blood_pressure'] = calculate_blood_pressure_score(
                        latest_health_data.blood_pressure_sys, latest_health_data.blood_pressure_dia)
                if latest_health_data.blood_sugar:
                    health_scores['blood_sugar'] = calculate_blood_sugar_score(latest_health_data.blood_sugar)
                if latest_health_data.steps:
                    health_scores['steps'] = calculate_steps_score(latest_health_data.steps)
                if latest_health_data.heart_rate:
                    health_scores['heart_rate'] = calculate_heart_rate_score(latest_health_data.heart_rate)

                if form.is_valid():  # 注意： 将 form.add_error 移到 if form.is_valid(): 代码块内部
                    # 身高提示
                    if user_profile.height is None and latest_health_data.weight:  # 只有体重填写了，身高没填写才提示
                        form.add_error(None, "请先填写您的身高信息才能进行体重评估。")

                    if latest_health_data.blood_sugar > 11.1:
                        form.add_error(None, '您的血糖值偏高，请注意饮食和运动。')
                    if latest_health_data.blood_pressure_sys is not None and latest_health_data.blood_pressure_dia is not None:
                        if latest_health_data.blood_pressure_sys > 140 or latest_health_data.blood_pressure_dia > 90:
                            form.add_error(None, '您的血压值偏高，建议您及时就医。')
            else:
                # 如果没有健康数据，但用户填写了身高和体重，则计算所有评分
                health_scores = {}
                if user_profile.height:
                    if user_profile.weight:
                        health_scores['weight'] = calculate_weight_score(user_profile.weight, user_profile.height)
                    if latest_health_data: # 检查是否为 None
                        if latest_health_data.blood_pressure_sys and latest_health_data.blood_pressure_dia:
                            health_scores['blood_pressure'] = calculate_blood_pressure_score(latest_health_data.blood_pressure_sys,
                                                                                         latest_health_data.blood_pressure_dia)
                    if latest_health_data: # 检查是否为 None
                        if latest_health_data.blood_sugar:
                            health_scores['blood_sugar'] = calculate_blood_sugar_score(latest_health_data.blood_sugar)
                    if latest_health_data:  # 检查是否为 None
                        if latest_health_data.steps:
                            health_scores['steps'] = calculate_steps_score(latest_health_data.steps)
                    if latest_health_data: # 检查是否为 None
                        if latest_health_data.heart_rate:
                            health_scores['heart_rate'] = calculate_heart_rate_score(latest_health_data.heart_rate)
        else:
            health_scores = {}

    return render(request, 'data.html', {'data_form': form, 'health_data': health_data,
                                       'health_scores': health_scores})


def index(request):
    latest_health_data = HealthData.objects.filter(user=request.user).order_by(
        '-date').first() if request.user.is_authenticated else None
    return render(request, 'index.html', {'latest_health_data': latest_health_data})


# 评分算法函数
def calculate_weight_score(weight, height):
    if height is None or weight is None:  # 如果身高或体重为空，则返回默认评分
        return 50
    bmi = weight / (height * height)
    if bmi < 18.5:
        return 60
    elif 18.5 <= bmi < 25:
        return 90
    elif 25 <= bmi < 30:
        return 70
    else:
        return 50


def calculate_blood_pressure_score(sys, dia):
    if sys is None or dia is None:
        return 50  # 返回默认评分
    if sys < 120 and dia < 80:
        return 100
    elif 120 <= sys < 140 and dia < 90:
        return 80
    elif sys >= 140 or dia >= 90:
        return 60
    else:
        return 50


def calculate_blood_sugar_score(blood_sugar):
    if blood_sugar is None:
        return 50
    if blood_sugar < 7.0:
        return 100
    elif 7.0 <= blood_sugar < 11.1:
        return 80
    else:
        return 60


def calculate_steps_score(steps):
    if steps is None:
        return 50  # 返回默认评分
    if steps >= 10000:
        return 100
    elif 5000 <= steps < 10000:
        return 80
    else:
        return 60


def calculate_heart_rate_score(heart_rate):
    if heart_rate is None:
        return 50
    if 60 <= heart_rate <= 100:
        return 100
    else:
        return 70