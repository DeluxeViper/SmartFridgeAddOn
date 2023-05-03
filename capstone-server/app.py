from flask import Flask, abort, request
import datetime
from flask_cors import CORS
from data.mutex import lock
from data.user_repository import readUser
from data.fridge_repository import addFridge, deleteFridge
import json
import os.path
from pathlib import Path
import depthai as dai
import RPi.GPIO as GPIO
import subprocess
from threading import Thread
import time
import netifaces
import ipaddress
#from celery import Celery


dir = os.path.dirname(__file__)
fname = os.path.join(dir, 'user.json')
if os.path.isfile(fname):
    print("File exists")
    subprocess.call(['cd /home/user/capstone-server && ./start_update_process.sh'], shell=True)
"""
with Manager() as manager:
    still_capture_mp_queue = manager.Queue()
    update_process = Process(target=track_fridge_door, args=(still_capture_mp_queue,))
    consume_frames_process = Process(target=mp_queue_test, args=(still_capture_mp_queue,))
"""
app = Flask(__name__)
"""
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
"""
registered = False

CORS(app)
'''
@app.before_first_request
def light_thread():
    global registered
    def thread_task():
        subprocess.call(['./start_update_process.sh'], shell=True)
    thread = Thread(target=thread_task)
    
    while not registered:
        time.sleep(1)
    print("Registered = true, starting thread")
    thread.start()
'''
@app.route('/health')
def device_health():
    health = {
        "status": "Ready",
    }
    if(os.path.isfile(fname)):
        with open(fname, 'r') as user_credential_file:
            user_credentials = json.load(user_credential_file)
            health['user_id'] = user_credentials['user_id']
            health['email'] = user_credentials['email']
            health['fridge_name'] = user_credentials['fridge_name']
            health['fridge_id'] = user_credentials['fridge_id']
            health['status'] = "Active"
            user_credential_file.close()
    return health

def thread_task():
    subprocess.call(['cd /home/user/capstone-server'], shell=True)
    subprocess.call(['./start_update_process.sh'], shell=True)

def get_ip_info():
    addrs = netifaces.ifaddresses('wlan0')
    #print(addrs[netifaces.AF_INET])

    ipv4_info = addrs[netifaces.AF_INET]

    addr = ipv4_info[0]['addr']
    netmask = ipv4_info[0]['netmask']

    subnet = ipaddress.ip_network(f'{addr}/{netmask}', strict=False)

    #print(subnet)
    
    return subnet,addr,netmask
    

@app.route('/register', methods = ['POST'])
def register():
    global registered
    #global update_process
    if(os.path.isfile(fname)) :
        abort(409)
    request_data = request.get_json()
    if(readUser(request_data['user_id']) is None) :
        abort(404)
        
    subnet,addr,netmask = get_ip_info()
    
    print(f"retrieved ip info: {subnet}, {addr}") 
    
    fridge_dictionary = {
        u'name': request_data['fridge_name'],
        u'items': [],
        u'tracking': [],
        u'image': '',
        u'last_updated': datetime.datetime.now(),
        u'ip_address': str(addr),
        u'subnet': str(subnet)
    }

    addFridge(request_data['user_id'], request_data['fridge_id'], fridge_dictionary)

    user_credentials = {
        "user_id": request_data['user_id'],
        "email": request_data['email'],
        "fridge_name": request_data['fridge_name'],
        "fridge_id": request_data['fridge_id'],
    }
    registered = True
    #thread = Thread(target=thread_task)
    #thread.daemon = True
    #with lock:
    user_credential_file = open(fname, "w+")
    #with open(fname, "w+") as user_credential_file:
    user_credential_file.write(json.dumps(user_credentials, indent=2))
    user_credential_file.close()
    
    subprocess.call(['cd /home/user/capstone-server && ./start_update_process.sh'], shell=True)
    #subprocess.call([''])
    #thread.start()
        #update_process = multiprocessing.Process(target=track_fridge_door, args=())
        #update_process.start()
    return user_credentials


@app.route('/deregister', methods = ['DELETE'])
def deregister():
    #global update_process
    if not(os.path.isfile(fname)) :
        abort(404)
    subprocess.call(['cd /home/user/capstone-server && ./stop_update_process.sh'], shell=True)
    with lock:
        #update_process.terminate()
        with open(fname, 'r') as user_credential_file:
            user_credentials = json.load(user_credential_file)
            deleteFridge(user_credentials['user_id'], user_credentials['fridge_id'])
            user_credential_file.close()
        os.remove(fname)
        return {
            "status": "removed"
        }


"""
def teardown_processes():
    print("tearing down processes")
    still_capture_mp_queue.put("end")
    update_process.join()
    consume_frames_process.join()
"""

if __name__ == "__main__":
    # Still capture multiprocessing queue
    try:
        app.run(host="0.0.0.0", debug=True)
    except KeyboardInterrupt:
        subprocess.call(['cd /home/user/capstone-server && ./stop_update_process.sh'], shell=True)
    finally:
        subprocess.call(['cd /home/user/capstone-server && ./stop_update_process.sh'], shell=True)

"""
    if(os.path.isfile(fname)):
        update_process.start()
        consume_frames_process.start() 
    try:
        app.run(host="0.0.0.0", threaded=True)
            #mp_queue_test(still_capture_mp_queue)
            #consume_frames(still_capture_mp_queue, captureInputQueue, stillQueue, detectionQueue)
    finally:
        teardown_processes()
        print("exited flask server")
"""
