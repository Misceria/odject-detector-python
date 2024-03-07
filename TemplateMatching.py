

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import os
from copy import deepcopy
from math import sqrt
from scipy.signal import medfilt


TEMPLATES_DIR = 'C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\Templates'



def videoMatcher(video, templates_dir):
    cap = cv.VideoCapture(video)
    if cap.isOpened()==False:
        print("Error reading video stream file")
    once = True
    while cap.isOpened:
        ret, frame = cap.read()
        if once:
            once = False
            h, w, _ = frame.shape
            sub_frame = cv.resize(frame, (int(w//3), int(h//3)))
            #print(sub_frame)
            ROI = cv.selectROI("Select", sub_frame)
            ROI = [x*3 for x in ROI]
            print(ROI)
        if ret==True:
            #sky_frame, mask = getSky(frame)
            #frame = templateMatching(sky_frame, templates_dir=TEMPLATES_DIR, thresh=0.73)
            
            #frame_without_horizon, mask = imageMatcher(frame, size_decrease=1)
            #frame_canny, contour = CannyContours(frame_without_horizon, pre_max=True)
            #frame_canny = frame[ROI[0]:ROI[2], ROI[1]:ROI[3]]
            #print(frame_canny.shape)
            #print(frame.shape)
            framy_canny = CannyContours(frame[ROI[1]:ROI[1]+ROI[3], ROI[0]:ROI[0]+ROI[2]], biggest=True)
            frame_harris = HarrisMethod(frame[ROI[1]:ROI[1]+ROI[3], ROI[0]:ROI[0]+ROI[2]])
            cv.imshow("HARRIS", frame_harris)
            #frame = CannyContours(frame)
            
            """height, width, _ = frame.shape
            cv.drawContours(frame, contour, -1, (0, 0, 255), 2)
            frame = cv.resize(frame, (int(width//3), int(height//3)))
            cv.imshow("Template Matching", frame)
            """
            if cv.waitKey(25) & 0xFF == ord('q'):
                break
        
        else:   
            break


def imageMatcher(source_image, show=False, size_decrease=4):
    try:
        source_image = cv.imread(source_image)
    except:
        pass
    height, width, _ = source_image.shape
    source_image_grey = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    
    #frame = templateMatching(source_image_grey, templates_dir=TEMPLATES_DIR, thresh=0.73)
    #frame = HarrisMethod(frame)
    image, mask = getSky(source_image)
    #sky_image = CannyContours(image)
    print("EXND")
    if show:  
        show_image = cv.resize(source_image, (width//size_decrease, height//size_decrease))
        cv.imshow("dasd", show_image)
        cv.waitKey(0)
    return image, mask
    

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
                            - EuclideanDistance((dots_y[dot], dots_x[dot]), (0, dots_x[dot]))*1.35\
                            - (dots_y[dot]-size[0])**2
                            
        all_distances.append(summ_distance/len(dots_y))
    try:
        return (dots_x[all_distances.index(max(all_distances))], dots_y[all_distances.index(max(all_distances))])
    except ValueError:
        return None
    
    
def EuclideanDistance(point1, point2):
    return (sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2))


def calSkyline(mask):
    height, width = mask.shape
    for i in range(width):
        raw = mask[:, i]
        after_median = medfilt(raw, 19)
        try:
            first_zero_index = np.where(after_median==0)[0][0]
            first_one_index = np.where(after_median==1)[0][0]
            if first_zero_index >= 0:
                mask[first_one_index:first_zero_index, i] = 1
                mask[first_zero_index:, i] = 0
                mask[:first_one_index, i] = 0   
        except:
            continue
    #plt.imshow(mask)
    #plt.show()
    mask = cv.medianBlur(mask, 107) #205
    return mask


def getSky(image):
    height, width, _ = image.shape
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    image_gray = cv.blur(image_gray, (2,2))
    cv.medianBlur(image_gray, 5)
    lap = cv.Laplacian(image_gray, cv.CV_8U)
    gradient_mask = (lap < 6).astype(np.uint8)
    
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 30))
    mask = cv.morphologyEx(gradient_mask, cv.MORPH_OPEN, kernel)
    #plt.imshow(mask)
    #plt.show()
    mask = calSkyline(mask)
    final_image = cv.bitwise_and(image, image, mask=mask)
    return final_image, mask


def HarrisMethod(source_image, mask=None):
    
    """
    
    
    """
    
    rows, cols, _ = source_image.shape
    
    gray = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv.cornerHarris(gray, 2,3,0.1)
    #result is dilated for marking the corners, not important
    #dst = cv.dilate(dst,None)
    #dst = cv.erode(dst, np.ones((1,1), np.uint8), iterations=1)
    dots_y, dots_x = np.where(dst>0.01*dst.max())
    print(len(dots_y), len(dots_y))
    if len(dots_y) > 500:
        print(len(dots_y), len(dots_x))
        indexes = np.random.random_integers(0, len(dots_y)-1, 500)
        print(len(indexes))
        dots_y = []
        dots_x = []
    main_dot = EuclideanDistanceMax(dots_y, dots_x, (rows, cols))
    if main_dot:
        source_image = cv.circle(source_image, main_dot, 10, (0,0,255), 3)
        #print(main_dot)
        source_image[dst>0.01*dst.max()]=[0, 0, 255]
        #dots = np.argwhere(dst>0.01*dst.max())
        # Threshold for an optimal value, it may vary depending on the image.
        #source_image[dst>0.01*dst.max()]=[0,0,255]
    return source_image
        
        
def nothing():
    """
    
    do absolutely nothing
    
    """
    
    
    pass


def findFilters(source_image, size_decrease=1):
    
    """
    input: source_image - Входное изображение на которое применятся фильтры
            size_decrease - величина изменения размера изображения
            
    Эта функция позволяет поэесперементировать с диапазоном значений минимума и максимума яркости,
    на которое реагирует детектор, а также размытие
    
    """
    
    cv.namedWindow( "result" ) # создаем главное окно
    cv.namedWindow( "settings" ) # создаем окно настроек
    try:
        source_image = cv.imread(source_image)
    except:
        pass
    try:
        height, width, _ = source_image.shape
        source_image_grey = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    except:
        height, width = source_image.shape
        source_image_grey = source_image
    
    # создаем 6 бегунков для настройки начального и конечного цвета фильтра
    cv.createTrackbar('min', 'settings', 0, 255, nothing)
    cv.createTrackbar('max', 'settings', 0, 255, nothing)  
    cv.createTrackbar('blur', 'settings', 3, 50, nothing)  
    
    while True:
        minbr = cv.getTrackbarPos('min', 'settings')
        maxbr = cv.getTrackbarPos('max', 'settings') 
        blur = cv.getTrackbarPos('blur', 'settings')
        
        br_min = np.array(minbr, np.uint8)
        br_max = np.array(maxbr, np.uint8) 
        
        thresh = cv.inRange(source_image_grey, br_min, br_max)
        try:
            thresh = cv.medianBlur(thresh, blur)
        except:
            pass
        height, width = thresh.shape
        thresh = cv.resize(thresh, (width//size_decrease, height//size_decrease))
        cv.imshow('result', thresh)
        
        ch = cv.waitKey(5)
        if ch == 27:
            break
        
        
def CannyContours(source_image, size_decrease=1, show=False, biggest=False, pre_max=False, show_edges=False):
    
    """
    source_image - входное изображение
    size_decrease - степень уменьшения размера вывода изображения
    show - вывод изображения
    biggest - метод выбора наибольшего контура
    pre_max - метод выбора второго по размеру контура
    show_edges - вывод маски обнаружения
    Если не выбрано ничего из (biggest, pre_max) будут выведены все контуры
    
    """
    
    very_source_image = deepcopy(source_image)
    try:
        source_image = cv.imread(source_image)
    except:
        pass
    source_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    #ret, thresh = cv.threshold(source_image, 180, 255, 0)
    edges = cv.Canny(source_image , 50,255)
    edges = cv.GaussianBlur(edges, (17,17), 0)
    #edges = cv.GaussianBlur(edges, (3,3), 0)
    if show_edges:
        showImage(edges, size_decrease, "Canny edges")
    contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    if pre_max:
        contours = sorted(contours,key=len)
        try:
            cont = contours[-2]
            image_with_contours = cv.drawContours(very_source_image, cont, -1, (0,255, 0),3)
            return very_source_image, cont
        except:
            return very_source_image, []
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours PRE_MAX")
        contours = cont
    elif biggest:
        try:
            biggest_cont = max(contours, key=len)
            image_with_contours = cv.drawContours(very_source_image, contours, -1, (0,255, 0),3)
        except:
            image_with_contours, biggest_cont = very_source_image, None
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours BIGGEST")
        contours = biggest_cont
    else:
        image_with_contours = cv.drawContours(very_source_image, contours, -1, (0,255, 0),3)
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours ALL")
    return image_with_contours, contours


def showImage(source_image, size_decrease, name_image = "Sample"):
    if len(source_image.shape) == 3:
        h,w,_ = source_image.shape
    else:
        h, w = source_image.shape
    show_image = cv.resize(source_image, (w//size_decrease, h//size_decrease))
    cv.imshow('canny Contours', show_image)
    cv.waitKey(0)
        

def main():
    source_video = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\drone_vid.mp4"
    source_photo = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\source_image.png"
    app = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\174ND810_10_02\\DSC_1076.MOV"
    #source_photo = cv.imread(source_photo)
    #findFilters(source_photo, size_decrease=3)
    #image = imageMatcher(source_photo, size_decrease=2, show=True)
    #CannyContours(source_photo, size_decrease=2, show=True)
    videoMatcher(app, TEMPLATES_DIR)
    #templateMatching(source_image, template_image)


if __name__=="__main__":
    main()




