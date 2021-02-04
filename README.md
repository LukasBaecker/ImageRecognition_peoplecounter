![The Logo of the Imagerecognition group](./people_counter.svg)

# ImageRecognition_peoplecounter

This project is meant to fulfill the requirements of the image recognition course at WWU Münster.

## Idea
The people_counter is a Raspberry Pi programm based on python that should count people in a videoframe and weather they are entering a room or leaving. The user can set a maximum number of people that should be alowed to be inside and by exceeding this threshold the buzzer will alarm that to many people entered the room/builden or similar.

## Hardware used
  * Raspberry Pi 4B
  * Raspberry Pi camera V2.1
  * active Buzzer
  
## Software and Versions
  * Debian Buster with Raspberry Pi Desktop (V4.19)
  * python 3.7.3
  * OpenCV 4.1.0
  
## Getting started
To get started install the latest version of Raspberrie Pis OS 
The guiCV.py file is the current project-file that will run a scanner with CV2 and saves data to csv and as jpg.
For the saving you will need to add two folders: "saved_data" and "saved_pictures".

#
