"""
You must have an AWS account to use the Amazon Connect CTI Adapter.
Downloading and/or using the Amazon Connect CTI Adapter is subject to the terms of the AWS Customer Agreement,
AWS Service Terms, and AWS Privacy Notice.

© 2017, Amazon Web Services, Inc. or its affiliates. All rights reserved.

NOTE:  Other license terms may apply to certain, identified software components
contained within or distributed with the Amazon Connect CTI Adapter if such terms are
included in the LibPhoneNumber-js and Salesforce Open CTI. For such identified components,
such other license terms will then apply in lieu of the terms above.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import json
import base64
import logging
from salesforce import Salesforce

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.environ["LOGGING_LEVEL"]))

def lambda_handler(event, context):
    try:
        logger.info('Start CTR Sync Lambda')
        logger.info('Event: {}'.format(event))

        process_ctr_record(event['record'])

        return "Done"

    except Exception as e:
        raise e


def process_ctr_record(record):

    decoded_payload = base64.b64decode(record).decode('utf-8')
    recordObj = json.loads(decoded_payload)
    logger.info('DecodedPayload: {}'.format(recordObj))

    if ('postcallCTRImportEnabled' in recordObj["Attributes"] and recordObj["Attributes"]["postcallCTRImportEnabled"] == 'true'):
        logger.info('postcallCTRImportEnabled = true')
        create_ctr_record(recordObj)


def create_ctr_record(ctr):


    objectnamespace = os.environ['SF_ADAPTER_NAMESPACE']

    if not objectnamespace or objectnamespace == '-':
        logger.info("SF_ADAPTER_NAMESPACE is empty")
        objectnamespace = ''
    else:
        objectnamespace = objectnamespace + "__"

    sfRequest = {}

    sfRequest[objectnamespace + 'AWSAccountId__c'] = ctr['AWSAccountId']

    if not ctr['Agent'] == "":
        sfRequest[objectnamespace + 'AfterContactWorkDuration__c'] = ctr['Agent']['AfterContactWorkDuration']
        sfRequest[objectnamespace + 'AfterContactWorkEndTimestamp__c'] = ctr['Agent']['AfterContactWorkEndTimestamp']
        sfRequest[objectnamespace + 'AfterContactWorkStartTimestamp__c'] = ctr['Agent']['AfterContactWorkStartTimestamp']
        sfRequest[objectnamespace + 'AfterContactWorkStartTimestamp__c'] = ctr['Agent']['AfterContactWorkStartTimestamp']
        sfRequest[objectnamespace + 'AgentConnectedToAgentTimestamp__c'] = ctr['Agent']['ConnectedToAgentTimestamp']
        sfRequest[objectnamespace + 'AgentInteractionDuration__c'] = ctr['Agent']['AgentInteractionDuration']
        sfRequest[objectnamespace + 'AgentCustomerHoldDuration__c'] = ctr['Agent']['CustomerHoldDuration']
        sfRequest[objectnamespace + 'AgentHierarchyGroups__c'] = ctr['Agent']['HierarchyGroups']
        sfRequest[objectnamespace + 'AgentLongestHoldDuration__c'] = ctr['Agent']['LongestHoldDuration']
        sfRequest[objectnamespace + 'AgentNumberOfHolds__c'] = ctr['Agent']['NumberOfHolds']
        if not ctr['Agent']['RoutingProfile'] == "":
            sfRequest[objectnamespace + 'AgentRoutingProfileARN__c'] = ctr['Agent']['RoutingProfile']['ARN']
            sfRequest[objectnamespace + 'AgentRoutingProfileName__c'] = ctr['Agent']['RoutingProfile']['Name']

        sfRequest[objectnamespace + 'AgentUsername__c'] = ctr['Agent']['Username']

        sfRequest[objectnamespace + 'AgentConnectionAttempts__c'] = ctr['AgentConnectionAttempts']
        sfRequest[objectnamespace + 'Attributes__c'] = json.dumps(ctr['Attributes'])
        sfRequest[objectnamespace + 'Channel__c'] = ctr['Channel']
        sfRequest[objectnamespace + 'InitiationTimestamp__c'] = ctr['InitiationTimestamp']
        sfRequest[objectnamespace + 'InitialContactId__c'] = ctr['InitialContactId']
        sfRequest[objectnamespace + 'Initiation_Method__c'] = ctr['InitiationMethod']
        sfRequest[objectnamespace + 'InitiationTimestamp__c'] = ctr['InitiationTimestamp']
        sfRequest[objectnamespace + 'InstanceARN__c'] = ctr['InstanceARN']
        sfRequest[objectnamespace + 'LastUpdateTimestamp__c'] = ctr['LastUpdateTimestamp']
        sfRequest[objectnamespace + 'NextContactId__c'] = ctr['NextContactId']
        sfRequest[objectnamespace + 'PreviousContactId__c'] = ctr['PreviousContactId']

    # Queue
    if not ctr['Queue'] == "":
        sfRequest[objectnamespace + 'QueueARN__c'] = ctr['Queue']['ARN']
        sfRequest[objectnamespace + 'QueueDequeueTimestamp__c'] = ctr['Queue']['DequeueTimestamp']
        sfRequest[objectnamespace + 'QueueDuration__c'] = ctr['Queue']['Duration']
        sfRequest[objectnamespace + 'QueueEnqueueTimestamp__c'] = ctr['Queue']['EnqueueTimestamp']
        sfRequest[objectnamespace + 'QueueName__c'] = ctr['Queue']['Name']

    # Recording
    if not ctr['Recording'] != "None":
        sfRequest[objectnamespace + 'RecordingLocation__c'] = ctr['Recording']['Location']
        sfRequest[objectnamespace + 'RecordingStatus__c'] = ctr['Recording']['Status']
        sfRequest[objectnamespace + 'RecordingDeletionReason__c'] = ctr['Recording']['DeletionReason']

    # System End Data
    if not ctr['SystemEndpoint'] == "":
        sfRequest[objectnamespace + 'SystemEndpointAddress__c'] = ctr['SystemEndpoint']['Address']

    # Transfer Data
    sfRequest[objectnamespace + 'TransferCompletedTimestamp__c'] = ctr['TransferCompletedTimestamp']
    sfRequest[objectnamespace + 'TransferredToEndpoint__c'] = ctr['TransferredToEndpoint']

    logger.info(f'Record : {sfRequest}')

    sf = Salesforce()
    sf.sign_in()
    sf.update_by_external(objectnamespace + "AC_ContactTraceRecord__c", objectnamespace + 'ContactId__c',ctr['ContactId'], sfRequest)

    logger.info(f'Record Created Successfully')