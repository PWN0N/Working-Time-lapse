import signal
import numpy as np
from PIL import ImageGrab
import cv2
import time
import sys
import os

flips_time_mins = 30
interval = 5  # seconds
num_frames = flips_time_mins*60/interval
num_frames = int(num_frames)
year = -1
month = -1
day = -1

out_fps = 24
cammode = 0
shutdown_msg = False

def signal_handler(signal,frame):
    print('You Pressed Ctrl+C, The Program Will Be Shutdown')
    global shutdown_msg
    shutdown_msg = True
    print('Saving Videos')

def add_timestamp(img):

    time_str= time.strftime("%Y-%m-%d %H:%M:%S")

    color=(255,255,255)
    if np.mean( img[700:780,900:950])>128:
        color=(0,0,0)

    cv2.putText(img, time_str, (900, 700) ,cv2.FONT_HERSHEY_SIMPLEX ,0.8, color ,2)
    return img

capture = cv2.VideoCapture(0)
capture1 = cv2.VideoCapture(1)

cam, _ = capture.read()
cam1, _ = capture1.read()

if(cam and cam1):
    print('Dual Camera Mode')
    cammode = 1
elif(cam):
    print('Single Camera Mode')
    cammode = 2
else:
    print('No Camera Detect!')
    sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)

# capture frames to video
while True:
    if(day != time.strftime("%d")):
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%d")
        hour = time.strftime("%H")
        save_dir = "{0}/{1}/{2}".format(year, month, day)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
# innner camera init
    size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    codec = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')
    cam_filename = save_dir+"/cam_{:4}.avi".format(time.strftime("%H%M"))
    video = cv2.VideoWriter(cam_filename, codec, out_fps, size)
    # for low quality webcams, discard the starting unstable frames
    for i in range(20):
        capture.read()

# desktop screen init
    desktopim = np.array(ImageGrab.grab().convert('RGB'))
    #    desktopFrame =np.array(desktopim.getdata(),dtype='uint8')\
    #        .reshape((desktopim.size[1],desktopim.size[0],3))
    sp = desktopim.shape
    sz1 = sp[0]  # height(rows) of image
    sz2 = sp[1]  # width(colums) of image
    desktopsize = (int(sz2),int(sz1))
    codec = cv2.VideoWriter.fourcc('M', 'J', 'P', 'G')
    desktop_filename = save_dir+"/desktop_{:4}.avi".format(time.strftime("%H%M"))
    desktopvideo = cv2.VideoWriter(desktop_filename, codec, out_fps, desktopsize)

# outter camera init
    if (cammode == 1):
        size1 = (int(capture1.get(cv2.CAP_PROP_FRAME_WIDTH)),
                 int(capture1.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        cam1_filename = save_dir+"/cam1_{:4}.avi".format(time.strftime("%H%M"))
        video1 = cv2.VideoWriter(cam1_filename, codec, out_fps, size1)
        # for low quality webcams, discard the starting unstable frames
        for i in range(20):
            capture1.read()


    for i in range(num_frames):
        if (shutdown_msg):
            break
        _, frame = capture.read()


        video.write(add_timestamp(frame))

        desktopim = np.array(ImageGrab.grab().convert('RGB'))


        # ImageGrab and OpenCV have different color space
        desktopFrame = cv2.cvtColor(desktopim, cv2.COLOR_BGR2RGB)

        desktopvideo.write(add_timestamp(desktopFrame))

        if (cammode == 1):
            _, frame1 = capture1.read()
            video1.write(add_timestamp(frame1))

        time.sleep(interval)

    video.release()
    desktopvideo.release()
    if (cammode == 1):
        video1.release()
    if (shutdown_msg):
        break

capture.release()
if(cammode ==1):
    capture1.release()

print('Done!')
print('Exit The Program')
sys.exit(0)
