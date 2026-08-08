from app.views.ViewsBase import *
from django.shortcuts import render


def index(request):
    """报警管理页面：集中展示与处理进入区域/滞留/运动等报警事件及快照"""
    return render(request, 'app/alarm/index.html', {})
