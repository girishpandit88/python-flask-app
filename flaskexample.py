# flaskexample.py
#!/usr/bin/python

from flask import Flask, jsonify, request
import boto.ec2
import json
import awsfabrictasks.ec2.api as awsfab

app = Flask(__name__)

ec2=boto.ec2.connect_to_region('us-east-1',aws_access_key_id='<aws_access_key_id>',aws_secret_access_key='<aws_secret_access_key')

#given an instance id give connection string associated with it
@app.route("/instances/<instanceid>")
def describeInstance(instanceid):
	reservations=ec2.get_all_instances(filters={'instance-id':instanceid})
	response=''
	for r in reservations:
		for inst in r.instances:
			if instanceid==inst.id:
				response= jsonify(connectionString=getConnectionString(inst.ip_address,inst.key_name,inst.image_id)[:-2])
				response.status_code = 200
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
	reservations=ec2.get_all_instances(filters={"tag-value": tag} )
	connectionString=''
	for r in reservations:
		for inst in r.instances:
			# print inst.tags
			ebsenvname = inst.tags['elasticbeanstalk:environment-name']
			if ebsenvname is not None and tag in ebsenvname and inst.ip_address is not None:
				connectionString+=getConnectionString(inst.ip_address,inst.key_name,inst.image_id)
	
	response= jsonify(connectionString=connectionString[:-2])
	response.status_code=200
	return response		

def getConnectionString(ipaddress,keyname,ami_id):
	if ami_id in ['ami-8c6c28e4', 'ami-3ec17756']:
		user=getUserForAMIId(ami_id)
	else:
		user=getUserForAMIId(ami_id)
	connectionString = 'ssh -i '+keyname+'.pem'+' '+user+'@'+ipaddress+', '
	return connectionString

def getUserForAMIId(ami_id):
	image=ec2.get_image(ami_id)
	if 'ubuntu' in image.name:
		return 'ubuntu'
	else:
		return 'ec2-user'

if __name__ == "__main__":
    app.run()

