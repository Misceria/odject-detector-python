
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import os
from copy import deepcopy
from math import sqrt


TEMPLATES_DIR = 'C:\\Users\\klopp\\GitHub-directories\\drone-detector-python\\Imgs\\Templates'



def videoMatcher(video, templates_dir):
    cap = cv.VideoCapture(video)
    if cap.isOpened()==False:
        print("Error reading video stream file")
    while cap.isOpened:
        ret, frame = cap.read()
        if ret==True:
            #frame = templateMatching(frame, templates_dir=TEMPLATES_DIR, thresh=0.73)
            frame = HarrisMethod(frame)
            cv.imshow("Template Matching", frame)

            if cv.waitKey(25) & 0xFF == ord('q'):
                break
        
        else:
            break



def templateMatching(source_image, templates_dir, show_only=False, show_only_one=True, thresh=0.7):

    source_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    
    for template in os.listdir(templates_dir):
        #print(os.listdir(templates_dir))
        template_image = cv.imread(TEMPLATES_DIR+'\\'+template)
        template_image = cv.cvtColor(template_image, cv.COLOR_BGR2GRAY)
        w, h = template_image.shape[::-1]

        methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
                'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

        method = cv.TM_CCOEFF_NORMED
        res = cv.matchTemplate(source_image, template_image, method)
        (y_points, x_points) = np.where(res >= thresh) 
        boxes = list() 
        
        for (x, y) in zip(x_points, y_points): 
            boxes.append((x, y, x + w, y + h)) 

        for (x1, y1, x2, y2) in boxes:   
            cv.rectangle(source_image, (x1, y1), (x2, y2), 
                        (40, 70, 25), 3) 
        
    


        #top_left = max_loc
        #bottom_right = (top_left[0]+w, top_left[1]+h)

        #cv.rectangle(source_image, top_left, bottom_right, 255, 2)
    if show_only:
        plt.imshow(source_image, cmap='gray')
        plt.show()
    else:
        return source_image


def brigthness_estimation(image, pixel):
    summ = 0
    for y in range(-1, 1):
        for x in range(-1, 1):
            summ += sum(image[pixel[0]+y, pixel[1]+x])
    return summ/6120
    

def EuclideanDistanceMax(dots_y, dots_x, size):
    all_distances = []
    #print(len(dots))
    for dot in range(len(dots_y)):
        summ_distance = 0
        for cont_dot in range(len(dots_y)):
            
            # Наиболее удалённая точка со штрафом удалённости от центра изображения
            
            """summ_distance += EuclideanDistance((dots_y[dot], dots_x[dot]), (dots_y[cont_dot], dots_x[cont_dot])) \
                            - EuclideanDistance((dots_y[dot], dots_x[dot]), (int(size[0]/2), dots_x[dot])) \
                            - EuclideanDistance((dots_y[dot], dots_x[dot]), (dots_y[dot], int(size[1]/2)))"""
                            
            # Наиболее удалённая точка со штрафом удалённости от верха изображения
            
            summ_distance += EuclideanDistance((dots_y[dot], dots_x[dot]), (dots_y[cont_dot], dots_x[cont_dot])) \
                            - EuclideanDistance((dots_y[dot], dots_x[dot]), (0, dots_x[dot]))*1.35
                            
        all_distances.append(summ_distance/len(dots_y))
    return (dots_x[all_distances.index(max(all_distances))], dots_y[all_distances.index(max(all_distances))])
    
def EuclideanDistance(point1, point2):
    return (sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2))


def HarrisMethod(source_image):
    rows,cols,_ = source_image.shape
    
    gray = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv.cornerHarris(gray, 2,3,0.2)
    #result is dilated for marking the corners, not important
    #dst = cv.dilate(dst,None)
    #dst = cv.erode(dst, np.ones((1,1), np.uint8), iterations=1)
    dots_y, dots_x = np.where(dst>0.15*dst.max())
    #print(len(dots_y), len(dots_x))
    main_dot = EuclideanDistanceMax(dots_y, dots_x, (rows, cols))
    source_image = cv.circle(source_image, main_dot, 10, (0,0,255), 3)
    print(main_dot)
    source_image[dst>0.01*dst.max()]=[0,0,255]
    #dots = np.argwhere(dst>0.01*dst.max())
    # Threshold for an optimal value, it may vary depending on the image.
    #source_image[dst>0.01*dst.max()]=[0,0,255]
    return source_image
            

def main():
    source_video = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\drone_vid.mp4"
    source_photo = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\source_image.png"
    source_photo = cv.imread(source_photo)
    videoMatcher(source_video, TEMPLATES_DIR)
    #templateMatching(source_image, template_image)


if __name__=="__main__":
    main()




