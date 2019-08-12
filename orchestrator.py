from flask import Flask, jsonify, request, abort,redirect, url_for , Response
import requests
import os
import re
import pickle
import threading
import sys
import time
from threading import Thread
cont_dict = {}
no_of_req = 0
first_req = 0
#lock_no_of_req = threading.Lock()
#cont_dict_lock = threading.Lock()
app = Flask(__name__)
cur_cont = 0

def init_container():
    con = os.popen("sudo docker run -p 8000:80 -d acts").read()
    con_real = con.rstrip()
    cont_dict[8000] = con_real

def fault_tolerance():
	print("Fault tolerance started",file=sys.stderr)
	while(1):
		#print("Fault",file=sys.stderr)
		time.sleep(1)
		active_cont = list(cont_dict.keys())
		for i in range(len(active_cont)):
			req = requests.get("http://127.0.0.1:"+str(active_cont[i])+"/api/v1/_health")
			if(req.status_code == 500):
				tmp = os.popen("sudo docker container kill " + cont_dict[active_cont[i]]).read()
				del(cont_dict[active_cont[i]])
				con = os.popen("sudo docker run -p " + str(active_cont[i]) + ":80 -d acts").read()
				con_real = con.rstrip()
				cont_dict[active_cont[i]] = con_real
				print("started a new container for "+str(active_cont[i]),file=sys.stderr)
        #cont_dict_lock.release()

def auto_scale():
	global no_of_req
	global first_req
	print('Hello world!', file=sys.stderr)
	while(first_req == 0):
		pass
	 

	while(1):
		time.sleep(120)
		num_cont_needed = (no_of_req // 20) + 1
		print(num_cont_needed)
		if(len(cont_dict) != num_cont_needed):
			if(len(cont_dict) < num_cont_needed):
				max_cont_id = max(list(cont_dict.keys()))
				extra_cont = num_cont_needed - len(cont_dict)
				for i in range(extra_cont):
					con = os.popen("sudo docker run -p " + str(max_cont_id + i + 1) + ":80 -d acts").read()
					con_real = con.rstrip()
					cont_dict[max_cont_id + i + 1] = con_real
					print(cont_dict,file=sys.stderr)
			else:
				max_cont_id = max(list(cont_dict.keys()))
				extra_cont = abs(num_cont_needed - len(cont_dict))
				while(extra_cont != 0):
					cont_id_kill = cont_dict[max_cont_id]
					tmp = os.popen("sudo docker container kill " + cont_id_kill).read()
					del(cont_dict[max_cont_id])
					max_cont_id = max_cont_id - 1
					extra_cont = extra_cont - 1
					print(cont_dict,file=sys.stderr)
		else:
			print("Same number of containers",file=sys.stderr)
		no_of_req = 0
		
@app.route('/api/v1/<route>', methods=['GET','POST','DELETE','PUT'])
def route_path(route):
		global cur_cont
		global first_req
		global no_of_req
		if(first_req == 0):
			first_req = 1
		cur_cont = (cur_cont + 1) % len(cont_dict)
		new_url="http://127.0.0.1:"+str(cur_cont+8000)+"/api/v1/"+route
		print(new_url)
		rqst=requests.request(
			method=request.method,
			url= new_url,
			headers={key: value for (key, value) in request.headers if key != 'Host'},
			data=request.get_data())
		headers = [(name, value) for (name, value) in rqst.raw.headers.items()]
		print("rqst : ", rqst.content, rqst.status_code, headers)
		response = Response(rqst.content, rqst.status_code, headers)
		no_of_req = no_of_req + 1
		return response


def common_route():
	app.run(host = '0.0.0.0', port = 80)

if __name__ == '__main__':
	init_container()
	#t2 = threading.Thread(target = fault_tolerance)
	#t2.start()
	thread_health=Thread(target=fault_tolerance)
	thread_autoscaling=Thread(target=auto_scale)
	thread_api=Thread(target=common_route)
	thread_health.start()
	thread_api.start()
	thread_autoscaling.start()
	#thread_health.join()
	#thread_api.join()
	#thread_autoscaling.join()
  

