

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import os
from copy import deepcopy
from math import sqrt
from scipy.signal import medfilt
import imutils
import joblib


TEMPLATES_DIR = 'C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\Templates'



def videoMatcher(video, harris=False, canny=False, template_matching=False, size_decrease=1, choose_ROI = False):
    
    """
    
    Функция применения методов к видеопотоку
    
    """
    
    cap = cv.VideoCapture(video)
    if cap.isOpened()==False:
        print("Error reading video stream file")
    once = True
    while cap.isOpened:
        ret, frame = cap.read()
        if once:
            once = False
            h, w, _ = frame.shape 
        if choose_ROI:
            mask = drawRoi(frame)
            choose_ROI=False
        else:
            mask = None
        if ret==True:
            if harris:
                HarrisMethod(frame, show=True, size_decrease=size_decrease, wait_click=False, mask = mask)
            if canny:
                CannyContours(frame, show=True, size_decrease=size_decrease, wait_click=False, mask=mask)
            if template_matching:
                templateMatching(frame, TEMPLATES_DIR, show=True, size_decrease=size_decrease, wait_click=False, mask=mask)
            
            key_clicked = cv.waitKey(25)
            if key_clicked & 0xFF == ord('q'):
                break
            elif key_clicked & 0xFF == ord('r'):
                choose_ROI = True
        
        else:   
            break


def imageMatcher(source_image, show=False, size_decrease=4):
    
    """
    
    Функция для применения методов к изображению
    
    """
    
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
    

def templateMatching(source_image, templates_dir, show=False, thresh=0.7, mask = [], wait_click=True, size_decrease=1):
    
    
    """
    
    Метод обнаружения объекта на изображении по схожести с шаблонами
    source_image - исхожное изображение
    templates_dir - путь к папке с шаблонами
    show - вывод изображения
    thresh - степень уверенности
    
    
    """
    changed_source_image = cv.bitwise_and(source_image, mask)
    changed_source_image = cv.cvtColor(changed_source_image, cv.COLOR_BGR2GRAY)

    
    for template in os.listdir(templates_dir):
        #print(os.listdir(templates_dir))
        template_image = cv.imread(TEMPLATES_DIR+'\\'+template)
        template_image = cv.cvtColor(template_image, cv.COLOR_BGR2GRAY)
        w, h = template_image.shape[::-1]

        methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
                'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']

        method = cv.TM_CCOEFF_NORMED
        res = cv.matchTemplate(changed_source_image, template_image, method)
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
    if show:
        showImage(source_image, size_decrease=size_decrease, name_image="Template Matching", wait_click=wait_click)
    return source_image


def brigthnessEstimation(image, pixel):
    
    """
    
    Оценивает среднюю яркость точки и ближайших соседей
    

    """
    
    summ = 0
    for y in range(-1, 1):
        for x in range(-1, 1):
            summ += sum(image[pixel[0]+y, pixel[1]+x])
    return summ/6120
    

def EuclideanDistanceMax(dots_y, dots_x, size):
    
    """

    Находит наиболее удалённую от остальных точку
    
    dots_y - координаты точек по y
    dots_x - координаты точек по x
    size - количество точек
    
    """
    
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
    
    """

    Calculates euclidean distance between two points in 2 dimensional grid
    
    
    """
    
    return (sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2))


def calSkyline(mask):
    
    """
    
    Gets raw mask and returns horizon line
    
    """
    
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


def getSky(image, show=False, show_mask=False, size_decrease=1):
    
    """
    
    This func gets image and returns sky part of image and it's mask
    image - входное изображение, на котором необходимо найти небо
    
    """
    
    height, width, _ = image.shape
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    image_gray = cv.blur(image_gray, (2,2))
    cv.medianBlur(image_gray, 5)
    lap = cv.Laplacian(image_gray, cv.CV_8U)
    gradient_mask = (lap < 6).astype(np.uint8)
    
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 30))
    mask = cv.morphologyEx(gradient_mask, cv.MORPH_OPEN, kernel)
    mask = calSkyline(mask)
    final_image = cv.bitwise_and(image, image, mask=mask)
    if show:
        showImage(final_image, size_decrease, "Sky")
    if show_mask:
        showImage(mask, size_decrease, "Sky Mask")
    
    return final_image, mask


