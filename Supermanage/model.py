#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   File Name：     model
   Description :    数据库操作
   Author :       Lerrety
   date：          18-3-21
"""
from Model.models import *


# 判断用户， 返回：0-管理员，1-员工，2-用户名或密码错误
def checkUser(username, password):
    res = User.objects.filter(username=username, password=password).first()
    if res:
        return res.user_level
    else:
        return 2


# 添加商品种类, 返回：1-成功添加， 0-失败
def addGoodsType(typename):
    res = GoodsType.objects.filter(goods_type=typename).first()
    try:
        if res:
            return 0
        type_add = GoodsType(goods_type=typename)
        type_add.save()
        return 1
    except:
        return 0


# 列表返回所有商品种类
def getGoodsType():
    res = GoodsType.objects.all()
    type_list = []
    for var in res:
        type_list.append(var.goods_type)

    return type_list


# 添加商品信息， 加到库存表中, 返回：1-成功，0-失败, 2-编号重复
def addGoods(goods_id, goods_type, goods_name, unit, quantity, buying_price, price):
    res = Stock.objects.filter(goods_id=goods_id).first()
    if res:
        return 2
    try:
        goods_add = Stock(goods_id=goods_id, goods_type=goods_type, goods_name=goods_name, unit=unit, quantity=quantity,
                          buying_price=buying_price, price=price)
        goods_add.save()
        return 1
    except:
        return 0


# 列表返回所有库存信息
def getStock():
    res = Stock.objects.all()
    goods_list = []
    for var in res:
        goods_list.append(var)
    return goods_list


def reduce_stock_sale(reduce_set, username, now_time, user_level):
    """
        销售-减少库存，添加销售库记录
        返回: {
            'status': 'success'/'fail',
            'list': {0:{id, name, quantity, price, tot_price},
                    1:.....}
            'total': 总额,
            'sale_id': 销售单号,
            'time': now_time,
            'username': 用户名
        }
    """
    sale_id = now_time + user_level    # 销售单号：时间戳+用户等级
    total = 0
    return_set = {
        'sale_id': sale_id,
        'time': now_time
    }

    try:
        sale_list = {}
        for key in reduce_set:
            goods_id = reduce_set[key]['id']
            goods_quantity = int(reduce_set[key]['quantity'])
            stock_object = Stock.objects.get(goods_id=goods_id)
            db_quantity = stock_object.quantity     # 库存数量
            Stock.objects.filter(goods_id=goods_id).update(quantity=db_quantity-goods_quantity)  # 减少库存
            sale_list.update({     # 商品金额
                key: {'goods_id': goods_id,
                      'goods_name': stock_object.goods_name,
                      'goods_quantity': goods_quantity,
                      'price': stock_object.price,
                      'tot_price': round(stock_object.price*goods_quantity, 2)}
            })
            total += round(stock_object.price*goods_quantity, 2)  # 计算总额
            sale = Sale(sale_id=sale_id, time=now_time, goods_id=goods_id,
                        goods_quantity=goods_quantity, username=username)
            sale.save()
        return_set.update({
            'status': 'success',
            'total': total,
            'list': sale_list,
            'username': username,
        })
        return return_set
    except:
        return {
            'status': 'fail'
        }


def reduce_stock_return(reduce_set, username, now_time, user_level):
    """
        退货-减少库存，添加退货库记录
        返回: {
            'status': 'success'/'fail',
            'list': {0:{id, name, quantity, buying_price, tot_price},
                    1:.....}
            'total': 总额,
            'return_id': 退货单号,
            'time': now_time,
            'username': 用户名
        }
    """
    return_id = now_time + user_level  # 销售单号：时间戳+用户等级
    total = 0
    return_set = {
        'return_id': return_id,
        'time': now_time
    }

    try:
        return_list = {}
        for key in reduce_set:
            goods_id = reduce_set[key]['id']
            goods_quantity = int(reduce_set[key]['quantity'])
            stock_object = Stock.objects.get(goods_id=goods_id)
            db_quantity = stock_object.quantity  # 库存数量
            Stock.objects.filter(goods_id=goods_id).update(quantity=db_quantity - goods_quantity)  # 减少库存
            return_list.update({  # 商品金额
                key: {'goods_id': goods_id,
                      'goods_name': stock_object.goods_name,
                      'goods_quantity': goods_quantity,
                      'buying_price': stock_object.price,
                      'tot_price': round(stock_object.price * goods_quantity, 2)}
            })
            total += round(stock_object.buying_price * goods_quantity, 2)  # 计算总额
            return_goods = ReturnGoods(return_id=return_id, time=now_time, goods_id=goods_id,
                                       goods_quantity=goods_quantity, username=username)
            return_goods.save()
        return_set.update({
            'status': 'success',
            'total': total,
            'list': return_list,
            'username': username,
        })
        return return_set
    except:
        return {
            'status': 'fail'
        }


def add_stock_buy(add_set, username, now_time, user_level):
    """
        进货-减少库存，添加进货库记录
        返回: {
            'status': 'success'/'fail',
            'list': {0:{id, name, quantity, buying_price, tot_price},
                    1:.....}
            'total': 总额,
            'buy_id': 进货单号,
            'time': now_time,
            'username': 用户名
        }
    """
    buy_id = now_time + user_level  # 销售单号：时间戳+用户等级
    total = 0
    return_set = {
        'buy_id': buy_id,
        'time': now_time
    }

    try:
        return_list = {}
        for key in add_set:
            goods_id = add_set[key]['id']
            goods_quantity = int(add_set[key]['quantity'])
            stock_object = Stock.objects.get(goods_id=goods_id)
            db_quantity = stock_object.quantity  # 库存数量
            Stock.objects.filter(goods_id=goods_id).update(quantity=db_quantity + goods_quantity)  # 增加库存
            return_list.update({  # 商品金额
                key: {'goods_id': goods_id,
                      'goods_name': stock_object.goods_name,
                      'goods_quantity': goods_quantity,
                      'buying_price': stock_object.price,
                      'tot_price': round(stock_object.price * goods_quantity, 2)}
            })
            total += round(stock_object.buying_price * goods_quantity, 2)  # 计算总额
            buy = Buying(buy_id=buy_id, time=now_time, goods_id=goods_id,
                         goods_quantity=goods_quantity, username=username)
            buy.save()
        return_set.update({
            'status': 'success',
            'total': total,
            'list': return_list,
            'username': username,
        })
        return return_set
    except:
        return {
            'status': 'fail'
        }


# 添加用户信息， 加到用户信息表中, 返回：1-成功，0-失败, 2-名字重复
def addUser(user_level, username, password):
    res = User.objects.filter(username=username).first()
    if res:
        return 2
    try:
        user_add = User(user_level=user_level, username=username, password=password)
        user_add.save()
        return 1
    except:
        return 0


# 查询库存信息,返回指定编号的商品库存信息
def stock_db_query(goods_id):
    try:
        res = Stock.objects.filter(goods_id=goods_id).first()
        if res:
            return {
                'status': 'success',
                'msg': res
            }
        else:
            return {
                'status': 'fail'
            }
    except:
        return {
            'status': 'fail'
        }


# 销售单查询
def sale_list_db_query(sale_id):
    """
        销售单查询-查询销售库记录
        返回: {
            'status': 'success'/'fail',
            'list': {0:{id, name, quantity, price, tot_price},
                    1:.....}
            'total': 总额,
            'sale_id': 销售单号,
            'time': 销售时间戳
        }
    """
    try:
        res = Sale.objects.filter(sale_id=sale_id)
        if res:
            return_set = {
                'status': 'success'
            }
            return_list = {}
            count = 0
            total = 0
            for var in res:
                goods_id = var.goods_id
                goods_obj = Stock.objects.get(goods_id=goods_id)
                return_list.update({
                    count: {
                        'goods_id': goods_id,
                        'goods_name': goods_obj.goods_name,
                        'goods_quantity': var.goods_quantity,
                        'price': goods_obj.price,
                        'tot_price': round(goods_obj.price*var.goods_quantity, 2)
                    }
                })
                count += 1
                total += round(goods_obj.price*var.goods_quantity, 2)

            return_set.update({
                'list': return_list,
                'total': total,
                'sale_id': sale_id,
                'time': res.first().time
            })
            return return_set

        else:
            return {
                'status': 'fail'
            }

    except:
        return {
            'status': 'fail'
        }
