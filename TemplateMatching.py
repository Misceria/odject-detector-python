
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import os


TEMPLATES_DIR = 'C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\Templates'




def videoMatcher(video, templates_dir):
    cap = cv.VideoCapture(video)
    if cap.isOpened()==False:
        print("Error reading video stream file")
    while cap.isOpened:
        ret, frame = cap.read()
        if ret==True:
            frame = templateMatching(frame, templates_dir=TEMPLATES_DIR, thresh=0.73)
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
            #cv.putText(source_image, str(thresh), (x1, y1), cv.FONT_HERSHEY_COMPLEX, 1, (255, 100, 100), 2)
            
    if show_only:
        plt.imshow(source_image, cmap='gray')
        plt.show()
    else:
        return source_image


def brightnessMatching(source_image, show_only=False, thresh=0.7):
    rows,cols,_ = source_image.shape
    img = np.zeros((rows, cols, 1), dtype=np.uint8)
    for y in range(rows):
        for x in range(cols):
            pixel = source_image[y, x]
            img[y,x] = sum(pixel)/3
    cv.imshow("IMG", img)
    cv.waitKey(0)
            

def main():
    source_video = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\drone_vid.mp4"
    source_photo = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\source_image.png"
    source_photo = cv.imread(source_photo)
    #videoMatcher(source_video, TEMPLATES_DIR)
    brightnessMatching(source_photo)
    #templateMatching(source_image, template_image)


if __name__=="__main__":
    main()




