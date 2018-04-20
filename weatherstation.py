
import json
from datetime import datetime
from time import sleep, localtime
from flask import request

import requests

from flask import Flask, render_template
import sqlite3
app = Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def hello_world():

    return render_template('index.html')
@app.route('/test')
def test():

    return render_template('test.html')
@app.route('/api/get')
def api():
    cnxn = sqlite3.connect('data.db')
    cnxn.row_factory = dict_factory
    cur = cnxn.cursor()
    data = cur.execute("SELECT date, label, apitemp, hometemp FROM temperature ORDER BY date ASC").fetchall()
    print(data)
    cnxn.close()
    return json.dumps(data)

@app.route('/api/insert', methods=["GET", "POST"])
def api_insert():
    data = request.form
    cnxn = sqlite3.connect('data.db') # type: sqlite3.Connection
    cnxn.row_factory = dict_factory
    cur = cnxn.cursor()
    data = request.form
    print("DATA = {}".format(data))
    r = requests.get(
        'http://api.openweathermap.org/data/2.5/weather?q=Ruckersville&APPID=13779597594e37ddbc7836d9599c7457')
    api_temp = float(r.json()['main']['temp']) - 273.15
    from time import strftime
    sqlstring = "INSERT INTO temperature (date, label, hometemp, apitemp) VALUES ('{}', '{}', {}, {})".format(datetime.now().timestamp() * 1000, strftime("%I%p", localtime()), data["hometemp"], api_temp)
    print(sqlstring)
    data = cur.execute(sqlstring).fetchone()
    cnxn.commit()
    cnxn.close()

    # import yagmail
    # yag = yagmail.SMTP()
    # contents = ['This is the body, and here is just text http://somedomain/image.png',
    #             'You can find an audio file attached.', '/local/path/song.mp3']
    # yag.send('to@someone.com', 'subject', contents)
    return "Successfully inserted into the database!"

if __name__ == '__main__':
    weather = "test"
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
