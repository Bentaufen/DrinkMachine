# DrinkMachine
A Voice Automated Drink Machine that will pour drinks that are controlled by Amazon Alexa.

STEPS I took to create the DrinkMachine.

1. Put Alexa onto a Raspberry Pi 3. This required a Raspberry Pi 3 and a microphone to communicate with Alexa. To do this, I simply followed Amazon's guide here https://github.com/alexa/alexa-avs-sample-app. NOTE: I also have an Amazon Echo so this step was unnecessary, however,  but to make the drink machine to be multi-purpose, such as control music, and Alexa is the best way to do this.

2. Create an Alexa Skills Kit that recognizes the command "Alexa tell DrinkMachine to pour soda one" or "Alexa ask DrinkMachine to pour me a drink." The ASK then pushes these commands into AWS Lambda which is a programming platform that I have setup a python script to process these commands.

3. Program the python script on AWS Lambda. The script also reads AWS IoT data from the Raspberry Pi and also uploads new data to the Raspberry Pi. AWS IoT does this by sending and receiving Delta messages to and from the Pi. The Pi then receives and these messages and communicates to the valves of the DrinkMachine directly through GPIO. For implemnting AWS IoT, I used Amazon's python libraries including on Github on both AWS Lambda and the Pi. 

4. Created a python script on the Raspberry Pi to interpret delta messages and tell what valves to open and for how long. For instance, if the requested drink was soda one, then valve one would open for 5 seconds (how long it was determined to pour a full drink). If the requested drink was mixed, both valves would open for about 2.5 seconds.

5. My roommate created the circuit that connects the valves to the Raspberry Pi GPIO. We then put together the rest of the machine including two 2-liter soda bottles which wer connected to the valves and tubes for directing liquid to the cup. 

All code included in this project is on here.

