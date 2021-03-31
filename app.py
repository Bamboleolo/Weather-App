from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import sys
import json
import os
import sqlite3

app = Flask(__name__)
file_path = os.path.abspath(os.getcwd())+"/weather.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
app.secret_key = 'many random bytes'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name


con = sqlite3.connect('weather.db')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
if not cursor.fetchall() or not os.path.exists('weather.db'):
    db.create_all()


# write your code here
@app.route('/')
def index():
    dict_with_weather_info_list = []
    for city in City.query.all():
        print("index(): " + city.name)
        req = ow_req_addr + city.name + "&appid=" + ow_api_key
        resp = requests.get(req)
        res = json.loads(resp.text)

        dict_with_weather_info = {'deg': (round(res['main']['temp'] - 273.16)),
                                  'state': res['weather'][0]['main'],
                                  'name': res['name'].upper(),
                                  'id': city.id}
        dict_with_weather_info_list.append(dict_with_weather_info)
    return render_template('index.html', weathers=dict_with_weather_info_list)


@app.route('/add', methods=['POST'])
def add_city():
    print("ADD_CITY!!")
    city_name = request.form['city_name']

    req = ow_req_addr + city_name + "&appid=" + ow_api_key
    resp = requests.get(req)
    print(resp.text)
    res = json.loads(resp.text)

    if res["cod"] == '404':
        flash("The city doesn't exist!")
        print("The city doesn't exist!")
    elif City.query.filter_by(name=res['name'].upper()).first():
        flash("The city has already been added to the list!")
        print("The city has already been added to the list!")
    else:
        row = City(name=res['name'].upper())
        db.session.add(row)
        db.session.commit()

    return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    print('delete city...')
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
        db.create_all()
    else:
        app.run()
        db.create_all()
