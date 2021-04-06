Clubhouse Analytics
===================

As of April 2021, Clubhouse does not expose any analytics to show basic stats
such as average listener/participant time, max users, average users, regulars,
and more. This is a quick hack project to test a proof of concept to generate
this data off of screenshots.

1.  Periodically screenshot the room during a Clubhouse event

2.  Upload screenshots to a S3 bucket

3.  Run this script. Amazon Textract extracts the timestamp of the screenshot in the image and all usernames active in the event. Data is populated into Amazon Timestream.

5.  Query to generate analytics. There is enough data to identify: when a user was first seen, last seen, average count in the room, max count in the room, and other metrics.

Currently there is no cloudformation to populate the infrastructure. I may spend the time to add this, but ultimately this is just a quick hack side project. I am crossing my fingers that analytics gets released and I can just archive this project. If you are interested in using it, the core pieces you
need are:

1.  AWS Account

2.  Textract, S3, Timestream

3.  Quicksight/Grafana if you want to create dashboards

![Alt text](/images/Textract.png?raw=true "Textract in Action")

Examples:

Timestream query:
```
select Participant,
       count(time) as Occurences,
       min(time) start_time,
       max(time) end_time
from "Clubhouse"."participants"
group by Participant
```

Provides:

```
Participant Occurences start_time end_time
Chandra	    3	2021-04-01 10:56:00.000000000	2021-04-01 11:22:00.000000000
Sunny	    1	2021-04-01 10:45:00.000000000	2021-04-01 10:45:00.000000000
Alexander   2	2021-04-01 10:45:00.000000000	2021-04-01 11:22:00.000000000
Sidney      3	2021-04-01 10:45:00.000000000	2021-04-01 11:11:00.000000000
Raquel      3	2021-04-01 10:56:00.000000000	2021-04-01 11:22:00.000000000
Parsa       1	2021-04-01 10:56:00.000000000	2021-04-01 10:56:00.000000000
Patrick     4	2021-04-01 10:45:00.000000000	2021-04-01 11:22:00.000000000
Ricky       1	2021-04-01 10:56:00.000000000	2021-04-01 10:56:00.000000000
CANROR      1	2021-04-01 10:56:00.000000000	2021-04-01 10:56:00.000000000
Rob         1	2021-04-01 11:22:00.000000000	2021-04-01 11:22:00.000000000
```