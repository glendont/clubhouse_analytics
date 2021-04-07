import boto3
import time
import psutil
from botocore.config import Config

s3 = boto3.resource('s3')
textract = boto3.client('textract')
my_bucket = s3.Bucket('clubhouse-stats')

session = boto3.Session()
write_client = session.client('timestream-write', config=Config(
    read_timeout=20, max_pool_connections=5000, retries={'max_attempts': 10}))
query_client = session.client('timestream-query')

# Document
s3BucketName = "clubhouse-stats"

DATABASE_NAME = "Clubhouse"
TABLE_NAME = "participants"
USER = 1

def write(ActiveUser):

    dimensions = [
        {'Name': 'room', 'Value': "AWS Startups"},
        {'Name': 'Participant', 'Value': "Test"}
    ]

    records = []
    current_time = int(time.time() * 1000)

    records = {
        'Time': str(current_time),
        'Dimensions': dimensions,
        'MeasureName': "Active",
        'MeasureValue': 1,
        'MeasureValueType': 'DOUBLE'
    }

    if len(records) > 0:
      write_records(records)  

def write_records(records):
    try:
        result = write_client.write_records(DatabaseName=DATABASE_NAME,
                                            TableName=TABLE_NAME,
                                            Records=records,
                                            CommonAttributes={})
        status = result['ResponseMetadata']['HTTPStatusCode']
        print("Processed %d records. WriteRecords Status: %s" %
              (len(records), status))
    except Exception as err:
        print("Error:", err)


def extractText(file):
    # Call Amazon Textract
    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': file.key
            }
        })

    print("\nText\n========")
    text = ""
    skipText = ["All rooms", "Leave quietly", "Others in the room", "+"]
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            if item["Text"] not in skipText:
                write(item["Text"])
                print('' + item["Text"] + '')
                text = text + " " + item["Text"]


for file in my_bucket.objects.all():
    extractText(file)
