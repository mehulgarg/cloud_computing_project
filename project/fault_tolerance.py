import os
from flask import Flask,request,jsonify,make_response,Response
from flask_restful import Resource, Api
from pymongo import MongoClient,ReturnDocument
import re
import base64
from datetime import datetime
from flask_restful import reqparse
import os
import copy
import requests
import json
import docker
import threading
import time

instance_ip='http://54.172.183.151'

client = MongoClient('mongodb://127.0.0.1', 27017)





# this should  be running for all containers
def fault_check():

    threading.Timer(1.0, fault_check).start()

    client = MongoClient('mongodb://127.0.0.1', 27017)
    db = client.container_meta
    col = db.containers


    client2 = docker.from_env()

    container_list = list(col.find())
    for i in range(len(container_list)):
        port_no = col.find()[i]['port']
        res = requests.get('http://127.0.0.1:'+str(port_no)+'/api/v1/_health')
         

        if(res.statuscode == 200):
            continue
        elif(res.statuscode == 500):
            print("\nhealthcheck == 500\n")

            #if the one which is serving the requests fails
            if(col.find()[i]['current']==1):
                next_port = col.find_one({"port":port_no+1})
                if(next_port):
                    res = requests.get('http://127.0.0.1:'+str(next_port)+'/api/v1/_health')
                    if(res.statuscode==200):
                        col.update_one({"port":port_no+1},{'$set': {'current':1}})
                        col.update_one({"port":port_no},{'$set': {'current':0}})
                        # **************    trigger appropriate action to the load balancer to direct to this container
                else:
                    col.update_one({"port":8000},{'$set': {'current':1}})
                    col.update_one({"port":port_no},{'$set': {'current':0}})

            #to replace this container with a new one
            id_of_container=col.find_one({'port':port_no})['id']
            container_remove=client2.containers.get(id_of_container)
            container_remove.stop(timeout=1)
            client2.containers.prune()
            print('finished removing')

            #adding a new container
            new_container=client2.containers.run('cc_acts_web',detach=1,environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':port_no})
            # check the image name once

            print('finished adding and the id is',new_container.id)
            col.update_one({"port":port_no},{'$set': {'id':new_container.id}})
    
        

fault_check()
    

            

 # time.sleep(1.0 - ((time.time() - starttime) % 1.0))












