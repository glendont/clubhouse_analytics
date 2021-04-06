clubhouse_analytics
===================

As of April 2021, Clubhouse does not expose any analytics to show basic stats
such as average listener/participant time, max users, average users, regulars,
and more. This is a quick hack project to test a proof of concept to generate
this data off of screenshots.

1.  Periodically I screen shot the room during a Clubhouse event

2.  I upload these screenshots to a S3 bucket

3.  Amazon Textract extracts the timestamp of the phone and all names of users
    in the event

4.  This data populates a timeseries database in Amazon Timestream

5.  This data provides when a user was first seen, last seen, average count in
    the room, max count in the room, and additional metrics that may be of
    interest.

Currently there is no cloudformation to populate the infrastructure which I may
add. I am crossing my fingers that analytics gets released and I can just
archive this project. If you are interested in using it, the core pieces you
need are:

1.  AWS Account

2.  Textract, S3, Timestream

3.  Quicksight/Grafana if you want to create dashboards
