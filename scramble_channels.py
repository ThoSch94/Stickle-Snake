import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


path = "/data/users/tschiller/Research_project/images/train/"
# Bild laden    
for file in os.listdir(path):
    if file.endswith(('.jpg', '.JPG')):
        image = plt.imread(path+file)
        r, g, b = cv2.split(image)
        channels = [r, g, b]
        np.random.shuffle(channels)
        image_mixed = cv2.merge((channels[0], channels[1], channels[2]))

        plt.imsave("/data/users/tschiller/Research_project/images_scrambled/train/"+file, image_mixed)

path = "/data/users/tschiller/Research_project/images/test/"
# Bild laden    
for file in os.listdir(path):
    if file.endswith(('.jpg', '.JPG')):
        image = plt.imread(path+file)
        r, g, b = cv2.split(image)
        channels = [r, g, b]
        np.random.shuffle(channels)
        image_mixed = cv2.merge((channels[0], channels[1], channels[2]))
        plt.imsave("/data/users/tschiller/Research_project/images_scrambled/test/"+file, image_mixed)

