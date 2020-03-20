from flask import Flask,jsonify,Response, redirect, url_for, request, session, abort
from pandas import read_excel
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import requests
import config
import sqlite3


app = Flask(__name__)

# config
app.config.update(
      SECRET_KEY = config. SECRET_KEY
)
# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):

    def __init__(self, id):
        self.id = id
     
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user =User(0)


# some protected url
@app.route('/')
@login_required
def home():
    return Response("Hello World!")

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == config.password and username ==config.username :
            login_user(user)
            return redirect('/')
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app.route("/v1/process", methods =["GET","POST"])
def process():
    if request.form :
        data=request.form
        sender=data['from']
        message =data['message']
        print('received {} from {}'.format(message,sender))

        answer = check_serial(message)

        send_sms(sender,answer)
        ret = {"message":"processed"}
        return jsonify(ret) , 200
    else :
        return "request is empty"

def send_sms(receptor,message):
    url = 'https://api.kavenegar.com/v1/{}/sms/send.json'.format(config.API_KEY)
    print(config.API_KEY)
    data ={'message':message ,
           'receptor':receptor }
    res = requests.post(url,data)     
    print("message :{} status code:{}".format(message,res.status_code))  

def sqlite(): 
    conn = sqlite3.connect(config.DATABASE_FILE_PATH)
    cur = conn.cursor()

    cur.execute("""	 CREATE TABLE IF NOT EXISTS sht35 (
        id INTEGER PRIMARY KEY,
        temp TEXT,
        humid TEXT
        );     """
    )
    conn.close()

def import_database_from_excel(filepath):

    conn = sqlite3.connect(config.DATABASE_FILE_PATH)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS serials')
    cur.execute("""
        CREATE TABLE IF NOT EXISTS serials ( 
        id INTEGER PRIMARY KEY,
        ref TEXT,
        desc TEXT,
        start_serial TEXT,
        end_serial TEXT,
        date DATE
        ); """    )

    conn.commit()

   
            

    df = read_excel(filepath,0)
    for index,(line,ref,desc,start_serial,end_serial,date) in df.iterrows():
        print(index)
        query = "INSERT INTO serials VALUES('{}','{}','{}','{}','{}','{}')".format(line,ref,desc,start_serial,end_serial,date)
        cur.execute(query)
    conn.commit()

   


def check_serial(serial):
    conn = sqlite3.connect(config.DATABASE_FILE_PATH)
    cur = conn.cursor()

    query = "SELECT * FROM serials WHERE start_serial < '{}' and end_serial >'{}'".format(serial,serial)
    results = cur.execute(query)
    if len(results.fetchall()) == 1:
        return "i found your serial"
    return "it was not in the db"
 

if __name__ == "__main__":
    import_database_from_excel("./data.xlsx")
    app.run("0.0.0.0",5000)
    
  

