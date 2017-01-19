from __future__ import print_function
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import datetime
import json


# These are my AWS IoT login and certificates
host = "**************.iot.us-east-1.amazonaws.com"
cert_path = "cert/"
rootCAPath = cert_path + "root-CA.crt"
certificatePath = cert_path + "**********-certificate.pem.crt"
privateKeyPath = cert_path + "**********-private.pem.key"
shadowClient = "DrinkMachine_Lambda" 

# Init AWSIoTMQTTClient
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(shadowClient)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec 


# --------------- Helpers that build all of the responses ----------------------
def create_attributes(DrinkChoice):
    return {"DrinkChoice": DrinkChoice}

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def Welcome_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("DrinkMachine", True)
    customCallback = ""

    # Set Session Attributes
    DrinkChoice = ''

    # Set other defaults
    card_title = "Welcome"
    should_end_session = False

    # Start the real task
   
    speech_output = "I am ready to pour you a drink. " \
                    "Would you like soda one, soda two, or mixed?"
    reprompt_text = "Would you like soda one, soda two, or mixed?" 

    if 'slots' in intent:
        if 'DrinkChoice' in intent['slots']:
            if 'value' in intent['slots']['DrinkChoice']:
                DrinkChoice = intent['slots']['DrinkChoice']['value']

                speech_output = "Did you put a cup in to receive " + DrinkChoice
                reprompt_text = "Did you put a cup in to receive " + DrinkChoice

              

    # Publish to AWS IoT Shadow 
    
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Start\": \"NO\", "\
                                                    "\"DrinkChoice\": \"" + DrinkChoice + "\" "\
                                                "} "\
                                    ", \"reported\": {"\
                                                    "\"Start\": \"NO\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()
    
    # Send response back to the Alexa Voice Skill
    session_attributes = create_attributes(DrinkChoice)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def DrinkChoice_response(intent, session):
    # Connect to AWS IoT Shadow
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("DrinkMachine", True)
    customCallback = ""
    
    # Set Session Attributes
    if 'attributes' in session:
        if 'DrinkChoice' in session['attributes']:
            DrinkChoice = session['attributes']['DrinkChoice']
        else:
            DrinkChoice = ''
       
    else:
        DrinkChoice = ''
        

    # Set other defaults
    card_title = "DrinkChoice"
    should_end_session = False
    
    speech_output = "I didn't understand. What kind of drink do you want? " \
                    "Would you like me to pour soda one, soda two, or mixed"
    reprompt_text = "Choose either soda one, soda two, or mixed."
    # Start the real task
    if 'slots' in intent:
        if 'DrinkChoice' in intent['slots']:
            if 'value' in intent['slots']['DrinkChoice']:
                DrinkChoice = intent['slots']['DrinkChoice']['value']

                speech_output = "Did you put a cup in to receive " + DrinkChoice
                reprompt_text = "Did you put a cup in to receive " + DrinkChoice

    
    
    

    

    
        
    # Publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Start\": \"NO\", "\
                                                    "\"DrinkChoice\": \"" + DrinkChoice + "\" "\
                                                "} "\
                                    ", \"reported\": {"\
                                                    "\"Start\": \"NO\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()


    # Send response back to the Alexa Voice Skill
    session_attributes = create_attributes(DrinkChoice)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def Ready_response(intent, session):
    # Connect to AWS IoT Shadow 
    
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("DrinkMachine", True)
    customCallback = ""

    # Set Session Attributes
    if 'attributes' in session:
        if 'DrinkChoice' in session['attributes']:
            DrinkChoice = session['attributes']['DrinkChoice']
        else:
            DrinkChoice = ''
    
    else:
        DrinkChoice = ''

    # Set other defaults
    card_title = "StartPouring"
    should_end_session = True

    # Start the real task
    if DrinkChoice <> "":
        speech_output = "Pouring " + DrinkChoice + " now."
        reprompt_text = ""

        # Publish to AWS IoT Shadow
        
        myJSONPayload = "{ \"state\" : {"\
                                      "\"desired\": {"\
                                                     "\"Start\": \"YES\", "\
                                                     "\"DrinkChoice\": \"" + DrinkChoice + "\" "\
                                                  "} "\
                                  "} "\
                   "}"
        myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
        myAWSIoTMQTTShadowClient.disconnect()

    else:
        speech_output = "Something went wrong, please start over by asking for Help"
        reprompt_text = "Something went wrong, please start over by asking for Help"

    # Send response back to the Alexa Voice Skill
    session_attributes = create_attributes(DrinkChoice)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def NotReady_response(intent, session):
    # Connect to AWS IoT Shadow
    
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("DrinkMachine", True)
    customCallback = ""

    # Set Session Attributes
    if 'attributes' in session:
        if 'DrinkChoice' in session['attributes']:
            DrinkChoice = session['attributes']['DrinkChoice']
        else:
            DrinkChoice = ''
    else:
        DrinkChoice = ''

    # Set other defaults
    card_title = "NotReady"
    should_end_session = False
    
     # Publish to AWS IoT Shadow
    myJSONPayload = "{ \"state\" : {"\
                                    "\"desired\": {"\
                                                    "\"Start\": \"NO\", "\
                                                    "\"DrinkChoice\": \"" + DrinkChoice + "\" "\
                                                "} "\
                                    ", \"reported\": {"\
                                                    "\"Start\": \"NO\" "\
                                                "} "\
                                    "} "\
                    "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    myAWSIoTMQTTShadowClient.disconnect()

    # Start the real task
    speech_output = "Put a cup underneath the nozzle so you don't spill. " \
                    "I will wait for you, tell me when you are ready"
    reprompt_text = "Hurry up i don't have all day, tell me when you are ready"

    # Send response back to the Alexa Voice Skill
    session_attributes = create_attributes(DrinkChoice)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def Stop_response():
    session_attributes = {}
    card_title = "Stop"

    # Setting this to true ends the session and exits the skill.
    should_end_session = True

    DrinkChoice = ''

    speech_output = "I'm done making drinks for you, you're welcome."
    reprompt_text = None

    # Connect and publish to AWS IoT Shadow
    
    myAWSIoTMQTTShadowClient.connect()
    myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("DrinkMachine", True)
    customCallback = ""
    myJSONPayload = "{ \"state\" : {"\
                                "\"desired\": {"\
                                                "\"Start\": \"NO\", "\
                                                "\"DrinkChoice\": \"\" "\
                                            "} "\
                                "} "\
                "}"
    myDeviceShadow.shadowUpdate(myJSONPayload, customCallback, 5)
    session_attributes = create_attributes(DrinkChoice)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PourDrink":
        return DrinkChoice_response(intent, session)
    elif intent_name == "WelcomeIntent":
        return Welcome_response(intent, session)
    elif intent_name == "ReadyIntent":
        return Ready_response(intent, session)
    elif intent_name == "NotReadyIntent":
        return NotReady_response(intent, session)
    elif intent_name == "StopIntent":
        return Stop_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
  
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.**********"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])


    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
