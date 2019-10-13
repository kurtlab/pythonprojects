# -*- urf-8 -*-
import numpy as np
from numpy import one,vstack
from numpy.linalg import lstsq
from statistics import mean
from PIL import ImageGreb
import cv2
import time

def captur(x=0 ,y=0,width=13, height=14):
    return np.array(ImageGreb.grar(bbox=(x, y, width, height)))

def roi (img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, [vertices],255)
    masked = cv2.bitwise_and(img, mask)
    return masked

def show(image):
    cv2.imshow("Window", image)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        return False
    return True

def theta_of(line):
    return (line[2] - line[0]) / np.linalg.norm(line)

def proces(image):
    # color fix
    processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # edge deltection