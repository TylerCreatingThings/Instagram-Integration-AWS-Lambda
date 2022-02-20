import json
from os import environ
from botocore.exceptions import ClientError
import boto3
import botocore.vendored.requests as requests
import pymssql
import logging
import traceback

logger=logging.getLogger()
logger.setLevel(logging.INFO)

def log_err(errmsg):
	logger.error(errmsg)
	return {"body": errmsg, "headers": {}, "statusCode": 400,"isBase64Encoded":"false"}
logger.info("Cold start complete.") 

def handler(event, context):
    redirectUrl = "https://8hgwqd82hk.execute-api.ca-central-1.amazonaws.com/beta/instagramGetAuthorizationToken/"
    if vars[0] == "instagramGetAuthorizationToken":
        msgResponse = "Instagram Connection Succesful"
        try:
            redirectUrl = "https://8hgwqd82hk.execute-api.ca-central-1.amazonaws.com/beta/"
            url = 'https://api.instagram.com/oauth/access_token'
            header = {'content-type': 'application/x-www-form-urlencoded'}
            #accountType=Client,clientId=1
            state=event['queryStringParameters']['state']
            state = state.split(",")
            if state[0] == 'accountType=PersonalTrainer':
                state[1] = state[1][5:]
                redirectUrl = 'https://8hgwqd82hk.execute-api.ca-central-1.amazonaws.com/beta/instagramGetAuthorizationToken/'
                dataVars = {'client_id':'x','client_secret':'x','grant_type':'authorization_code','redirect_uri':redirectUrl,'code':event['queryStringParameters']['code']}
                jsonData = requests.post(url,headers=header, data=dataVars).text
                convertedJson = json.loads(jsonData)
                instagramAccessToken = convertedJson["access_token"]
                instagramId = convertedJson["user_id"]
                urlLongToken = "https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=x&access_token="+instagramAccessToken
                jsonData = requests.get(urlLongToken,headers=header).text
                convertedJson = json.loads(jsonData)
                instagramAccessToken = convertedJson["access_token"]
                query = "exec connectTrainerInstagram 'x','"+str(instagramId)+"','"+str(instagramAccessToken)+"','"+str(state[1])+"'"
        except Exception as e:
            return log_err ("ERROR: Improper API Format.\n{}"+str(e).format(
                traceback.format_exc()))
    else:
        return log_err ("ERROR: Improper API Format.\n{}"+vars[0].format(
            traceback.format_exc()) )

if __name__== "__main__":
	handler(None,None)
			