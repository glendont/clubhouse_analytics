import json
import boto3
import time
import re
import logging
import time
import datetime
from botocore.config import Config
import urllib.parse
import os 

def lambda_handler(event, context):

        # Initialise environment variables 
        ROOM = os.environ['ROOM_NAME']
        DATABASE_NAME = os.environ['DATABASE_NAME']
        TABLE_NAME = os.environ['TABLE_NAME']
        DATE_OF_EVENT=os.environ['DATE']

        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        file_name = key.split('/')[-1]
        bucket = event['Records'][0]['s3']['bucket']['name']
        
        print('Bucket:', bucket)
        print('Filename:', file_name)
        
        s = boto3.Session()
        s3 = boto3.resource('s3')
        my_bucket = s3.Bucket(bucket)
        
        for list_files in my_bucket.objects.all():
            if (list_files.key==file_name):
              file = list_files
              break

        # Call Amazon Textract
        textract = boto3.client('textract')
        response = textract.detect_document_text(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': file_name
                }
            })
            
        write_client = s.client('timestream-write', config=Config(
        read_timeout=20, max_pool_connections=5000, retries={'max_attempts': 10}))
        query_client = s.client('timestream-query')

        text = ""
        skipText = ["All rooms", "Leave quietly", "Others in the room", "+","Followed by the speakers",'Hallway','7','*','0000','02']

        # Regex to test extracted value to see if it's the phones clock
        isClock = re.compile('\d:\d')

        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                if item["Text"] not in skipText:
                    if isClock.match(item["Text"]):
                      ROOM_TIME = item["Text"]
                      MODIFIED_TIME = str(round(time.mktime(datetime.datetime.strptime(DATE_OF_EVENT + " " + item["Text"], "%d-%m-%Y %H:%M").timetuple())*1000))
                    else:
                        ## Write data into Timestream database
                        USER = item["Text"]
                        logging.debug("Preparing record for %s", USER)
                        logging.info("The time is %s", ROOM_TIME)
                        common_attributes = {
                            'Dimensions': [
                                {'Name': 'User', 'Value': USER},
                                {'Name': 'Room', 'Value': ROOM},
                                {'Name': "Timestamp", 'Value': ROOM_TIME},
                          ]
                        }
                        record = [{
                          'MeasureName': 'Active',
                          'MeasureValue': '1',
                          'Time': str(MODIFIED_TIME),
                          'TimeUnit': "MILLISECONDS"
                        }]

                        try:
                            result = write_client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,Records=record, CommonAttributes=common_attributes)
                            logging.info('Write Record: %(list_0)s - Status: %(list_1)s', { 'list_0': USER, 'list_1' : result['ResponseMetadata']['HTTPStatusCode'] })
                        except write_client.exceptions.RejectedRecordsException as err:
                            logging.error(err)
                            for rr in err.response["RejectedRecords"]:
                                print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
                            logging.info("Other records were written successfully. ")
                        except Exception as err:
                            logging.error(err)
                        
     