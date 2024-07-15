from django import forms
from .models import UserProfile, HealthData

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'height', 'weight', 'gender', 'phone_number', 'medical_history']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'birth_date': '出生日期',
            'height': '身高 (米)',
            'weight': '体重 (公斤)',
            'gender': '性别',
            'phone_number': '电话号码',
            'medical_history': '病史',
        }

class HealthDataForm(forms.ModelForm):
    class Meta:
        model = HealthData
        fields = ['date', 'weight', 'blood_pressure_sys', 'blood_pressure_dia', 'steps', 'heart_rate', 'blood_sugar']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'date': '日期',
            'weight': '体重 (公斤)',
            'blood_pressure_sys': '收缩压',
            'blood_pressure_dia': '舒张压',
            'steps': '步数',
            'heart_rate': '心率',
            'blood_sugar': '血糖',
        }