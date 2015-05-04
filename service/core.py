import boto.ec2
import json
from boto.ec2.autoscale import AutoScaleConnection
class CoreService:
	def __init__(self):
		self.ec2=boto.ec2.connect_to_region('us-east-1')
		self.asg=AutoScaleConnection()
		self.ebs=boto.connect_beanstalk()

	def getConnectionString(self,ipaddress,keyname,ami_id):
		if ami_id in ['ami-8c6c28e4', 'ami-3ec17756']:
			user=self.getUserForAMIId(ami_id)
		else:
			user=self.getUserForAMIId(ami_id)
		connectionString = 'ssh -i '+keyname+'.pem'+' '+user+'@'+ipaddress+', '
		return connectionString

	def getConnectedELB(self,application_name,ebsid,ebsenvname):
		print "application_name: "+ str(application_name) + " ebsid: "+ str(ebsid) + " ebsenvname: "+ str(ebsenvname)
		environments = self.ebs.describe_environments(application_name=application_name,environment_ids=ebsid)
		print environments
		if len(environments['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments'])>0:
			return environments['DescribeEnvironmentsResponse']['DescribeEnvironmentsResult']['Environments'][0]['CNAME']
		else:
			return ""


	def getUserForAMIId(self,ami_id):
		image=self.ec2.get_image(ami_id)
		if 'ubuntu' in image.name:
			return 'ubuntu'
		else:
			return 'ec2-user'

	def generateResponse(self,instanceid):
		filters={'instance-id':instanceid}
		reservations=self.ec2.get_all_instances(filters=filters)
		response=''
		responseJSON = []
		for r in reservations:
			for inst in r.instances:
				if instanceid==inst.id:
					resJson = {
						'connectionString': self.getConnectionString(inst.ip_address,inst.key_name,inst.image_id)[:-2],
						'loadBalancer': self.getConnectedELB(inst.tags.get('service-name',None),
								inst.tags.get('elasticbeanstalk:environment-id',None), inst.tags.get('elasticbeanstalk:environment-name', None)),
						'privateIP': inst.private_ip_address,
						'instanceId': inst.id,
						'launchTime': inst.launch_time,
						'status': inst.state
					}
					responseJSON.append(resJson)
		return responseJSON

	def get_all_key_pairs(self):
		keys=self.ec2.get_all_key_pairs()
		body = {}
		for key in keys:
			print key.name
			if len(body)>0:
				body['keys'].append(key.name+".pem")
			else:
				body['keys'] = [key.name+".pem"]
		return json.dumps(body)

	def get_all_tagged_instances_metadata(self,tag):
		filters={"tag-value": tag}
		reservations=ec2.get_all_instances(filters=filters)
		connectionString=''
		responseJSON=[]
		for r in reservations:
			for inst in r.instances:
				ebsenvname = inst.tags.get('elasticbeanstalk:environment-name', None) or inst.tags['Name']
				if ebsenvname is not None and tag in ebsenvname and inst.ip_address is not None:
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
		return responseJSON