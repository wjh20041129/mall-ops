# -*- coding: utf-8 -*-
import hashlib
import json
import os
import random
import time

import pymysql
import redis
from flask import (Flask, flash, redirect, render_template, request,
                   session, url_for)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mall-secret")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "mall")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mall123")
DB_NAME = os.getenv("DB_NAME", "mall")
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")


def get_db():
    return pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_redis():
    return redis.Redis(host=REDIS_HOST, decode_responses=True)


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def query(sql, args=None, one=False):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, args)
        result = cursor.fetchone() if one else cursor.fetchall()
    finally:
        conn.close()
    return result


@app.route("/")
def index():
    goods = query("SELECT * FROM goods ORDER BY id")
    return render_template("index.html", goods=goods)


@app.route("/goods/<int:gid>")
def goods_detail(gid):
    r = get_redis()
    key = "goods:%d" % gid
    data = r.get(key)
    if data:
        print("缓存命中", key)
        goods = json.loads(data)
    else:
        goods = query("SELECT * FROM goods WHERE id=%s", (gid,), one=True)
        if not goods:
            return "商品不存在", 404
        r.setex(key, 60, json.dumps(goods, ensure_ascii=False))
        print("缓存已写入", key)
    return render_template("goods.html", goods=goods)


@app.route("/buy", methods=["POST"])
def buy():
    if "user_id" not in session:
        flash("请先登录")
        return redirect(url_for("login"))

    gid = int(request.form.get("goods_id"))
    qty = int(request.form.get("quantity", 1))
    conn = get_db()
    try:
        cursor = conn.cursor()
        # 带库存条件的更新，防超卖
        n = cursor.execute(
            "UPDATE goods SET stock=stock-%s WHERE id=%s AND stock>=%s",
            (qty, gid, qty))
        if n == 0:
            conn.rollback()
            flash("库存不足")
            return redirect(url_for("goods_detail", gid=gid))
        cursor.execute("SELECT price FROM goods WHERE id=%s", (gid,))
        price = cursor.fetchone()["price"]
        order_no = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
        cursor.execute(
            "INSERT INTO orders(order_no, user_id, goods_id, quantity, total_price) "
            "VALUES(%s, %s, %s, %s, %s)",
            (order_no, session["user_id"], gid, qty, float(price) * qty))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("下单失败:", e)
        flash("下单失败，请重试")
        return redirect(url_for("index"))
    finally:
        conn.close()
    # 商品库存变了，清掉详情缓存
    get_redis().delete("goods:%d" % gid)
    flash("下单成功")
    return redirect(url_for("orders"))


@app.route("/orders")
def orders():
    if "user_id" not in session:
        flash("请先登录")
        return redirect(url_for("login"))
    rows = query(
        "SELECT o.order_no, g.name as goods_name, o.quantity, o.total_price, "
        "o.status, o.create_time FROM orders o "
        "JOIN goods g ON o.goods_id = g.id "
        "WHERE o.user_id=%s ORDER BY o.id DESC", (session["user_id"],))
    return render_template("orders.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = query("SELECT * FROM users WHERE username=%s AND password=%s",
                     (username, md5(password)), one=True)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        flash("用户名或密码错误")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)