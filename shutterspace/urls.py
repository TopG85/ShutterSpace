"""
URL configuration for shutterspace project.

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
from django.urls import path, include
from portfolio.views import portfolio_home
from portfolio.views import accounts_profile_redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', portfolio_home, name='home'),
    path('portfolio/', include('portfolio.urls')),
    # Custom auth URLs that handle redirects properly
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Provide a friendly redirect for /accounts/profile/ to the user's profile
    path('accounts/profile/', accounts_profile_redirect,
         name='accounts_profile_redirect'),
    # Include remaining auth URLs (password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
]

# Optional URL includes — only add when the package is available.
try:
    import allauth  # type: ignore  # noqa: F401
    urlpatterns += [path('accounts/', include('allauth.urls'))]
except Exception:
    pass

try:
    import django_summernote  # type: ignore  # noqa: F401
    urlpatterns += [path('summernote/', include('django_summernote.urls'))]
except Exception:
    pass


urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT)
