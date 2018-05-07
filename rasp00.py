import RPi.GPIO as GPIO
import time
import sys
import tweepy
from hx711 import HX711
from grovepi import *
from grove_rgb_lcd import *
from datetime import datetime

#Set Grove-LCD Backlight to blue 
setRGB(0,0,180)

def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Weight Sensor Program Stopped!"
    sys.exit()

#Create n new HX711
hx = HX711(27, 22)
hx.set_reading_format("LSB","MSB")
#Calibration of weight sensor. Using a known value (455g [incl. packaging] block of butter - this is avg value of max. 1kg load)
#I got a reading of -388981. Therefore my reference unit is -388981/456 = -853
hx.set_reference_unit(-853)
hx.reset()
hx.tare()

#Set up infinite loop
while True:
    try:
    	#Due to slight discrepancies sometimes after removing the load from the scale 
    	#a value below zero is displayed (e.g. -1g). The following line prevents negative values from being displayed
        val = max(0, int(hx.get_weight(5)))
        print str(val) + "g"

        hx.power_down()
        hx.power_up()
        #For the purpose of testing and demonstration the sleep time has been set at 1 sec.
        #This could be increased as necessary for a more practical application
        time.sleep(1)
        
        #Display the weight on the Grove-LCD 
        w = str(val)
        setText("Weight:" + w + "g")
        
        if val == 0:
            print "Add item to scale (max. load 700g)"
            setText("Weight:" + w + "g\n" + "Add item max.700")
            
            #Set auth variables
            def get_api(cfg):
                auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
                auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
                return tweepy.API(auth)

			#Create a function to hold values of keys. The values have been omitted for privacy.
			#To run this code please enter your own API values
	    	def main():
  				cfg = { 
                    "consumer_key"        : "YOUR API KEY",
                    "consumer_secret"     : "YOUR API SECRET",
                    "access_token"        : "YOUR ACCESS TOKEN",
                    "access_token_secret" : "YOUR ACCESS TOKEN SECRET" 
                }
				
				#Create a new api
                api = get_api(cfg)
                tweet = "***Supplies completely depleted!***"
                #Add time to message.To prevent the program posting tweets to often
                #the placeholder for mins (%M) could be omiited to restrict updates to every hour
                #or the time could be completely omitted (%-I:%M%P) to restrict updates to once a day
                time = datetime.now().strftime('%-I:%M%P on %d-%m-%Y')
                
                try:
                	#A tweet is referred to as 'status'
                    status = api.update_status(status=tweet + " @ " + time)
                #Tweepy throws an error and the program crashes if a duplicate message is sent
                #This exception allows the program to continue running without duplicating messages
                except tweepy.TweepError as error:
                    if error.api_code == 187:
                        print('Duplicate message: No tweet sent')
                    else:
                        raise error
                            
            if __name__ == "__main__":
                main()
                
        #While loop to detect when the weight drops below a determined level (100g in this case)    
        while val != 0:
            if val < 100:
            	#Set auth variables
            	def get_api(cfg):
                    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
                    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
                    return tweepy.API(auth)

				#Create a function to hold values of keys. The values have been omitted for privacy.
				#To run this code please enter your own API values
				def main():
  		    		cfg = { 
                    	"consumer_key"        : "YOUR API KEY",
                    	"consumer_secret"     : "YOUR API SECRET",
                    	"access_token"        : "YOUR ACCESS TOKEN",
                    	"access_token_secret" : "YOUR ACCESS TOKEN SECRET" 
                    }
                    
					#Create a new api
                    api = get_api(cfg)
                    tweet = "Warning: Supplies low! Please stock up."
                    time = datetime.now().strftime('%-I:%M%P on %d-%m-%Y')
                    
                    try:
                    	#A tweet is referred to as 'status'
                        status = api.update_status(status=tweet + " @ " + time)
                    #Tweepy throws an error and the program crashes if a duplicate message is sent
                	#This exception allows the program to continue running without duplicating messages
                    except tweepy.TweepError as error:
                        if error.api_code == 187:
                            print('Duplicate message: No tweet sent')
                        else:
                            raise error
                        
            	if __name__ == "__main__":
                    main()
			break
    
    #Error/Exception Handling    
    except (IOError, TypeError) as e:
    	print(str(e))
    	setText(" ")
    	
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
        setText(" ")
    	break