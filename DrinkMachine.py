from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import sys
import time
import json
import os
import RPi.GPIO as GPIO


# These are my AWS IoT login and certificates
host = "***************.iot.us-east-1.amazonaws.com"
cert_path = os.path.realpath(__file__).rstrip(os.path.basename(__file__)) + "cert/"
rootCAPath = cert_path + "root-CA.crt"
certificatePath = cert_path + "**********-certificate.pem.crt"
privateKeyPath = cert_path + "**********-private.pem.key"
shadowClient = "DrinkMachine_RaspberryPi"

# Parameters
DrinkChoice = ["", "soda 1", "soda 2", "mixed", "mixed drink"]
DrinkChoice_Selected = DrinkChoice.index("")

ReadyStatus = ["NO", "YES"]
ReadyStatus_Selected = ReadyStatus.index("NO")

def IoT_to_Raspberry_Change_DrinkChoice(ShadowPayload):
    global DrinkChoice_Selected
    
    # Desired = DRINK CHOICE change
    DrinkChoice_Selected = DrinkChoice.index(ShadowPayload)
    if (ShadowPayload <> "" and DrinkChoice[DrinkChoice_Selected] <> ""): #check if status or desired is not an empty value
        
        JSONPayload = '{ "state" : {'+\
                            '"reported": {'+\
                                '"DrinkChoice": "' + DrinkChoice[DrinkChoice_Selected] + '"'+\
                            '} '+\
                        '} '+\
                    '}'
        myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) #Send the new status as REPORTED values

def IoT_to_Raspberry_Change_Start(ShadowPayload):
    global DrinkChoice_Selected
    # Desired = Start
    
    if (ShadowPayload == "YES"):
        
        
        if (DrinkChoice[DrinkChoice_Selected] == "soda 1"): 
                print 'ready to pour ' + DrinkChoice[DrinkChoice_Selected]
                
                GPIO.output(sodaOne, True) 
                time.sleep(sodaTime)
                GPIO.output(sodaOne, False)
                
                JSONPayload = '{ "state" : {'+\
                                    '"reported": {'+\
                                        '"Start":"YES" '+\
                                    '} '+\
                                '} '+\
                            '}'
                myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) #Send the new status as REPORTED values
        elif (DrinkChoice[DrinkChoice_Selected] == "soda 2"):
            print "Ready for  " + DrinkChoice[DrinkChoice_Selected]
            
            GPIO.output(sodaTwo, True)
            time.sleep(sodaTime)
            GPIO.output(sodaTwo, False)
       
            JSONPayload = '{ "state" : {'+\
                                '"reported": {'+\
                                    '"Start":"YES" '+\
                                '} '+\
                            '} '+\
                        '}'
            myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) #Send the new status as REPORTED values
        elif (DrinkChoice[DrinkChoice_Selected] == "mixed" or DrinkChoice[DrinkChoice_Selected] == "mixed drink"):
            print "ready for a " + DrinkChoice[DrinkChoice_Selected]
            
            GPIO.output(sodaOne, True)
            GPIO.output(sodaTwo, True) 
            time.sleep(sodaTime/2)
            GPIO.output(sodaOne, False)
            GPIO.output(sodaTwo, False)
            
            JSONPayload = '{ "state" : {'+\
                                '"reported": {'+\
                                    '"Start":"YES" '+\
                                '} '+\
                            '} '+\
                        '}'
            myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) #Send the new status as REPORTED values
           
            time.sleep (3)
            
            
            DrinkChoice_Selected = DrinkChoice.index("") 
            JSONPayload = '{ "state" : {'+\
                                '"reported": {'+\
                                    '"Start": "NO", '+\
                                    '"DrinkChoice": "' + DrinkChoice[DrinkChoice_Selected] + '"'+\
                                '}, '+\
                                '"desired": {'+\
                                    '"Start": "NO", '+\
                                    '"DrinkChoice": "' + DrinkChoice[DrinkChoice_Selected] + '"'+\
                                '} '+\
                            '} '+\
                        '}'
            myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5) #Send the new status as REPORTED values

