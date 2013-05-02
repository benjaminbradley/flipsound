
# all available pin IDs: 2,3,4,7,8,9,10,11,14,15,17,18,22,23,24,25,27

# GPIO pin layout for rev2 RPi
# [3v]	[5v]
# 2		[5v]
# 3		GND
# 4		14
# GND	15
# 17	18
# 27	GND
# 22	23
# [3v]	24
# 10	GND
# 9		25
# 11	8
# GND	7
# 

# --- recommended wiring for LCD+10 buttons ---
# basic idea: keep LCD pins at the top, then 2 rows of buttons down each side
# - similar to the physcal layout of the components on the board
# 			[3v]	[5v]
# lcd.e		2		[5v]
# lcd.rs	3		GND
# lcd.dat1	4		14	lcd.dat2
# 			GND 	15	lcd.dat3
# 			17		18	lcd.dat4
# butLt		27  	GND
# but4		22  	23	butRt
# 			[3v]	24	but8
# but3		10  	GND
# but2		9		25	but7
# but1		11  	8	but6
# 			GND 	7	but5
