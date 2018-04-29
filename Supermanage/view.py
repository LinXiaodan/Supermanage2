#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   File Name：     view
   Description :    
   Author :       Lerrety
   date：          18-3-21
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .model import *
import json
import time


# 登录
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')

        check_user = checkUser(username, password)
        if check_user == 0 or check_user == 1:
            res = redirect('/stock')
            res.set_cookie('username', username, 60*60*24)
            res.set_cookie('user_level', check_user, 60*60*24)
            return res

        else:
            return render(request, 'login.html', {'msg': '用户名或密码错误'})


# 库存
def stock(request):
    username = request.COOKIES.get('username')
    user_level = request.COOKIES.get('user_level')

    if user_level == '0' or user_level == '1':
        context = {
            'username': username
        }
        stock_list = getStock()
        if user_level == '0':
            context.update({
                'info_list': ['编号', '种类', '名称', '单位', '库存量', '进货价（元）', '售价（元）']
            })
            show_list = []
            for var in stock_list:
                show_list.append([var.goods_id, var.goods_type, var.goods_name, var.unit, var.quantity,
                                  var.buying_price, var.price])
            context.update({
                'show_list': show_list
            })
        else:
            context.update({
                'info_list': ['编号', '种类', '名称', '单位', '库存量', '售价（元）']
            })
            show_list = []
            for var in stock_list:
                show_list.append([var.goods_id, var.goods_type, var.goods_name, var.unit, var.quantity,
                                  var.price])
            context.update({
                'show_list': show_list
            })
        return render(request, 'stock.html', context)
    else:
        return redirect('/login')


# 库存查询
def stock_query(request):
    if request.COOKIES.get('user_level') is None:
        return redirect('/login')

    if request.method == 'POST':
        msg = json.loads(request.body)
        goods_id = msg.get('goods_id')
        query_list = stock_db_query(goods_id)
        user_level = request.COOKIES.get('user_level')
        ctx = {}

        if query_list.get('status') == 'fail':
            ctx = query_list
        else:
            ctx.update({
                'status': 'success'
            })
            if user_level == '0':
                ctx.update({
                    'info_list': ['编号', '种类', '名称', '单位', '库存量', '进货价（元）', '售价（元）']
                })
                msg = query_list.get('msg')
                # ctx.update({
                #     'show_list': [msg.get('goods_id'), msg.get('goods_type'), msg.get('goods_name'), msg.get('unit'),
                #                   msg.get('quantity'), msg.get('buying_price'), msg.get('price')]
                # })
                ctx.update({
                    'show_list': [msg.goods_id, msg.goods_type, msg.goods_name, msg.unit, msg.quantity,
                                  msg.buying_price, msg.price]
                })
        return HttpResponse(json.dumps(ctx))
        # return HttpResponse(json.dumps(query_res))
    return render(request, 'stock_query.html')


# 添加商品种类
def add_type(request):
    if request.COOKIES.get('user_level') is None:
        return redirect('/login')
    if int(request.COOKIES.get('user_level')) is not 0:     # 非管理员
        return redirect('/stock')

    ctx = {
        'username': request.COOKIES.get('username')
    }
    if request.method == 'POST':
        if addGoodsType(request.POST.get('type')) == 1:
            ctx.update({
                'msg': '添加种类成功！'
            })
        else:
            ctx.update({
                'msg': '添加种类失败！'
            })

    return render(request, 'add_type.html', ctx)


