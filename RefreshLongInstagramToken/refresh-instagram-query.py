import json
from os import environ
import botocore.vendored.requests as requests
import pymssql
import logging
import traceback

endpoint=environ.get('ENDPOINT')
port=environ.get('PORT')
dbuser=environ.get('DBUSER')
password=environ.get('DBPASSWORD')
database=environ.get('DATABASE')


logger=logging.getLogger()
logger.setLevel(logging.INFO)

def make_connection():
	return pymssql.connect(server=endpoint, user=dbuser, password=password,
	port=int(port), database=database, autocommit=True)

def log_err(errmsg):
	logger.error(errmsg)
	return {"body": errmsg, "headers": {}, "statusCode": 400,"isBase64Encoded":"false"}
logger.info("Cold start complete.") 

def handler(event, context):
    header = {'content-type': 'application/x-www-form-urlencoded'}
    queryBookingsCompletion=""" select ISNULL(PersonalTrainer.instagramAccessToken,Client.instagramAccessToken) AS access_token,CASE WHEN Client.accountId is not null THEN 'Client' else 'Trainer' end as Type,ISNULL(Client.clientId,PersonalTrainer.ptId) as Id,AR.accountId
  FROM AccountInstagramTokenRefresh as AR
  LEFT JOIN Client on AR.accountId=Client.accountId
  LEFT JOIN PersonalTrainer on AR.accountId=PersonalTrainer.accountId
  WHERE AR.lastRefreshDate <= dateadd(day,-50,getdate()) and (PersonalTrainer.instagramAccessToken is not null or Client.instagramAccessToken is not null)"""
  
    try:
        cnx = make_connection()
        cursor=cnx.cursor()
        innerCursor=cnx.cursor()
        try:
            cursor.execute(queryBookingsCompletion)
        
        except:
            return log_err ("ERROR: Cannot execute cursor.\n{}".format(
                traceback.format_exc()) )
        r=[]
        results_list = []
        for result in cursor:
            try:
                urlLongToken = "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token="+result[0]
                jsonData = requests.get(urlLongToken,headers=header).text
                convertedJson = json.loads(jsonData)
                instagramAccessToken = convertedJson["access_token"]
                if result[1] == 'Trainer':
                    queryUpdateToken = "exec refreshTrainerInstagramToken 'x','"+str(instagramAccessToken)+"','"+str(result[2])+"'"
                elif result[1] == 'Client':
                    queryUpdateToken = "exec refreshClientInstagramToken 'x','"+str(instagramAccessToken)+"','"+str(result[2])+"'"
                innerCursor.execute(queryUpdateToken)
            except:
                pass
        cursor.close()
        innerCursor.close()
        return {"body":  "Successful Run: "+str(results_list), "headers": {}, "statusCode": 200,
        "isBase64Encoded":"false"}
    except:
    	return log_err("ERROR: Cannot connect to database from handler.\n{}".format(
    		traceback.format_exc()))
    finally:
    	try:
    		cnx.close()
    	except:
    		pass
				
if __name__== "__main__":
	handler(None,None)
			