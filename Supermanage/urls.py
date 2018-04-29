"""Supermanage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import view


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', view.login),
    url(r'^$', view.login),
    url(r'add_type', view.add_type),
    url(r'add_goods', view.add_goods),
    url(r'query_sale_list', view.sale_list_query),
    url(r'sale', view.sale),
    url(r'add_user', view.add_user),
    url(r'return_goods', view.return_goods),
    url(r'query_buy_list', view.buy_list_query),
    url(r'buy', view.buy),
    url(r'logout', view.logout),
    url(r'query_stock', view.stock_query),
    url(r'stock', view.stock)
]
