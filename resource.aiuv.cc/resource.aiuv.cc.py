# coding=utf-8
from flask import Flask
from flask import render_template
import MySQLdb
import json
from flask_wtf import Form
from wtforms import *
from wtforms.validators import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'resource.aiuv.cc'

class ResourceForm(Form):
    id = IntegerField('id')
    ip = StringField('ip')
    cpuFree = FloatField('cpuFree')
    memoryFree = FloatField('memoryFree')
    memoryTotal = FloatField('memoryTotal')
    diskFree = FloatField('diskFree')
    diskTotal = FloatField('diskTotal')
    disks = TextAreaField('disks')



DBINFO = {'host': '10.0.202.201',
          'port': 3306,
          'user': 'noc',
          'password': 'ksBtZ1f25cv7',
          'db': 'hx_noc',
          'table': 'hx_resource'
          #grant select,insert,delete,update,create on hx_noc.* to 'noc'@'10.%' identified by 'ksBtZ1f25cv7';
          }

@app.route('/')
def resource():
    sql = '''SELECT * from {}'''.format(DBINFO['table'])
    try:
        conn = MySQLdb.connect(host=DBINFO['host'],
                               user=DBINFO['user'],
                               passwd=DBINFO['password'],
                               port=DBINFO['port'],
                               db=DBINFO['db'],
                               connect_timeout=10
                               )
        conn.set_character_set('utf8')
        cur = conn.cursor()
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        cur.execute(sql)
        ones = cur.fetchall()
        conn.commit()
        conn.close()
        return render_template("resource.html",rows = ones)

    except MySQLdb.Error as e:
        return ("Error %d: %s" % (e.args[0], e.args[1]))

if __name__ == '__main__':
    app.run()
