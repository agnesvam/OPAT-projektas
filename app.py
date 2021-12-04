import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
import requests


def __init__(self):
 con = sqlite3.connect('datab.db')
 f = open('db.sql','r')
 str = f.read()
 cur = con.cursor()
 cur.executemany(str)

def save_city_to_db( user, city):
    con = sqlite3.connect('datab.db')
    cur = con.cursor()
    cur.execute('INSERT INTO user_items ( username, citys) values (?,?)', ( user, city))
    con.commit()
    con.close()


def register_user_to_db(username,password,email):
    con = sqlite3.connect('datab.db')
    cur=con.cursor()
    cur.execute('INSERT INTO users (username,password,email) values (?,?,?)',(username,password,email))
    con.commit()
    con.close()

def check_user(username, password):
    con = sqlite3.connect('datab.db')
    cur = con.cursor()
    cur.execute('Select username,password FROM users WHERE username=? and password=?', (username, password))

    result = cur.fetchone()
    if result:
        return True
    else:
        return False

app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"

temp = 0

@app.route("/")
def index():
    return render_template('home.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        register_user_to_db(username, password,email)
        return redirect(url_for('login'))

    else:
        return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():

    if request.method == 'POST':

        api_key = "6b06dbe48b2f20ba8e9c3fadcfa903b3"

        base_url = "http://api.openweathermap.org/data/2.5/weather?"

        city_name = request.form['search']

        complete_url = base_url + "appid=" + api_key +"&q="+city_name + "&units=metric"

        response = requests.get(complete_url)
        r = requests.get(complete_url.format(city_name)).json()

        x = response.json()

        if x["cod"] != "404":
            y = x["main"]
    
            current_temperature = y["temp"]
        
            current_humidity = y["humidity"]
        
            z = x["weather"]

            weather_description = z[0]["description"]   

            icon = r['weather'][0]['icon']
        
        else:
            return render_template('search.html', cityName = "Miestas nerastas", temperature = "", description = "")

        return render_template('search.html', cityName = city_name, temperature = current_temperature, description = weather_description,)
    else:
        return render_template('search.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    s = 0
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
      
        print(check_user(username, password))
        if check_user(username, password):
            session['username'] = username
            session['password'] = password
        return redirect(url_for('homeLoggedIn'))
    else:
        return render_template('login.html')


@app.route('/home', methods=['POST', "GET"])
def home():

    api_key = "6b06dbe48b2f20ba8e9c3fadcfa903b3"

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    #city_name = "Vilnius"
    cities = ["Vilnius","Kaunas","New York","Bangkok","London","Dubai","Delhi","Rome","Mexico","Los Angeles"]
    context1 = []

    for city in cities:
        complete_url = base_url + "appid=" + api_key +"&q="+city + "&units=metric"

        response = requests.get(complete_url)

        x = response.json()

        if x["cod"] != "404":
            y = x["main"]
    
            current_temperature = y["temp"]
        
            current_humidity = y["humidity"]
        
            z = x["weather"]

            weather_description = z[0]["description"]
            r = requests.get(complete_url.format(city)).json()

            city_weather = [city, current_temperature, weather_description, r['weather'][0]['icon']]

            context1.append(city_weather)
    
        else:
            return render_template('search.html', popular=context1)

    return render_template('home.html', popular=context1)

#CIA BANDYTA SU SAUGOJIMU------------------------------------------------------------------------------------------------------------------------------------------------------
searched = ""
@app.route('/home-logged', methods=['POST', 'GET'])
def homeLoggedIn():
    if request.method == 'POST':
        api_key = "6b06dbe48b2f20ba8e9c3fadcfa903b3"

        base_url = "http://api.openweathermap.org/data/2.5/weather?"

        city_name = request.form['search']
        global searched 
        searched= city_name
        print(searched)

        complete_url = base_url + "appid=" + api_key +"&q="+city_name + "&units=metric"

        response = requests.get(complete_url)
        r = requests.get(complete_url.format(city_name)).json()

        x = response.json()

        if x["cod"] != "404" and x["cod"] != "400":
            y = x['main']
    
            current_temperature = y['temp']
        
            current_humidity = y['humidity']
        
            z = x['weather']

            weather_description = z[0]['description']

            icon =  r['weather'][0]['icon']

        else:
            return render_template('home-logged-in.html', cityName = "Miestas nerastas", temperature = "", description = "")
        return render_template('home-logged-in.html', cityName = city_name, temperature = current_temperature, description = weather_description, icon = icon, searching=city_name)
    else:
        return render_template('home-logged-in.html')   

    


@app.route('/save', methods=['POST', 'GET'])
def homeSave():
    if request.method == 'POST':
       
        email = session['username']
        city = searched
           

        save_city_to_db( email, city)
        
        #return redirect(url_for('homeLoggedIn'))       
        return render_template('home-logged-in.html')   

    else:
        return render_template('home-logged-in.html')   
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/update',methods = ['POST', 'GET'])
def update():
   if request.method == 'POST':

         username=session['username']
        # username = request.form['username']
         email = request.form['email']
         password = request.form['password']

            
         with sqlite3.connect("datab.db") as con:
            cur = con.cursor()
            update_task(con, (username, email, password, username))
            
      
         return render_template("home-logged-in.html")

def update_task(conn, task):
   
    sql = ''' UPDATE users
              SET username = ? ,
                  email = ? ,
                  password = ?
              WHERE username = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
        
@app.route('/profile')
def ShowProfile():
   
   return render_template("profile.html", username=session['username'])
       # return render_template('profile.html', password= =session['password'] )




def deleteAccount(conn, name):
       
    sql = ''' DELETE FROM users
              WHERE username = ?'''
    cur = conn.cursor()
    cur.execute(sql, name)
    conn.commit()

@app.route('/delete',methods = ['POST', 'GET'])
def delete():
   
    if request.method == 'POST':
         username=session['username']
         with sqlite3.connect("datab.db") as con:
            cur = con.cursor()
            cur.execute('DELETE FROM users WHERE username=?', [username])
            
         session.clear()
         return redirect(url_for('index'))
        
def findlist(usr):
    con = sqlite3.connect('datab.db')
    cur = con.cursor()
    cur.execute('Select citys FROM user_items WHERE username=?', [usr])

    items = cur.fetchall()
    print(items)
    return items





@app.route('/list', methods=['POST', 'GET'])
def ShowList():
   usr=session['username']

   items=findlist(usr)
  

   return render_template("mylist.html", username=session['username'], items=items)
       # return render_template('profile.html', password= =session['password'] )

       
if __name__ == '__main__':
    app.run(debug=True)

