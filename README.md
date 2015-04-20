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
					connectionString: "ssh -i tnt-auth-prod.pem ec2-user@54.227.77.235",
					instanceId: "i-90020b6a",
					launchTime: "2015-03-20T16:30:49.000Z",
					loadBalancer: "",
					privateIP: "10.109.145.44",
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
					connectionString: "ssh -i tnt-auth-prod.pem ec2-user@54.227.77.235",
					instanceId: "i-90020b6a",
					launchTime: "2015-03-20T16:30:49.000Z",
					loadBalancer: "",
					privateIP: "10.109.145.44",
					status: "running"
				}
			]
}
```