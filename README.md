A standalone python flask app. 

To run this app locally, 

```python flaskexample.py```

Given instance id gets the connection string for that instance.

Usage: 
``` /instances/<instance-id> [GET]```

Response: 
```
{
	instanceid: [
				{
					connectionString: "ssh -i KEYNAME.pem ec2-user@55.255.255.255",
					instanceId: "i-abcdefgh",
					launchTime: "2015-03-20T16:30:49.000Z",
					loadBalancer: "app.elasticbeanstalk.com",
					privateIP: "10.10.10.0",
					status: "running"
				}
			]
}
```

Given a tag, gets all instances connection string, comma separated, that are associated with that instance.

Usage: 
```/tags?tag=<tagname> [GET]```

Response:
```
{
	tagname: [
				{
					connectionString: "ssh -i KEYNAME.pem ec2-user@55.255.255.255",
					instanceId: "i-abcdefgh",
					launchTime: "2015-03-20T16:30:49.000Z",
					loadBalancer: "app.elasticbeanstalk.com",
					privateIP: "10.10.10.0",
					status: "running"
				}
			]
}
```