#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#fromLanguage = "en"
#toLanguage = "zh-TW"

fromLanguage = "zh-TW"
toLanguage = "en"

import sys
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

GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Raspberry Pi configuration.
DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0

#font = ImageFont.load_default()
#font = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 21)
font = ImageFont.truetype('fonts/zh-TW.ttf', 21)
# Create TFT LCD display class.
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))
# Initialize display.
disp.begin()

languages = ["en", "de", "es", "fr", "it", "ja", "ko", "ru"]
langIndex = 0   # default language
statusNow = 0  # 0 --> wait, 1 --> listen, 4 --> unknow, 5 --> error, 6 --> Update setting
lastStatus = -1
translateStatus = "c2e" 
languageStatus = languages[langIndex]

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

def click_TranslateDirection():

	global statusNow, lastStatus, translateStatus, fromLanguage, toLanguage
	#print(statusNow, lastStatus)
	statusNow = 6

	if translateStatus=="c2e":
		translateStatus = "e2c"
	else:
		translateStatus = "c2e"

	tmpTXT = fromLanguage
	fromLanguage = toLanguage
	toLanguage = tmpTXT

	print("icons/"+translateStatus+".jpg")
	image = Image.open("icons/"+translateStatus+".jpg")
	image = image.rotate(180)
	disp.clear((0, 0, 0))
	disp.display(image)
	time.sleep(0.5)
	lastStatus = statusNow

def click_languageSelect():

	global statusNow, lastStatus, translateStatus, fromLanguage, toLanguage, languages, langIndex
	statusNow = 6

	if langIndex+1 > (len(languages) - 1):
		langIndex = 0
	else:
		langIndex = langIndex + 1
	
	if fromLanguage=="zh-TW":
		toLanguage = languages[langIndex]
	else:
		fromLanguage = languages[langIndex]

	print("icon_flag/"+languages[langIndex]+".jpg")
	image = Image.open("icon_flag/"+languages[langIndex]+".jpg")
	image = image.rotate(180)
	disp.clear((0, 0, 0))
	disp.display(image)
	time.sleep(0.5)
	lastStatus = statusNow	

try:

	while True:

		try:
			input_state = GPIO.input(13) #Start to record BUTTON
			language_state = GPIO.input(19) #Switch Language BUTTON
			translate_state = GPIO.input(26) #Switch C2E or E2C BUTTON

			if translate_state==0:
				click_TranslateDirection()

			if language_state==0:
				click_languageSelect()

			if input_state==0:
				statusNow = 1
				print("From:" + fromLanguage + "   To:" + toLanguage)

				r = sr.Recognizer()
				with sr.Microphone() as source:
					print("Say something!")
					if(lastStatus != statusNow):
						# Load an image.
						image = Image.open("icons/listen.jpg")
						# Resize the image and rotate it so it's 240x320 pixels.
						image = image.rotate(180)
						# Draw the image on the display hardware.
						disp.display(image)
						lastStatus = statusNow

					audio = r.listen(source)

				#sttTXT_org = r.recognize_google(audio, key="AIzaSyDMjV3fPEyVyQ6CGv6hZ-5Ndn9vCn-2NtI", language=fromLanguage)
				sttTXT_org = r.recognize_google(audio, language = fromLanguage)				
				print("Google Speech Recognition thinks you said: " + sttTXT_org)
				image = Image.open("icons/p1.jpg")
				image = image.rotate(0).resize((240, 320))
				disp.display(image)

				sttTXT_tblob = TextBlob(sttTXT_org)

				blobTranslated = sttTXT_tblob.translate(to=toLanguage)
				print("Translated -->  " + blobTranslated.raw)
		                # Draw the image on the display hardware.
				lineIndex = 290
				txtSpeak = blobTranslated.raw
				#arrayTXT = txtSpeak.split()[::-1]
				if toLanguage=="zh-TW" or toLanguage=="ja" or toLanguage=="ko":
					arrayTXT = list(txtSpeak)
				else:
					arrayTXT = txtSpeak.split()

				disp.clear((0, 0, 0))
				lines = ""
				font = ImageFont.truetype("fonts/"+toLanguage+".ttf", 21)
				for words in list(arrayTXT):
					if(len(lines + " " + words)>13):
						draw_rotated_text(disp.buffer, lines, (1, lineIndex), 180, font, fill=(255,255,255))
						print("words->" + words + " // lines->" + lines)
						lines = words
						lineIndex = lineIndex - 26
					else:
						lines = lines + " " + words
				
				print("lines->" + lines)
				draw_rotated_text(disp.buffer, lines, (1, lineIndex), 180, font, fill=(255,255,255))
				disp.display()
				tts = gTTS(blobTranslated.raw + ". ", lang=toLanguage)
				tts.save("tts.mp3")
				os.system('omxplayer --no-osd tts.mp3')
				time.sleep(3)
			else:
				statusNow = 0
				if(lastStatus != statusNow and statusNow != 1):
					# Load an image.
					image = Image.open(random.choice(["icons/s1.jpg","icons/s2.jpg","icons/s3.jpg","icons/s4.jpg","icons/s5.jpg"]))
					# Resize the image and rotate it so it's 240x320 pixels.
					image = image.rotate(180)
					# Draw the image on the display hardware.
					disp.display(image)
					lastStatus = statusNow

		except sr.UnknownValueError:
			statusNow = 4
			lastStatus = statusNow
			print("Google Speech Recognition could not understand audio")
			# Load an image.
			image = Image.open("icons/q1.jpg")
			# Resize the image and rotate it so it's 240x320 pixels.
			image = image.rotate(180)
			# Draw the image on the display hardware.
			disp.display(image)
			time.sleep(3.5)

		except sr.RequestError as e:
			statusNow = 5
			lastStatus = statusNow
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
			# Load an image.
			image = Image.open("icons/e1.jpg")
	                # Resize the image and rotate it so it's 240x320 pixels.
			image = image.rotate(180)
	                # Draw the image on the display hardware.
			disp.display(image)
			time.sleep(3.5)

		except:
			print("Unexpected error")
			

except:
	print("Unexpected error:", sys.exc_info()[0])
	raise
