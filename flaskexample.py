#!/usr/bin/python
from flask import Flask, jsonify, request
import boto.ec2
import json
from boto.ec2.autoscale import AutoScaleConnection
import memcache
import logging
from time import gmtime, strftime
from service.core import CoreService
app = Flask(__name__)
service=CoreService()

mc = memcache.Client(["127.0.0.1:11211"])
# logging.basicConfig(filename='flaskexample.log',filemode='aw',level=logging.INFO,format='%(asctime)-15s %(message)s', datefmt=strftime("%Y-%m-%d %H:%M:%S:%f %z", gmtime()))

#given an instance id give connection string associated with it
@app.route("/instances/<instanceid>")
def describeInstance(instanceid):
	responseJSON = service.generateResponse(instanceid)
	if len(responseJSON) < 1:
		response=jsonify({'message':'Instance not found'})
		response.status_code=404
	else:
		response=jsonify(**{eval('instanceid'): responseJSON})
		response.status_code=200
	return response

@app.route("/keypairs")
def describeKeyPair():
	return service.get_all_key_pairs()



#given a elastic beanstalk environment name tag give all instances associated with it
@app.route("/tags/")
def getTaggedInstances():
	tag=request.args.get('tag')
	if not mc.get(tag.encode('utf-8')):
		# app.logger.info('Not available in cache' )
		responseJSON=service.get_all_tagged_instances_metadata(tag)
		if len(responseJSON) < 1:
			response=jsonify({'message':'Instance not found'})
			response.status_code=404
		else:
			response=jsonify(**{eval('tag'): responseJSON})
			response.status_code=200
	else:
		# app.logger.info('Found in cache')
		responseJSON = mc.get(tag.encode('utf-8'))
		# app.logger.info(responseJSON)
		response=jsonify(**{eval('tag'): responseJSON})
		response.status_code=200

	return response		


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