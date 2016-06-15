#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#fromLanguage = "en"
#toLanguage = "zh-TW"

fromLanguage = "zh-TW"
toLanguage = "en"

import random
import time
from PIL import Image
import Adafruit_ILI9341 as TFT
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
#import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from PIL import ImageDraw
from PIL import ImageFont

import os
from os import path
import speech_recognition as sr
from textblob import TextBlob
from gtts import gTTS

GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Raspberry Pi configuration.
DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0

#font = ImageFont.load_default()
font = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 21)
# Create TFT LCD display class.
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
# Initialize display.
disp.begin()

statusNow = 0  # 0 --> wait, 1 --> listen, 4 --> unknow, 5 --> error
lastStatus = -1

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)


while True:

	try:
		input_state = GPIO.input(2)

		if input_state==0:

			statusNow = 1
			r = sr.Recognizer()
			with sr.Microphone() as source:
				print("Say something!")
				if(lastStatus != statusNow):
					# Load an image.
					image = Image.open("listen.jpg")
					# Resize the image and rotate it so it's 240x320 pixels.
					image = image.rotate(0).resize((240, 320))
					# Draw the image on the display hardware.
					disp.display(image)
					lastStatus = statusNow

				audio = r.listen(source)

	                        #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "14657872182260.wav")
	                        #with sr.AudioFile(AUDIO_FILE) as source:
	                        #audio = r.record(source) # read the entire audio file

	                #sttTXT_org = r.recognize_google(audio, key="AIzaSyDMjV3fPEyVyQ6CGv6hZ-5Ndn9vCn-2NtI", language$
			sttTXT_org = r.recognize_google(audio, language = fromLanguage)
			print("Google Speech Recognition thinks you said: " + sttTXT_org)

			sttTXT_tblob = TextBlob(sttTXT_org)

			blobTranslated = sttTXT_tblob.translate(to=toLanguage)
			print("Translated -->  " + blobTranslated.raw)
	                # Draw the image on the display hardware.
			lineIndex = 12
			txtSpeak = blobTranslated.raw
			#arrayTXT = txtSpeak.split()[::-1]
			arrayTXT = txtSpeak.split()
			disp.clear((0, 0, 0))
			lines = ""
			for words in list(arrayTXT):
				if(len(lines + " " + words)>13):
					draw_rotated_text(disp.buffer, lines, (1, lineIndex), 0, font, fill=(255,255,255))
					print(lines)
					lines = words
					lineIndex = lineIndex + 26
				else:
					lines = lines + " " + words
				
				draw_rotated_text(disp.buffer, lines, (1, lineIndex), 0, font, fill=(255,255,255))

			disp.display()
			tts = gTTS(blobTranslated.raw + ". ", lang=toLanguage)
			tts.save("tts.mp3")
			os.system('omxplayer -p -o hdmi tts.mp3')
			time.sleep(10)
		else:
			statusNow = 0
			if(lastStatus != statusNow and statusNow != 1):
				# Load an image.
				image = Image.open(random.choice(["s1.jpg","s2.jpg","s3.jpg","s4.jpg","s5.jpg"]))
				# Resize the image and rotate it so it's 240x320 pixels.
				image = image.rotate(0).resize((240, 320))
				# Draw the image on the display hardware.
				disp.display(image)
				lastStatus = statusNow

	except sr.UnknownValueError:
		statusNow = 4
		lastStatus = statusNow
		print("Google Speech Recognition could not understand audio")
		# Load an image.
		image = Image.open("q1.jpg")
		# Resize the image and rotate it so it's 240x320 pixels.
		image = image.rotate(0).resize((240, 320))
		# Draw the image on the display hardware.
		disp.display(image)
		time.sleep(3.5)

	except sr.RequestError as e:
		statusNow = 5
		lastStatus = statusNow
		print("Could not request results from Google Speech Recognition service; {0}".format(e))
		# Load an image.
		image = Image.open("e1.jpg")
                # Resize the image and rotate it so it's 240x320 pixels.
		image = image.rotate(0).resize((240, 320))
                # Draw the image on the display hardware.
		disp.display(image)
		time.sleep(3.5)
