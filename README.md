A standalone python flask app. 

Given instance id gets the connection string for that instance.
Usage: /instances/<instance-id> [GET]
Response: 
{
	connectionString: "ssh -i {key-pair} {user}@{ip_address}"
}

Given a tag, gets all instances connection string, comma separated, that are associated with that instance.
Usage: /tags?tag=<tagname>
Response:
{
	connectionString: "ssh -i {key-pair} {user}@{ip_address}, ssh -i {key-pair} {user}@{ip_address}"	
}