# 添加商品信息
def add_goods(request):
    if request.COOKIES.get('user_level') is None:
        return redirect('/login')
    if int(request.COOKIES.get('user_level')) is not 0:     # 非管理员
        return redirect('/stock')

    ctx = {
        'username': request.COOKIES.get('username')
    }
    type_list = getGoodsType()
    ctx.update({
        'goodstype_list': type_list
    })

    if request.method == 'GET':
        return render(request, 'add_goods.html', ctx)

    else:
        goods_id = request.POST.get('goods_id')
        goods_type = request.POST.get('goods_type')
        goods_name = request.POST.get('goods_name')
        unit = request.POST.get('unit')
        buying_price = request.POST.get('buying_price')
        price = request.POST.get('price')
        res = addGoods(goods_id, goods_type, goods_name, unit, 0, buying_price, price)
        if res == 1:
            ctx.update({
                'msg': '添加商品成功！'
            })
        elif res == 0:
            ctx.update({
                'msg': '添加商品失败！'
            })
        else:
            ctx.update({
                'msg': '商品编号重复！'
            })
        return render(request, 'add_goods.html', ctx)


# 销售
def sale(request):
    if request.COOKIES.get('user_level') is None:   # 未登录
        return redirect('/login')

    username = request.COOKIES.get('username')
    ctx = {
        'username': username
    }

    if request.method == 'GET':
        return render(request, 'sale.html', ctx)
    else:
        now_time = str(int(time.time()))
        sale_result = reduce_stock_sale(json.loads(request.body), username, now_time, request.COOKIES.get('user_level'))

        if sale_result.get('status') == 'success':
            return HttpResponse(json.dumps(sale_result))
        else:
            return HttpResponse('失败，请重试！')


# 退货
def return_goods(request):
    if request.COOKIES.get('user_level') is None:   # 未登录
        return redirect('/login')
    if int(request.COOKIES.get('user_level')) is not 0:     # 非管理员
        return redirect('/stock')

    username = request.COOKIES.get('username')
    ctx = {
        'username': username
    }

    if request.method == 'GET':
        return render(request, 'return_goods.html', ctx)
    else:
        now_time = str(int(time.time()))
        return_result = reduce_stock_return(json.loads(request.body), username, now_time, request.COOKIES.get('user_level'))

        if return_result.get('status') == 'success':
            return HttpResponse(json.dumps(return_result))
        else:
            return HttpResponse('失败，请重试！')


# 进货
def buy(request):
    if request.COOKIES.get('user_level') is None:  # 未登录
        return redirect('/login')
    if int(request.COOKIES.get('user_level')) is not 0:  # 非管理员
        return redirect('/stock')

    username = request.COOKIES.get('username')
    ctx = {
        'username': username
    }

    if request.method == 'GET':
        return render(request, 'buy.html', ctx)
    else:
        now_time = str(int(time.time()))
        return_result = add_stock_buy(json.loads(request.body), username, now_time, request.COOKIES.get('user_level'))

        if return_result.get('status') == 'success':
            return HttpResponse(json.dumps(return_result))
        else:
            return HttpResponse('失败，请重试！')


# 销售单页面
def sale_list(request):
    list_info = json.loads(request.COOKIES.get('list_info'))
    print list_info
    return HttpResponse('销售')


# 添加用户
def add_user(request):
    if request.COOKIES.get('user_level') is None:
        return redirect('/login')
    if int(request.COOKIES.get('user_level')) is not 0:     # 非管理员
        return redirect('/stock')

    username = request.COOKIES.get('username')
    ctx = {
        'username': username
    }

    if request.method == 'GET':
        return render(request, 'add_user.html', ctx)
    else:
        user_level_val = request.POST.get('user_level')
        if user_level_val == 'admin':
            add_user_level = 0
        else:
            add_user_level = 1
        add_username = request.POST.get('username')
        add_password = request.POST.get('password')
        res = addUser(add_user_level, add_username, add_password)
        if res == 1:
            ctx.update({
                'msg': '添加用户成功！'
            })
        elif res == 0:
            ctx.update({
                'msg': '添加用户失败！'
            })
        else:
            ctx.update({
                'msg': '用户名重复！'
            })
        return render(request, 'add_user.html', ctx)


# 注销
def logout(request):
    response = redirect('/login')
    response.delete_cookie('username')
    response.delete_cookie('user_level')
    return response
