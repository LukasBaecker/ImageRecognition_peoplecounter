![The Logo of the Imagerecognition group](./people_counter.svg)

# ImageRecognition_peoplecounter

This project is meant to fulfill the requirements of the image recognition course at WWU Münster.

## Idea
The people_counter is a Raspberry Pi programm based on python that should count people in a videoframe and weather they are entering a room or leaving. The user can set a maximum number of people that should be alowed to be inside and by exceeding this threshold the buzzer will alarm that to many people entered the room/builden or similar.

## Hardware used
  * Raspberry Pi 4B
  * Raspberry Pi camera V2.1
  * active Buzzer
  * VNC Viewer 6.20.
  
## Software and Versions
  * Debian Buster with Raspberry Pi Desktop (V4.19)
  * python 3.7.3
  * OpenCV 4.1.0
  
## Getting started
### Installation
To get started install Debian Buster with Raspberry Pi Desktop from [here](https://www.raspberrypi.org/software/raspberry-pi-desktop/).
Starting the Raspberry Pi and getting to the Desktop you will need to connect it to the internet first. After that you can check if the neccessary python version is installed. If not so, install the version as shown in the list above. Also you will need to install OpenCV on your Pi system.

We recommand to install VNC Viewer on your computer or mobile device to get remote access to the Pi. Check that all needed settings for that are set.

Check that the camera is activated in the option menu as well.

### let's get ready
  * Clone this repository or download it to your Raspberry Pi. 
  * Create a folder called "saved_data" right were you save all the files from this repository to find the detected personnumber data saved as csv-file later on in here.
  * follow the instructions under "make the script executable"
  * set up a OSM account and add two new Sensors to your OSM. More details under "OpenSenseMap integration"
  
### make the script executable
To make the python script "guiCV.py" executable on double-click follow these instructions.
First go to the folder of the project with 

```
$cd FOLDERPATH
```
followed by 

```
$ chmod +x guiCV.py
```

The following will move the "guiCV.py" into your bin directory, and it will be runnable from anywhere.

```
$ cp guiCV.py /usr/bin
```
OR
```
$ cp guiCV.py /usr/local/bin
```

Now the guiCV.py file should be executable by double-click it

### OpenSenseMap intergration
To load the data of your Pi up to the OpenSenseMap just follow the instructions of [OpenSenseMap](https://opensensemap.org/register).
  * Set the Group Identifier as "InOutCounting".
  * set two sensors and call them like:
    * "total_num_people" as phenomenon and with "person" as unit and "int" as type
    * "current_people" as phenomenon and also with "person" as unit and "int" as type

All you have to do now is to fill in your IDs into the setupCV.yaml file and you are ready to start the guiCV.py script.

Happy counting!
