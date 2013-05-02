# flipsound.py
# v0.1
# 2013-03-15
# BGCB

# LIBRARIES
import re
from subprocess import * 
from time import sleep, strftime
from datetime import datetime
from sys import exit
import operator
import os
import signal
import pygame.mixer
from Adafruit_CharLCD import Adafruit_CharLCD
import RPi.GPIO as GPIO



# CONSTANTS & GLOBAL VARIABLES
NUMBUTTONS = 10
LCD_WIDTH=16
LCD_HEIGHT=2
MISC_PAGENAME = 'miscellaneous'
SYSTEM_SOUND_DIR_NAME = 'system'

# output: LCD config
lcd_rs_pin=3
lcd_e_pin=2
lcd_data_pins=[4,14,15,18]

# input - button pins
# button ids start at 0 & will automatically be mapped to pins based on their order in the button_pins array
num_sound_buttons = NUMBUTTONS - 2
num_sound_channels = num_sound_buttons		# so on any given page all the buttons can be playing their sounds together
PLAYSOUND_BUTTONIDS = range(0, num_sound_buttons)	# NOTE: sound buttons should start at index 0 & serve as index arrays for sound data, channels, etc.
BUTTONID_PREVPAGE = num_sound_buttons
BUTTONID_NEXTPAGE = num_sound_buttons + 1
button_pins = [8, 25, 24, 23, 9, 10, 22, 27, 7, 11]
LCD_ENABLED = True
DEBUGLOG = '/home/pi/flipsound/debug.log'
MENU_START = MENU_REBOOT = 0
MENU_SHUTDOWN = 1



# output: sound config
#sound_pages = {
#	'Game Show' : ['applause', 'freesound.org-37215__simon-lacelle__ba-da-dum', 'buzzer'],
#	'Haunted' : ['freesound.org-68682__mikaelfernstrom__doorcreaking', 'thunder', 'scream'],
#	'City' : ['freesound.org-58202__the-bizniss__car-horn', ],
#	'Homestuck' : ['00082-riddle-absence', '00222-haunting violin refrain', '00422-Skaia-a dormant crucible of unlimited creative potential']
	#'Space' : [],	# 1. antenna-sound 2. heavy-breathing 3. silence 4. radio-noise 
	#'Jungle/Forest' : [],
	#'Flipside' : [],	# 1. unce-unce 2. spanking 3. burning fire	
#}
sound_dir = os.path.dirname(os.path.realpath(__file__))+'/sounds'
STARTUP_SOUND = sound_dir +'/' + SYSTEM_SOUND_DIR_NAME + '/bopadabah.wav'


#########################################################################################################
# HELPER FUNCTIONS
#########################################################################################################

def debugmsg(msg):
	if DEBUGLOG:
		with open(DEBUGLOG, "a") as myfile:
		    myfile.write(str(datetime.now())+": "+msg+"\n")
# end debugmsg()


def handleSigQUIT(signum, frame):
	debugmsg("Got sigQUIT, terminating program...")
	textout_clearscreen()
	textout_message("Prgm stop.Power\n")
	textout_message("down or restart.")
	global going
	going = False
signal.signal(signal.SIGQUIT, handleSigQUIT)


def textout_clearscreen():
	global LCD_ENABLED
	global lcd
	if LCD_ENABLED:
		lcd.clear()
	else:
		print "\n------------------------------------------------------------------\n"
# end clearscreen()


def textout_message(msg):
	global LCD_ENABLED
	global lcd
	if LCD_ENABLED:
		lcd.message(msg.ljust(LCD_WIDTH))
	else:
		print msg
# end message()


def textout_go_home(a,b):
	global LCD_ENABLED
	global lcd
	if LCD_ENABLED:
		lcd.setCursor(a,b)
	else:
		print "\n"


def get_page_display(page_name):
	m = re.match('(\d+)\.(.*)', page_name)	# if there's a number at the beginning for sorting, remove it
	if m:
		return m.group(2)
	return page_name


def get_sound_display(sound_name):
	# remove the .wav from the end
	if(sound_name.lower().endswith('.wav')):
		sound_name = sound_name[0:-4]
	# if there's a hash mark, remove it and everything after it
	m = re.match('(.*?)#.*', sound_name)
	if m:
		sound_name = m.group(1)
	# if there's a directory name, remove it
	m = re.match('.*/(.*)', sound_name)
	if m:
		sound_name = m.group(1)
	# if there's a number at the beginning for sorting, remove it
	m = re.match('(\d+)\.(.*)', sound_name)
	if m:
		return m.group(2)[:(LCD_WIDTH-3)]
	return sound_name[:(LCD_WIDTH-3)]	# just show the first 13 characters of the last sound that was played
	