def HarrisMethod(source_image, mask=[], show = False, size_decrease=1, wait_click=True):
    
    """
    THIS FUNCTION NEEDS REFACTORING
    source_image - входное изображение
    mask - маска области в которой происходит поиск (NEED REALISATION)
    
    
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
    if mask == []:
        if len(dots_y) > 500:
            print(len(dots_y), len(dots_x))
            indexes = np.random.random_integers(0, len(dots_y)-1, 500)
            print(len(indexes))
            n_dots_x = []
            n_dots_y = []
            for ind in indexes:
                n_dots_x.append(dots_x[ind])
                n_dots_y.append(dots_y[ind])
    else:
        n_dots_x = []
        n_dots_y = []
        for ind in range(len(dots_x)):
            if mask[dots_y[ind], dots_x[ind]].all() == 1:
                n_dots_x.append(dots_x[ind])
                n_dots_y.append(dots_y[ind])  
    main_dot = EuclideanDistanceMax(n_dots_y, n_dots_x, (rows, cols))
    if main_dot:
        source_image = cv.circle(source_image, main_dot, 10, (0,0,255), 3)
        #print(main_dot)
        #source_image[dst>0.01*dst.max()]=[0, 0, 255]
        source_image[dots_y, dots_x]=[0, 0, 255]
        #dots = np.argwhere(dst>0.01*dst.max())
        # Threshold for an optimal value, it may vary depending on the image.
        #source_image[dst>0.01*dst.max()]=[0,0,255]
    if show:
        showImage(source_image, size_decrease, "Harris Method", wait_click=wait_click)
    return source_image, main_dot
        
        
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
        
        
def CannyContours(source_image, size_decrease=1, show=False, biggest=False, pre_max=False, show_edges=False, smallest=False, mask = None, wait_click=True):
    
    """
    source_image - входное изображение
    size_decrease - степень уменьшения размера вывода изображения
    show - вывод изображения
    biggest - метод выбора наибольшего контура
    pre_max - метод выбора второго по размеру контура
    show_edges - вывод маски обнаружения
    Если не выбрано ничего из (biggest, pre_max) будут выведены все контуры
    
    """

    
    try:
        source_image = cv.imread(source_image)
    except:
        pass
    very_source_image = deepcopy(source_image)
    if mask:
        print(mask.shape, source_image.shape)
        source_image = cv.bitwise_and(source_image, mask)
    #cv.imshow("BITWISE", source_image)
    #cv.waitKey(0)
    source_image = cv.cvtColor(source_image, cv.COLOR_BGR2GRAY)
    #ret, thresh = cv.threshold(source_image, 180, 255, 0)
    edges = cv.Canny(source_image , 50,255)
    edges = cv.GaussianBlur(edges, (17,17), 0)
    #edges = cv.GaussianBlur(edges, (3,3), 0)
    if show_edges:
        showImage(edges, size_decrease, "Canny edges", wait_click=wait_click)
    contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #contours = sorted(contours, key=len)[:-2]
    print(len(contours))
    if pre_max:
        contours = sorted(contours,key=len)
        try:
            cont = contours[-2]
            image_with_contours = cv.drawContours(very_source_image, cont, -1, (0,255, 0),3)
            contours = cont
        except:
            image_with_contours, contours =  very_source_image, []
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours PRE_MAX", wait_click=wait_click)
        contours = cont
    elif biggest:
        try:
            biggest_cont = max(contours, key=len)
            image_with_contours = cv.drawContours(very_source_image, biggest_cont, -1, (0,255, 0),3)
        except:
            image_with_contours, biggest_cont = very_source_image, None
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours BIGGEST", wait_click=wait_click)
        contours = biggest_cont
    elif smallest:
        try:
            smallest_cont = min(contours, key=len)
            image_with_contours = cv.drawContours(very_source_image, smallest_cont, -1, (0,255, 0),3)
        except:
            image_with_contours, smallest_cont = very_source_image, None
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours BIGGEST", wait_click=wait_click)
        contours = smallest_cont
    else:
        image_with_contours = cv.drawContours(very_source_image, contours, -1, (0,255, 0),3)
        if show:
            showImage(image_with_contours, size_decrease, "Canny Contours ALL", wait_click=wait_click)
    return image_with_contours, contours


def showImage(source_image, size_decrease=1, name_image = "Sample", wait_click=False):
    
    """
    
    Shows image on screen
    source_image - входное изображение
    size_decrease - степень уменьшения изображения
    name_imaage - имя окна для вывода
    
    """
    if len(source_image.shape) == 3:
        h,w,_ = source_image.shape
    else:
        h, w = source_image.shape
    show_image = cv.resize(source_image, (w//size_decrease, h//size_decrease))
    cv.imshow(name_image, show_image)
    if wait_click:
        cv.waitKey(0)
        
        
def showImages(source_images, size_decrease=1, name_images = ["Sample"], wait_click = False):
    
    """
    
    Shows many images on screen at once
    source_image - массив входных изображений
    size_decrease - степень уменьшения изображения
    name_imaage - массив имён окон для вывода
    
    """
    for image_num in range(len(source_images)):
        if len(source_images[image_num].shape) == 3:
            h,w,_ = source_images[image_num].shape
        else:
            h, w = source_images[image_num].shape
        show_image = cv.resize(source_images[image_num], (w//size_decrease, h//size_decrease))
        cv.imshow(name_images[image_num], show_image)
    if wait_click:
        cv.waitKey(0)
        

def drawRoi(source_image, size_decrease=1):
    
    """
    
    Позволяет вручную выбрать ROI для изображения
    source_image - исходное изображение
    
    returns:
        mask - маска объекта выделенной зоны интереса
    """
    
    global pts, size_decrease_for_draw_roi
    size_decrease_for_draw_roi = size_decrease
    pts = []
    try:
        img = cv.imread(source_image)
    except:
        img = source_image
    cv.namedWindow('Select Polygonal ROI')
    cv.setMouseCallback('Select Polygonal ROI', drawRoiEvent, img)
    print("[INFO] Используйте ЛКМ для выбора области")
    print("[INFO] Используйте ПКМ для отмены")
    print("[INFO] Используйте CКМ для завершения области")
    print("[INFO] Используйте S для сохранения области")
    print("[INFO] Нажмите ESC для выхода")
    cv.imshow('Select Polygonal ROI', img)
    while True:
        key = cv.waitKey(1) & 0xFF
        if key == 27:
            break
        if key == ord("s"):
            saved_data = {
                "ROI": pts
            }
            joblib.dump(value=saved_data, filename="config.pkl")
            print("[INFO] ROI сохранён.")
            break
    cv.destroyAllWindows()
    
    return mask2


def drawRoiEvent(event, x, y, flags, img):
    
    """
    
    Обработчик события нажатия на изображение
    event - событие
    x - точка нажатия по оси абсцисс
    y - точка нажатия по оси ординат
    
    """
    global mask, mask2, mask3, size_decrease_for_draw_roi
    img2 = img.copy()

    if event == cv.EVENT_LBUTTONDOWN:
        pts.append((x, y))  

    if event == cv.EVENT_RBUTTONDOWN:
        pts.pop()  

    if event == cv.EVENT_MBUTTONDOWN:
        mask = np.zeros(img.shape, np.uint8)
        points = np.array(pts, np.int32)
        points = points.reshape((-1, 1, 2))
        
        mask = cv.polylines(mask, [points], True, (255, 255, 255), 2)
        mask2 = cv.fillPoly(mask.copy(), [points], (255, 255, 255))
        mask3 = cv.fillPoly(mask.copy(), [points], (0, 255, 0)) 

        show_image = cv.addWeighted(src1=img, alpha=0.8, src2=mask3, beta=0.2, gamma=0)

        #cv.imshow("mask", mask2)
        #cv.imshow("show_img", show_image)

        ROI = cv.bitwise_and(mask2, img)
        #cv.imshow("ROI", ROI)
        #cv.waitKey(0)
        showImages([mask2, show_image, ROI], 3, ["mask", "show_img", "ROI"])

    if len(pts) > 0:
        
        cv.circle(img2, pts[-1], 3, (0, 0, 255), -1)

    if len(pts) > 1:
        for i in range(len(pts) - 1):
            cv.circle(img2, pts[i], 5, (0, 0, 255), -1)  
            cv.line(img=img2, pt1=pts[i], pt2=pts[i + 1], color=(255, 0, 0), thickness=2)

    cv.imshow('Select Polygonal ROI', img2)


def main():
    source_video = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\DSC_1080.MOV"
    source_photo = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\Imgs\\source_image.png"
    app = "C:\\Users\\kseni\\Github-repos\\odject-detector-python\\174ND810_10_02\\DSC_1076.MOV"
    #source_photo = cv.imread(source_photo)
    #findFilters(source_photo, size_decrease=3)
    #image = imageMatcher(source_photo, size_decrease=2, show=True)
    #CannyContours(source_photo, size_decrease=2, show=True)
    #videoMatcher(app)
    #templateMatching(source_image, template_image)
    
    #CannyContours(source_photo, 3, show=True, mask=msk)
    videoMatcher(source_video, canny=True, size_decrease=3 , choose_ROI=False)


if __name__=="__main__":
    main()




