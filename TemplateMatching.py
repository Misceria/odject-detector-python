
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import os


TEMPLATES_DIR = 'C:\\Users\\klopp\\GitHub-directories\\drone-detector-python\\Imgs\\Templates'



def videoMatcher(video, templates_dir):
    cap = cv.VideoCapture(video)
    if cap.isOpened()==False:
        print("Error reading video stream file")
    while cap.isOpened:
        ret, frame = cap.read()
        if ret==True:
            frame = templateMatching(frame, templates_dir=TEMPLATES_DIR)
            cv.imshow("Video stream", frame)

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


def main():
    source_video = "C:\\Users\\klopp\\GitHub-directories\\drone-detector-python\\Imgs\\drone_vid.mp4"
    template_image = "C:\\Users\\klopp\\GitHub-directories\\drone-detector-python\\Imgs\\Templates\\template_image_2.png"
    videoMatcher(source_video, TEMPLATES_DIR)
    #templateMatching(source_image, template_image)


if __name__=="__main__":
    main()




