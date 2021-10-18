from flask import request, render_template, redirect, url_for
from flask_migrate import Migrate
import pymysql
import re
import datetime
import math
import json
import traceback
from web.server import app, db
from web.models import HashTagModel, HashTagProductModel

migrate = Migrate(app, db)

# L1 SUID
@app.route("/", methods=["GET"])
def index():
    # 設定前端參數
    data = []
    column = request.args.get('column')
    condition = request.args.get('condition')
    value = request.args.get('value')

    # SQL 檢查與 Query 語句包裝
    danger = sql_protect(column, condition, value)
    sql_condition = sql_query(column, condition, value)

    if danger == False:
        db, cursor = db_init('localhost', 'root', 'password', 'hiskio_sql')
        sql = """SELECT * FROM hiskio_sql.products {}""".format(sql_condition)
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
    return render_template('index.html', data=data, danger=danger)

@app.route("/", methods=["POST"])
def create():
    name = request.values.get('name')
    description = request.values.get('description')
    publish_date = request.values.get('publish_date')
    price = request.values.get('price')
    cost = request.values.get('cost')
    now = datetime.datetime.now()
    db, cursor = db_init('localhost', 'root', 'password', 'hiskio_sql')
    sql = """
            INSERT INTO `hiskio_sql`.`products` (`name`,`description`,`publish_date`,`price`,`cost`, `created_at`, `updated_at`) 
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');
          """.format(name, description, publish_date, price, cost, now, now)
    cursor.execute(sql)
    db.commit()

    sql = """SELECT * FROM hiskio_sql.products"""
    cursor.execute(sql)
    data = cursor.fetchall()

    db.close()
    return redirect(url_for('index', data=data, danger=False))

@app.route("/<id>", methods=["POST"])
def update(id):
    name = request.values.get('name')
    description = request.values.get('description')
    publish_date = request.values.get('publish_date')
    price = request.values.get('price')
    cost = request.values.get('cost')
    now = datetime.datetime.now()
    db, cursor = db_init('localhost', 'root', 'password', 'hiskio_sql')
    sql = """
            UPDATE `hiskio_sql`.`products`
            SET `name` = '{}', `description` = '{}', `publish_date` = '{}', `price` = '{}', `cost` = '{}', `updated_at` = '{}'
            WHERE (`id` = '{}'); 
          """.format(name, description, publish_date, price, cost, now, id)
    cursor.execute(sql)
    db.commit()

    sql = """SELECT * FROM hiskio_sql.products"""
    cursor.execute(sql)
    data = cursor.fetchall()

    db.close()
    return redirect(url_for('index', data=data, danger=False))

@app.route("/<id>", methods=["GET"])
def show(id):
    db, cursor = db_init('localhost', 'root', 'password', 'hiskio_sql')
    sql = """SELECT * FROM hiskio_sql.products WHERE id = {}""".format(id)
    cursor.execute(sql)
    data = cursor.fetchone()
    db.close()

    return data

@app.route("/<id>", methods=["DELETE"])
def delete(id):
    db, cursor = db_init('localhost', 'root', 'password', 'hiskio_sql')
    sql = """
            DELETE FROM `hiskio_sql`.`products`
            WHERE (`id` = '{}'); 
          """.format(id)
    cursor.execute(sql)
    db.commit()

    db.close()
    return {}

# L2 Sql function
@app.route("/my-datatable", methods=["GET"])
def my_datatable():
    # 顯示用資料 & 初始化變數
    data = columns = []
    stas_result = {}
    count = pages = 0

    # 統計用資料
    stas_columns = ['price', 'cost']
    aggregate_functions = ['SUM', 'AVG']

    # 搜尋參數
    column = request.args.get('column')
    condition = request.args.get('condition')
    value = request.args.get('value')

    # 分頁參數 & 相關變數設定
    currentPage = request.args.get('page', 1)
    data_per_page = 3
    offset = data_per_page * (int(currentPage) - 1)
    pagination_condition = """limit {} offset {}""".format(data_per_page, offset)

    danger = sql_protect(column, condition, value)
    sql_condition = sql_query(column, condition, value)

    if danger == False:
        # 擷取被搜尋到的資料
        db, cursor = db_init('localhost', 'root', 'password', 'hiskio_sql')
        sql = """SELECT * FROM hiskio_sql.products {} {}""".format(sql_condition, pagination_condition)
        cursor.execute(sql)
        data = cursor.fetchall()

        # 擷取欄位資訊
        sql = """SELECT * FROM hiskio_sql.products limit 1"""
        cursor.execute(sql)
        single_data = cursor.fetchone()
        columns = single_data.keys()

        # 擷取利用 SQL 函式統計( Sum, Avg )
        for stas_column in stas_columns:
            stas_result[stas_column] = {}
            for aggregate_function in aggregate_functions:
                sql = """SELECT {}({}) FROM hiskio_sql.products {}""".format(aggregate_function, stas_column, sql_condition)
                cursor.execute(sql)
                aggregate_result = cursor.fetchone()
                stas_result[stas_column][aggregate_function] = float(aggregate_result["{}({})".format(aggregate_function, stas_column)])

        # 擷取總個數與分頁資訊
        sql = """SELECT COUNT(*) as result FROM hiskio_sql.products {}""".format(sql_condition)
        cursor.execute(sql)
        count = cursor.fetchone()['result']
        pages = math.ceil(count/data_per_page)
        db.close()

    return render_template("my_datatable.html", data=data, columns=columns, danger=danger, count=count, pages=pages,
                                                stas_columns=stas_columns, stas_result=stas_result, aggregate_functions=aggregate_functions)

