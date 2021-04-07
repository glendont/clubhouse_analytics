import boto3
import time
import re
import logging
import time
import datetime

from botocore.config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

s3 = boto3.resource('s3')
textract = boto3.client('textract')
my_bucket = s3.Bucket('clubhouse-stats')
session = boto3.Session()
write_client = session.client('timestream-write', config=Config(
    read_timeout=20, max_pool_connections=5000, retries={'max_attempts': 10}))
query_client = session.client('timestream-query')

# Document
s3BucketName = "clubhouse-stats"

ROOM = "AWS Startups"
# Format DD/MM/YYYY
DATE_OF_EVENT = "2-4-2021"
DATABASE_NAME = "Clubhouse"
TABLE_NAME = "participants"
USER = ""

def write(USER, ROOM_TIME):

  logging.debug("Preparing record for %s", USER)
  logging.info("The time is %s", ROOM_TIME)
  common_attributes = {
      'Dimensions': [
          {'Name': 'User', 'Value': USER},
          {'Name': 'Room', 'Value': ROOM}
    ]
  }

  record = [{
    'MeasureName': 'Active',
    'MeasureValue': '1',
    'Time': str(ROOM_TIME),
    'TimeUnit': "MILLISECONDS"
  }]

  try:
      result = write_client.write_records(DatabaseName=DATABASE_NAME, TableName=TABLE_NAME,
                                         Records=record, CommonAttributes=common_attributes)
      logging.info('Write Record: %(list_0)s - Status: %(list_1)s', { 'list_0': USER, 'list_1' : result['ResponseMetadata']['HTTPStatusCode'] })
  except write_client.exceptions.RejectedRecordsException as err:
      logging.error(err)
      for rr in err.response["RejectedRecords"]:
          print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
      logging.info("Other records were written successfully. ")
  except Exception as err:
      logging.error(err)
    

def extractText(file):
  # Call Amazon Textract
  response = textract.detect_document_text(
      Document={
          'S3Object': {
              'Bucket': s3BucketName,
              'Name': file.key
          }
      })

  text = ""
  skipText = ["All rooms", "Leave quietly", "Others in the room", "+"]

  # Regex to test extracted value to see if it's the phones clock
  isClock = re.compile('\d:\d')

  for item in response["Blocks"]:
      if item["BlockType"] == "LINE":
          if item["Text"] not in skipText:
              if isClock.match(item["Text"]):
                ROOM_TIME = str(round(time.mktime(datetime.datetime.strptime(DATE_OF_EVENT + " " + item["Text"], "%d-%m-%Y %H:%M").timetuple())*1000))
              else:
                write(item["Text"], ROOM_TIME)

for file in my_bucket.objects.all():
    extractText(file)
