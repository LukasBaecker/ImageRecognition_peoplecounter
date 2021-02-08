#!/usr/bin/env python3
import yaml
import tkinter
import RPi.GPIO as GPIO
from time import sleep
import cv2
import csv
from PIL import Image
from PIL import ImageTk
import time
import requests
import json
#load env variables from yaml file
with open(r'setupCVGemenweg.yaml') as file:
    senseboxVars = yaml.load(file, Loader=yaml.FullLoader)

#Disable warnings (optional)

GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)
#Set buzzer - pin 23 as output
buzzer=23 
GPIO.setup(buzzer,GPIO.OUT)
#opensensemap setup
headers = {'content-type': 'application/json'}
url = 'https://api.opensensemap.org/boxes/'+senseboxVars['senseBox_id']+'/data'
print(senseboxVars)
#varibles for counting
avg = None
xvalues = list()
motion = list()
countIn = senseboxVars['initial_current_inside']
countOut = 0
countCurrentIn = senseboxVars['initial_current_inside']
maximumValue = senseboxVars['initial_maximum_personnumber']
#with open('SavedVisitorNumbers.csv', mode='w') as csv_file:
 #   fieldnames = ['Date', 'Time', 'Visitors']
  #  writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
OptionList = ["from left to right", "from right to left", "from up to down", "from down to up"]

def find_majority(k):
    myMap = {}
    maximum = ('', 0)  # (occurring element, occurrences)
    for n in k:
        if n in myMap:
            myMap[n] += 1
        else:
            myMap[n] = 1

        # Keep track of maximum on the go
        if myMap[n] > maximum[1]:
            maximum = (n, myMap[n])

    return maximum