# L3 Join
@app.route("/order-report", methods=["GET"])
def order_report():
    pass

# L4 Transaction
@app.route("/orders/<id>/shipment", methods=["POST"])
def create_shipment(id):
    pass

# L5 Hashtag sample code
@app.route("/hash-tags", methods=["GET"])
def hash_tags():
    data = []
    column = request.args.get('column')
    condition = request.args.get('condition')
    value = request.args.get('value')
    danger = sql_protect(column, condition, value)
    sql_condition = sql_query(column, condition, value)
    if danger == False:
        db, cursor = db_init()
        sql = """SELECT * FROM hiskio_sql.hash_tags {}""".format(sql_condition)
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
    return render_template("hash_tags.html", data=data, danger=danger)

@app.route("/hash-tags", methods=["POST"])
def create_hash_tags():
    name = request.values.get('name')
    db, cursor = db_init()
    sql = """
            INSERT INTO `hiskio_sql`.`hash_tags` (`name`) VALUES ('{}');
          """.format(name)
    cursor.execute(sql)
    db.commit()

    get_all_from_tables(cursor, 'hash_tags')

    db.close()
    return redirect(url_for('hash_tags', data=data, danger=False))

@app.route("/hash-tags/<id>", methods=["POST"])
def update_hash_tags(id):
    name = request.values.get('name')
    db, cursor = db_init()
    sql = """
            UPDATE `hiskio_sql`.`hash_tags` SET `name` = '{}' WHERE (`id` = '{}'); 
          """.format(name, id)
    cursor.execute(sql)
    db.commit()

    get_all_from_tables(cursor, 'hash_tags')

    db.close()
    return redirect(url_for('hash_tags', data=data, danger=False))

@app.route("/hash-tags/<id>", methods=["DELETE"])
def delete_hash_tags(id):
    db, cursor = db_init()
    sql = """
            DELETE FROM `hiskio_sql`.`hash_tags`
            WHERE (`id` = '{}'); 
          """.format(id)
    cursor.execute(sql)
    db.commit()

    db.close()
    return {}


# L5 Hashtag
@app.route("/products/<id>/hash-tags", methods=["GET"])
def product_hash_tags(id):
    pass

@app.route("/products/<id>/hash-tags", methods=["POST"])
def product_bind_hash_tags(id):
    pass

# Tools
def sql_query(column, condition, value, condition_text = 'where'):
    sql_condition = ' {} '.format(condition_text)
    if condition == 'in':
        value = list(map(lambda item: "'{}'".format(str(item)), value.split(',')))
        value = ','.join(value)
        sql_condition += column + ' ' + condition + ' ({})'.format(value)
    elif condition == 'between':
        value = value.split(',')
        sql_condition += column + ' ' + condition + ' "{}" and "{}"'.format(value[0], value[1])
    elif condition == 'like':
        sql_condition += column + ' ' + condition + ' "%{}%"'.format(value)
    elif condition == 'is null':
        sql_condition += column + ' ' + condition
    elif condition == None:
        sql_condition = ''
    else: # =, !=, >
        sql_condition += column + ' ' + condition + ' "{}" '.format(value)
    return sql_condition

def db_init(host, user, password, db):
    db = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db, cursor

def sql_protect(column, condition, value):
    if column == condition == value == None:
        return False
    regex = re.compile(r'\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})\b')
    column_match = regex.search(column)
    condition_match = regex.search(condition)
    value_match = regex.search(value)
    if column_match or condition_match or value_match:
        return True
    else:
        return False

def get_all_from_tables(cursor, table):
    sql = 'SELECT * FROM hiskio_sql.{}'.format(table)
    cursor.execute(sql)
    return cursor.fetchall()

def where_in_string_to_list(value): # Where In 包裝使用
    return list(map(lambda item: "'{}'".format(str(item)), value.split(',')))

def serialize_model(data): # Model 釋出使用
    return list(map(lambda item: item.serialize(), data))