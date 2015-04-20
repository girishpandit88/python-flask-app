#!/usr/bin/python
from flask import Flask, jsonify, request
import boto.ec2
import json
from boto.ec2.autoscale import AutoScaleConnection
import memcache
import logging
from time import gmtime, strftime

app = Flask(__name__)

ec2=boto.ec2.connect_to_region('us-east-1')
asg=AutoScaleConnection()
ebs=boto.connect_beanstalk()
mc = memcache.Client(["127.0.0.1:11211"])
logging.basicConfig(filename='flaskexample.log',filemode='aw',level=logging.INFO,format='%(asctime)-15s %(message)s', datefmt=strftime("%Y-%m-%d %H:%M:%S:%f %z", gmtime()))

#given an instance id give connection string associated with it
@app.route("/instances/<instanceid>")
def describeInstance(instanceid):
	reservations=ec2.get_all_instances(filters={'instance-id':instanceid})
	response=''
	responseJSON = []
	for r in reservations:
		for inst in r.instances:
			if instanceid==inst.id:
				resJson = {
					'connectionString': getConnectionString(inst.ip_address,inst.key_name,inst.image_id)[:-2],
					'loadBalancer': getConnectedELB(inst.tags.get('service-name',None),
							inst.tags.get('elasticbeanstalk:environment-id',None), inst.tags.get('elasticbeanstalk:environment-name', None)),
					'privateIP': inst.private_ip_address,
					'instanceId': inst.id,
					'launchTime': inst.launch_time,
					'status': inst.state
				}
				responseJSON.append(resJson)
	response=jsonify(**{eval('instanceid'): responseJSON})
	response.status_code=200
	return response

@app.route("/keypairs")
def describeKeyPair():
	keys = ec2.get_all_key_pairs()
	body = {}
	for key in keys:
		print key
		try:
			body['key'].append(key)
		except:
			body['key'] = [key]
	return str(body)


#given a elastic beanstalk environment name tag give all instances associated with it
@app.route("/tags/")
def getTaggedInstances():
	tag=request.args.get('tag')
	if not mc.get(tag.encode('utf-8')):
		app.logger.info('Not available in cache' )
		reservations=ec2.get_all_instances(filters={"tag-value": tag})
		connectionString=''
		responseJSON=[]
		for r in reservations:
			for inst in r.instances:
				ebsenvname = inst.tags.get('elasticbeanstalk:environment-name', None) or inst.tags['Name']
				print 'ebsenvname: '+ebsenvname
				if ebsenvname is not None and tag in ebsenvname and inst.ip_address is not None:
					connectionString=inst.ip_address
					resJson = {
						'connectionString': getConnectionString(inst.ip_address,inst.key_name,inst.image_id)[:-2],
						'loadBalancer': getConnectedELB(inst.tags.get('service-name',None),
							inst.tags.get('elasticbeanstalk:environment-id',None), inst.tags.get('elasticbeanstalk:environment-name', None)),
						'privateIP': inst.private_ip_address,
						'instanceId': inst.id,
						'launchTime': inst.launch_time,
						'status': inst.state
					}
					responseJSON.append(resJson)
		if len(responseJSON) > 0:
			mc.set(tag.encode('utf-8'),responseJSON)
		response=jsonify(**{eval('tag'): responseJSON})
		response.status_code=200
	else:
		app.logger.info('Found in cache')
		responseJSON = mc.get(tag.encode('utf-8'))
		app.logger.info(responseJSON)
		response=jsonify(**{eval('tag'): responseJSON})
		response.status_code=200

	return response		

def getConnectionString(ipaddress,keyname,ami_id):
	if ami_id in ['ami-8c6c28e4', 'ami-3ec17756']:
		user=getUserForAMIId(ami_id)
	else:
		user=getUserForAMIId(ami_id)
	connectionString = 'ssh -i '+keyname+'.pem'+' '+user+'@'+ipaddress+', '
	return connectionString

def getConnectedELB(application_name,ebsid,ebsenvname):
	print "application_name: "+ str(application_name) + " ebsid: "+ str(ebsid) + " ebsenvname: "+ str(ebsenvname)
	environments = ebs.describe_environments(application_name=application_name,environment_ids=ebsid)
	print environments
	if len(environments['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments'])>0:
		return environments['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments'][0]['CNAME']
	else:
		return ""


def getUserForAMIId(ami_id):
	image=ec2.get_image(ami_id)
	if 'ubuntu' in image.name:
		return 'ubuntu'
	else:
		return 'ec2-user'

@app.route("/asg/")
def getInstancesAssociatedWithASG():
	name=request.args.get('name')
	asgGroup = asg.get_all_groups(names=[name],max_records=10)
	print asgGroup.__dict__
	response = {
			'asgResponse': asgGroup.__dict__
	}
	return response

if __name__ == "__main__":
    app.run(debug=True)