class App:
    def __init__(self, window, window_title, video_source=0):
        global header
        global url
        global countCurrentIn
        global OptionList
        global maximumValue
        self.csv_file= open('./saved_data/SavedVisitorNumbers_'+time.strftime("%d-%m-%Y")+'.csv', mode='w')
        self.fieldnames = ['Date', 'Time', 'Current Visitors', 'Total Visitors']
        self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
        self.writer.writeheader()
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)
        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.grid(row=0,column=0, columnspan=1, rowspan=4)
        # Button that lets the user take a snapshot
        self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.grid(row=4,column=0)
        #currently In: labels and buttons
        self.labelCurrentIn=tkinter.Label(window,text= "currently inside: "+str(countCurrentIn),bg='gold',fg='blue')
        self.labelCurrentIn.grid(row=0,column=1, columnspan=2)
        #In: labels and buttons
        self.btn_correctInPlus=tkinter.Button(window, text="+", command=self.countIn)
        self.btn_correctInPlus.grid(row=1,column=1)
        #Out: labels and buttons
        self.btn_correctOutPlus=tkinter.Button(window, text="-", command=self.countOut)
        self.btn_correctOutPlus.grid(row=1,column=2)
        #selection of direciton
        self.variable = tkinter.StringVar(window)
        self.variable.set(OptionList[0])
        self.opt = tkinter.OptionMenu(window, self.variable, *OptionList)
        self.labelDirection=tkinter.Label(window,text= "change the direction for entering: ",bg='gold',fg='blue')
        self.labelDirection.grid(row=0,column=3)
        self.opt.config(font=('Helvetica', 12))
        self.opt.grid(row=1,column=3)
        #that was not a human
        self.btn_reset=tkinter.Button(window, text="That one thing wasn't a human being... coming in.", width=50, command=self.noHumanComingIn)
        self.btn_reset.grid(row=2,column=1, columnspan=2, rowspan=1)
        self.btn_reset=tkinter.Button(window, text="...leaving", width=50, command=self.noHumanLeaving)
        self.btn_reset.grid(row=2,column=3, columnspan=1, rowspan=1)
        #maxNumber
        self.maximumValueLabel = tkinter.Label(window, text="Current Maximum Number is "+str(maximumValue) +". Do you want to change?")
        self.maximumValueLabel.grid(row=3, column=1)
        self.enter = tkinter.Entry(window)
        self.enter.grid(row=3, column=2)
        tkinter.Button(window, text='Set Maximum Number', command=self.setMaximum).grid(row=3, column=3)
        #Resetbutton
        self.btn_reset=tkinter.Button(window, text="Reset", width=50, command=self.resetNumbers)
        self.btn_reset.grid(row=4,column=1, columnspan=2, rowspan=1)
        #show total number
        self.labelIn=tkinter.Label(window,text= "Todays visitors: "+str(countIn),bg='gold',fg='blue')
        self.labelIn.grid(row=4,column=3)
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 5
        self.update()
        self.window.mainloop()
    def noHumanComingIn(self):
        global countIn
        global countCurrentIn
        countIn -= 1
        countCurrentIn -= 1
        self.labelIn.config(text="Todays visitors: "+str(countIn))
        self.labelCurrentIn.config(text="currently inside: "+str(countCurrentIn))
        self.data = [{"sensor":senseboxVars['total_num_people_id'], "value": countIn},{"sensor":senseboxVars['current_people_id'], "value":countCurrentIn}]
        self.r = requests.post(url, json=self.data, headers=headers)
        print(self.r.status_code)
        self.writer.writerow({'Date': time.strftime("%d-%m-%Y"),'Time': time.strftime("%H-%M-%S"), 'Current Visitors': countCurrentIn, 'Total Visitors': countIn})
    def noHumanLeaving(self):
        global countOut
        global countCurrentIn
        countOut -= 1
        countCurrentIn += 1
        self.data = [{"sensor":senseboxVars['current_people_id'], "value":countCurrentIn}]
        self.r = requests.post(url, json=self.data, headers=headers)
        print(self.r.status_code)
        self.writer.writerow({'Date': time.strftime("%d-%m-%Y"),'Time': time.strftime("%H-%M-%S"), 'Current Visitors': countCurrentIn, 'Total Visitors': countIn})
        self.labelCurrentIn.config(text="currently inside: "+str(countCurrentIn))  
    def setMaximum(self):
        global maximumValue
        maximumValue = int(self.enter.get())
        self.maximumValueLabel.config(text="Current Maximum Number is "+str(maximumValue) +". Do you want to change?") 
    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("./saved_pictures/frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    def countIn(self):
        global countIn
        global countCurrentIn    
        countIn += 1
        countCurrentIn += 1
        self.labelIn.config(text="Todays visitors: "+str(countIn))
        self.labelCurrentIn.config(text="currently inside: "+str(countCurrentIn))
        self.data = [{"sensor":senseboxVars['total_num_people_id'], "value": countIn},{"sensor":senseboxVars['current_people_id'], "value":countCurrentIn}]
        self.r = requests.post(url, json=self.data, headers=headers)
        print(self.r.status_code)
        self.writer.writerow({'Date': time.strftime("%d-%m-%Y"),'Time': time.strftime("%H-%M-%S"), 'Current Visitors': countCurrentIn, 'Total Visitors': countIn})
    def countOut(self):
        global countOut
        global countCurrentIn
        countOut += 1
        if (countCurrentIn >0):
            countCurrentIn -= 1
        self.labelCurrentIn.config(text="currently inside: "+str(countCurrentIn))
        self.data = [{"sensor":senseboxVars['current_people_id'], "value":countCurrentIn}]
        self.r = requests.post(url, json=self.data, headers=headers)
        print(self.r.status_code)
        self.writer.writerow({'Date': time.strftime("%d-%m-%Y"),'Time': time.strftime("%H-%M-%S"), 'Current Visitors': countCurrentIn, 'Total Visitors': countIn})
    def resetNumbers(self):
        global countIn
        global countOut
        global countCurrentIn
        self.labelIn.config(text="Todays visitors: "+str(countIn))
        countOut = countIn
        countCurrentIn = 0
        self.labelCurrentIn.config(text="Currently inside: "+str(countCurrentIn))
        self.data = [{"sensor":senseboxVars['total_num_people_id'], "value": countIn},{"sensor":senseboxVars['current_people_id'], "value":countCurrentIn}]
        self.r = requests.post(url, json=self.data, headers=headers)
        print(self.r.status_code)
        self.writer.writerow({'Date': time.strftime("%d-%m-%Y"),'Time': time.strftime("%H-%M-%S"), 'Current Visitors': countCurrentIn, 'Total Visitors': countIn})
    def update(self):
        global avg
        global xvalues
        global motion
        global OptionList
        global buzzer
        global countCurrentIn
        global countIn
        global countOut
        global maximumValue
        OptionList = ["from left to right", "from right to left", "from up to down", "from down to up"]
        
        if (countCurrentIn > maximumValue):
            GPIO.output(buzzer,GPIO.HIGH)
            sleep(0.5) # Delay in seconds
            GPIO.output(buzzer,GPIO.LOW)
            sleep(0.5)
        
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        
        flag = True
        text = ""

        cv2.imshow('Input', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if avg is None:
            print("[INFO] starting background model...")
            avg = gray.copy().astype("float")

        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            if cv2.contourArea(c) < 5000:
                continue
            if (self.variable.get() == OptionList[0] or self.variable.get() == OptionList[1]):
                (x, y, w, h) = cv2.boundingRect(c)
                xvalues.append(x)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                flag = False
            else:
                (x, y, w, h) = cv2.boundingRect(c)
                xvalues.append(y)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                flag = False

        no_x = len(xvalues)
        if (no_x > 2):
            if (self.variable.get() == OptionList[0] or self.variable.get() == OptionList[2]):
                difference = xvalues[no_x - 1] - xvalues[no_x - 2]
                if(difference > 0):
                    motion.append(1)
                else:
                    motion.append(0)
            else:
                difference = xvalues[no_x - 1] - xvalues[no_x - 2]
                if(difference < 0):
                    motion.append(1)
                else:
                    motion.append(0)    

        if flag is True:
            if (no_x > 5):
                print(motion)
                val, times = find_majority(motion)
                print(val)
                print(times)
                #self.snapshot()
                if val == 1 and times >= 10:
                    self.countIn()
                else:
                    self.countOut()
            xvalues = list()
            motion = list()
        if ret:
            self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        #video_source = cv2.rotate(video_source, cv2.ROTATE_90_CLOCKWISE)
        self.vid = cv2.VideoCapture(video_source)
        
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        # Check if the webcam is opened correctly
        if not self.vid.isOpened():
            raise IOError("Cannot open webcam")
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            


# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")