def change_to_page(sound_page_index):
	global sound_names
	page_name = sound_page_names[sound_page_index]
	page_display = get_page_display(page_name)
	#debugmsg("changing to page #"+sound_page_index+": "+page_name)
	textout_clearscreen()
	textout_message("Page"+str(sound_page_index+1)+":" + page_display+"\n")
	sound_names = []
	for soundname in sound_pages[page_name]:
		sound_names.append(page_name+'/'+soundname)
	#sound_names = sound_pages[page_name]
	#print "sound_names changed to:"
	#import pprint
	#pprint.pprint(sound_names)
	textout_message(str(len(sound_names))+" sounds")
# end change_to_page()

	
def play_sound(index):
	if(index >= len(sound_names)):
		debugmsg("no sound #"+str(index)+" for this page")
	else:
		debugmsg("playing sound #"+str(index))
		# get name for corresponding sound
		sound_name = sound_names[index]
		debugmsg("playing sound: "+sound_name)
		sound_channels[index].play(sound_data[sound_name])
		sound_display = get_sound_display(sound_name)
		textout_go_home(0,1)	# updating the second line only
		textout_message("#"+str(index+1)+":"+sound_display)	# just show the first 13 characters of the last sound that was played
	

def drawmenu():
	global menu_page
	if menu_page == MENU_REBOOT:
		menuitem = "reBOOT"
	elif menu_page == MENU_SHUTDOWN:
		menuitem = "shutDOWN"
	textout_clearscreen()
	textout_message("mENU/onfIg mODE\n")
	textout_message("<nEXT|"+menuitem+">")

#########################################################################################################
#########################################################################################################


# scan sound directories for sound files
sound_pages = {}
for filename in os.listdir(sound_dir):
	filepath = os.path.join(sound_dir, filename)
	if(os.path.isdir(filepath)):
		page_name = filename
		if not filename == SYSTEM_SOUND_DIR_NAME:
			page_sounds = os.listdir(filepath)
			sound_pages[page_name] = page_sounds
			#print "display name for "+page_name+" is: "+get_page_display(page_name)
			#debugmsg("for page "+page_name+" the sounds are:")
			#for sound_filename in page_sounds:
			#	print "display name for sound "+sound_filename+" is "+get_sound_display(sound_filename)
	else:
		if(not filename.startswith('.')):	# skip ., .., and all other .hiddenfiles
			#add to miscellaneous sound pages
			if not sound_pages.has_key(MISC_PAGENAME):	# initialize the misc page if needed
				sound_pages[MISC_PAGENAME] = []
			sound_pages[MISC_PAGENAME].append(filename)
			#TODO: if number of sounds > sounds per page, then create a new "misc" page
			#debugmsg("misc sound: "+filepath)


sound_names = []	# array of sound names for the current page
sound_data = {}		# actual sound data for the sounds, indexed by filename
sound_page_names = sorted(list(sound_pages.keys()))
sound_page_index = 0


button_pins_index = {}
button_status = []


#### NOTES FOR PUTTING LEDs UNDER ALL THE BUTTONS
# 1 typical LED = 20 mA draw
# the 2 3.3v outs only provide 50mA each, restricting us to 4 LEDs driven from those pins
# the LCD (and + rail for buttons?) will use one of the 5v outs
# the other 5v out can supply max 300 mA current draw, which will power 15 LEDs - PLENTY!!!! (according to http://elinux.org/RPi_Low-level_peripherals)
# SO: hook up the button LEDs in parallel to the other 5v output pin

# INITIALIZATION
debugmsg("sleeping 3 seconds for system startup...")
sleep(3)
debugmsg("FlipSound starting up...")


# configure hardware in/out pins
GPIO.setmode(GPIO.BCM)

# initialize button pins & data structures
# NOTE: lcd button pins are set to OUT mode by Adafruit_CharLCD()'s init method
GPIO.setwarnings(False)	# ignore warnings about re-setting pin mode
for pin in button_pins:
	button_pins_index[pin] = len(button_pins_index)	# this will be a hash of pin => array index
	GPIO.setup(pin, GPIO.IN)	# set hardware pin to input mode
	button_status.append(False)
