# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.  
# SPDX-License-Identifier: Amazon Software License
# Licensed under the Amazon Software License http://aws.amazon.com/asl/

# Enriches CloudWatch alarm SNS message with Cloudwatch alarm tags and
# reformats the default alarm message payload before republishing to another SNS topic

# To use this:
# - Set the ACCOUNT_ID and REGION environment variables
# - Ensure the IAM role has permissions to publish to SNS 
# - Replace 'LambdaPostProcessingSNSTopic' with your SNS topic name

# Python 3.11.4

import json
import boto3
import os

sns = boto3.client('sns')
 
def lambda_handler(event, context):
    message_payload = json.loads(event['Records'][0]['Sns']['Message'])
    timestamp_payload = (event['Records'][0]['Sns']['Timestamp'])
    alarm_name = message_payload['AlarmName']
    region = message_payload['Region']
    alarm_description = message_payload['AlarmDescription']
    new_state_value = message_payload['NewStateValue']
    state_change_time = message_payload['StateChangeTime']
    alarmarn = message_payload['AlarmArn']
    timestamp = timestamp_payload
    newstatereason = message_payload['NewStateReason']
    account_id = message_payload['AWSAccountId']
    name_space = message_payload['Trigger']['Namespace']
    # subject = f"ALARM: {alarm_name} in {region} is {new_state_value}"
    dimensions = message_payload['Trigger']['Dimensions']
    
    # Get alarm tags
    cloudwatch = boto3.client('cloudwatch')
    alarm_tags = cloudwatch.list_tags_for_resource(ResourceARN=alarmarn)['Tags']
    
    # Build tag strings
    alarm_tag_str = ""
    for tag in alarm_tags:
        alarm_tag_str += f" {tag['Key']}: {tag['Value']}\n"
    
    message = (
        f"Alarm Name: {alarm_name}\n"
        f"Region: {region}\n"
        f"New State Value: {new_state_value}\n"
        f"Description: {alarm_description}\n"
        f"State Change Time: {state_change_time}\n"
        f"AlarmArn: {alarmarn}\n"
        f"Timestamp: {timestamp}\n"
        f"NewStateReason: {newstatereason}\n"
        f"AWSAccountId: {account_id}\n"
        f"Namespace: {name_space}\n"
        f"Dimensions: {dimensions}\n"
        f"Alarm Tags: \n{alarm_tag_str}\n"
)
    
    account_id = os.environ["ACCOUNT_ID"]
    region = os.environ["REGION"]
    
    topic_arn = f"arn:aws:sns:{region}:{account_id}:LambdaPostProcessingSNSTopic"
    response = sns.publish(TopicArn=topic_arn, Message=message)
    
    print("Message published")
    return(response)

