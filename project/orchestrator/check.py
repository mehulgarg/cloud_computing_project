#! encoding=utf-8
import docker
from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1', 27017)
db = client['container_meta']
col = db.containers

dockers = docker.from_env()
new_container=dockers.containers.run('acts',detach=1,volumes={"/home/ubuntu/project": {"bind": "/home/ubuntu/","mode": "rw"}},environment=["TEAM_ID=CC_189_206_229_232​"],links={'mongo':'mongo'},network='my-network',ports={'80/tcp':8000})
col.insert_one({'id':new_container.id,'port':8000,'current':1,'active':1})

'''new_container=dockers.containers.run('acts',detach=1,environment=["TEAM_ID=CC_189_206_229_232"],publish_all_ports = True,links={'mongo':'mongo'},network='my-network',ports={'80/tcp':8001})
col.insert_one({'id':new_container.id,'port':8001,'current':0,'active':1})

new_container=dockers.containers.run('acts',detach=1,environment=["TEAM_ID=CC_189_206_229_232"],publish_all_ports = True,links={'mongo':'mongo'},network='my-network',ports={'80/tcp':8002})
col.insert_one({'id':new_container.id,'port':8002,'current':0,'active':1})
'''