if LCD_ENABLED:
	lcd = Adafruit_CharLCD(lcd_rs_pin, lcd_e_pin, lcd_data_pins, GPIO)
	lcd.begin(LCD_WIDTH,LCD_HEIGHT)
GPIO.setwarnings(True)

# initialize the sound mixer
pygame.mixer.init(48000, -16, 1, 1024)

# load the sound data and initialize the sound channels
all_sound_names = []
for pagename in sound_pages:
	for soundname in sound_pages[pagename]:
		all_sound_names.append(pagename+'/'+soundname)
debugmsg("Sound directory is "+sound_dir+", loading data for "+str(len(all_sound_names))+" sound files...")
for name in all_sound_names:
	filename = sound_dir + '/' + name
	debugmsg("loading sound from "+filename)
	sound_data[name] = pygame.mixer.Sound(filename)
	if not sound_data[name]:
		debugmsg("ERROR: Couldn't load sound from file at "+filename)
	#sndA = pygame.mixer.Sound("buzzer.wav")

pygame.mixer.set_num_channels(num_sound_channels)
debugmsg("Initializing "+str(num_sound_channels)+" sound channels...")
sound_channels = []
for i in range(0, num_sound_channels-1):
	debugmsg("Initializing sound channel "+str(i+1))
	sound_channels.append(pygame.mixer.Channel(i))
	#soundChannelB = pygame.mixer.Channel(2)


# play startup sound
sound_channels[0].play(pygame.mixer.Sound(STARTUP_SOUND))

# load the first page of sounds
change_to_page(0)


debugmsg("Sound Board Ready: listening for button status changes...")

#print "hold both buttons down together, or type CTRL-C to quit\n"
menu_mode = False	# start in "play" mode
menu_page = MENU_START
going = True
while going:
	try:
		# look for button down/up events
		for pin in button_pins:
			buttonid = button_pins_index[pin]
			if(GPIO.input(pin) == True and button_status[buttonid] == False):
				debugmsg("button on pin "+str(pin)+" pressed, buttonid is "+str(buttonid))
				button_status[buttonid] = True
				
				#TODO: trigger event for this button
				#if(buttonid) is in sound_button_ids
				if(buttonid in PLAYSOUND_BUTTONIDS):
					if not menu_mode:
						play_sound(buttonid)
				elif(buttonid == BUTTONID_PREVPAGE):
					if menu_mode:
						if menu_page == MENU_REBOOT:
							menu_page = MENU_SHUTDOWN
							drawmenu()
						elif menu_page == MENU_SHUTDOWN:
							menu_page = MENU_START
							menu_mode = False
							change_to_page(sound_page_index)
					else:
						# go to prev page, or circle to last if needed
						sound_page_index = (sound_page_index+len(sound_pages)-1) % len(sound_pages)
						debugmsg("Changing to page "+str(sound_page_index))
						change_to_page(sound_page_index)
				elif(buttonid == BUTTONID_NEXTPAGE):
					if menu_mode:
						if menu_page == MENU_REBOOT:
							textout_clearscreen()
							textout_message("Restarting..")
							debugmsg("REBOOT selected in CONFIG/MENU: Issuing reboot command...")
							os.system("reboot")
							exit()
						elif menu_page == MENU_SHUTDOWN:
							textout_clearscreen()
							textout_message("Powering off..")
							debugmsg("SHUTDOWN selected in CONFIG/MENU: Issuing shutdown command...")
							os.system("shutdown now")
					else:
						# go to next page, or back to 1 if needed
						sound_page_index = (sound_page_index+1) % len(sound_pages)
						debugmsg("Changing to page "+str(sound_page_index))
						change_to_page(sound_page_index)
				
			elif(GPIO.input(pin) == False and button_status[buttonid] == True):
				#print "DEBUG: button on pin "+str(pin)+" up"
				button_status[buttonid] = False

		# handle special multi-button events
		if (GPIO.input(button_pins[BUTTONID_PREVPAGE]) == True and GPIO.input(button_pins[BUTTONID_NEXTPAGE]) == True):
			debugmsg("detected 2-button hold (PG-LEFT + PG-RIGHT), activating menu mode...")
			menu_mode = True
			drawmenu()

		sleep(.01)
	except KeyboardInterrupt:
		debugmsg("detected CTRL-C, quitting...")
		going = False
		exit()
	except:
		textout_clearscreen()
		textout_message("**** ERROR ****\n")
		textout_message("Program Crashed")
		raise

# cleanup code:
GPIO.cleanup()
exit()