# Shadow callback for when a DELTA is received (this happens when Lamda does set a DESIRED value in IoT)
def IoTShadowCallback_Delta(payload, responseStatus, token):
#    global DrinkChoice_Selected
    print(responseStatus)
    payloadDict = json.loads(payload)
    print("++DELTA++ version: " + str(payloadDict["version"]))

    # Desired = DRINK CHOICE change
    if ("DrinkChoice" in payloadDict["state"]):
        print("DrinkChoice: " + str(payloadDict["state"]["DrinkChoice"]))
        IoT_to_Raspberry_Change_DrinkChoice(str(payloadDict["state"]["DrinkChoice"]))

    # Desired = Start
    if ("Start" in payloadDict["state"]):
        print("Start: " + str(payloadDict["state"]["Start"]))
        IoT_to_Raspberry_Change_Start(str(payloadDict["state"]["Start"]))

# Shadow callback GET for setting initial status
def IoTShadowCallback_Get(payload, responseStatus, token):
    print(responseStatus)
    payloadDict = json.loads(payload)
    print("++GET++ version: " + str(payloadDict["version"]))
    
    if ("DrinkChoice" in payloadDict["state"]["desired"]):
        if(str(payloadDict["state"]["reported"]["DrinkChoice"]) <> str(payloadDict["state"]["desired"]["DrinkChoice"])):
            print("DrinkChoice: " + str(payloadDict["state"]["desired"]["DrinkChoice"]))
            IoT_to_Raspberry_Change_DrinkChoice(str(payloadDict["state"]["desired"]["DrinkChoice"]))
   
            
    if ("Start" in payloadDict["state"]["desired"]):
        if(str(payloadDict["state"]["reported"]["Start"]).upper() <> str(payloadDict["state"]["desired"]["Start"]).upper()):
            print("Start: " + str(payloadDict["state"]["desired"]["Start"]))
            IoT_to_Raspberry_Change_Start(str(payloadDict["state"]["desired"]["Start"]))

# Shadow callback for updating the AWS IoT
def IoTShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("++UPDATE++ request " + token + " timed out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("++UPDATE++ request with token: " + token + " accepted!")
        if ("desired" in payloadDict["state"]):
            print("Desired: " + str(payloadDict["state"]["desired"]))
        if ("reported" in payloadDict["state"]):
            print("Reported: " + str(payloadDict["state"]["reported"]))
    if responseStatus == "rejected":
        print("++UPDATE++ request " + token + " rejected!")

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(shadowClient)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
myDeviceShadow = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("DrinkMachine", True)

#Now start setting up all GPIO required things like the PINs, and the interrupts

#GPIO of soda one
sodaOne = 38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(sodaOne, GPIO.OUT)
GPIO.output(sodaOne, False)

#GPIO of soda two
sodaTwo = 40
GPIO.setup(sodaTwo, GPIO.OUT)
GPIO.output(sodaTwo, False)

#time it takes soda to pour
sodaTime = 4


JSONPayload = '{ "state" : {'+\
                    '"reported": {'+\
                        '"Start": "NO", '+\
                        '"DrinkChoice": "' + DrinkChoice[DrinkChoice_Selected] + '"'+\
                    '}, '+\
                    '"desired": {'+\
                        '"Start": "NO" '+\
                    '} '+\
                '} '+\
            '}'
myDeviceShadow.shadowUpdate(JSONPayload, IoTShadowCallback_Update, 5)

# Listen on deltas from the IoT Shadow
myDeviceShadow.shadowGet(IoTShadowCallback_Get, 5)
myDeviceShadow.shadowRegisterDeltaCallback(IoTShadowCallback_Delta)

def loop():
    print 'looping'
    time.sleep(10)

if __name__ == '__main__':
    try:
        print ('DrinkMachine started, Press Ctrl-C to quit.')
        while True:
            loop()
    finally:
        GPIO.cleanup()
        myAWSIoTMQTTShadowClient.shadowUnregisterDeltaCallback()
        myAWSIoTMQTTShadowClient.disconnect()           
        print 'DrinkMachine stopped.'
