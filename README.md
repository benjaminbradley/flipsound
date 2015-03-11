# FlipSound

This software was created to run the "Book of Sounds" sound board created for a Do-It-Yourself Shadow Puppet Theater space.
YouTube videos:
* Demo: https://www.youtube.com/watch?v=bx5x3KT_1Ko
* Behind the Scenes: https://www.youtube.com/watch?v=lCHsOf572nU


# DISCLAIMER:
This software comes with no warranty, expressed or implied, and no implication of fitness for any use of any kind. :)


# REQUIREMENTS:
Adafruit_CharLCD.py
	available from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_CharLCD/Adafruit_CharLCD.py
	put it in the same directory as flipsound.py


# SETUP:
1. Create a sounds/ subdirectory in the same directory as flipsound.py
2. Create sub-directories for each "page" of the sound board.
3. Put .wav sound files into the sub-directory for each page.

Files can be prefixed with a number and dot to change the order of the pages and/or sounds.

Example file structure:
sounds/1.game show/1.ba-dum-bum.wav
sounds/1.game show/2.applause.wav
sounds/1.game show/4.buzzer.wav
sounds/1.game show/Audience Clapping.wav
sounds/1.game show/Contestant Ring.wav
sounds/1.game show/Correct Answer.wav
sounds/1.game show/laugh.ogg
sounds/2.haunted/1.creaking door.wav
sounds/2.haunted/2.StrangeNoise.wav
sounds/2.haunted/2.thunder.wav
sounds/2.haunted/3.scream.wav
sounds/2.haunted/3.WickedLaughter.wav
sounds/2.haunted/Bats.wav
sounds/2.haunted/Incantation.wav
sounds/2.haunted/Owl.wav
sounds/animals/BirdChirp.wav
sounds/animals/CatMeow.wav
sounds/animals/ChickenCluck.wav
sounds/animals/CrowCaw.wav
sounds/animals/DogBark.wav
sounds/animals/Goat.wav

## OPTIONAL: STARTUP_SOUND
STARTUP_SOUND : Since it takes the RPi a few seconds to boot up, you can set the STARTUP_SOUND variable to a wav file that will be played when the software has finished loading.
MISC_PAGENAME : any wav files found in the main sounds/ directory (not in a "page" subdirectory) will get grouped into a page with this name
SYSTEM_SOUND_DIR_NAME : name of subdirectory reserved for system sounds (e.g. startup sound) - will be ignored (not put on a page)
HIDDEN_SOUND_DIR_NAME : name of subdirectory used for "hidden page"


# TO RUN:
python flipsound.py


# HARDWARE CONFIGURATION:
RPi pinouts are defined in the following variables:
* Output to LCD Display: lcd_rs_pin, lcd_e_pin, lcd_data_pins
* Input from arcade Buttons: button_pins
This documentation does not include hardware specs.


# OPERATION:
Once the software starts up, the display will show the name of the page and number of sounds on each page.
The "left" and "right" buttons will page forward/backward through all the loaded pages of sounds.
The 8 sound buttons will play the sound mapped to each button for the current page. 
Pushing all 8 buttons at the same time will activate the "hidden page" of sounds, if one is configured.

