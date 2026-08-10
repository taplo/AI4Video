"""
URL configuration for framework project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.conf import settings
import os

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path(r'app/', include('app.urls')),
    path(r'', include('app.urls')),
    # 动态上传目录（运行时新增文件）
    re_path(r'^upload/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'static', 'upload')}),
]

# OpenAPI Schema and Swagger UI (DEBUG mode only, per D-17)
# URLs are always registered but guarded at request time so they are not
# exposed in production. Returning 404 keeps the runtime dependency on
# drf_spectacular gated behind DEBUG.
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def _debug_only(view):
    """Return a view that 404s unless DEBUG is enabled."""
    def inner(request, *args, **kwargs):
        if not settings.DEBUG:
            from django.http import Http404
            raise Http404
        return view(request, *args, **kwargs)
    return inner

urlpatterns += [
    path('api/schema/', _debug_only(SpectacularAPIView.as_view()), name='schema'),
    path('api/docs/', _debug_only(SpectacularSwaggerView.as_view(url_name='schema')), name='swagger-ui'),
]

urlpatterns += staticfiles_urlpatterns()
