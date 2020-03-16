from flask import Flask,jsonify,request
import requests
import config


app = Flask(__name__)


@app.route("/", methods =["GET","POST"])
def process():
    data=request.form
    sender=data['from']
    message =data['message']
    print('received {} from {}'.format(message,sender))
    send_sms(sender,message)
    ret = {"message":"processed"}
    return jsonify(ret) , 200

def send_sms(receptor,message):
    url = 'https://api.kavenegar.com/v1/{}/sms/send.json'.format(config.API_KEY)
    print(config.API_KEY)
    data ={'message':message ,
           'receptor':receptor }
    res = requests.post(url,data)     
    print("message :{} status code:{}".format(message,res.status_code))  

def check_serial():
    pass

if __name__ == "__main__":  
    app.run("0.0.0.0",5000)
