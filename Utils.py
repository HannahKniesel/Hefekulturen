from PIL import Image, ImageOps
import numpy as np
import cv2
import matplotlib.pyplot as plt

from skimage.morphology import opening


# returns binary image 
def open_image(path):
    img = Image.open(path)
    img = ImageOps.grayscale(img)
    img = img.resize((3230, 2180))
    img_np = np.array(img)
    maximum = img_np.max()
    minimum = img_np.min()
    img_np = (((img_np - minimum) /(maximum - minimum))*255).astype(np.uint8)

    blur = cv2.GaussianBlur(img_np,(5,5),0)
    ret3,img_np = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_np = img_np/255

    element = np.ones((7,7))
    img_np = opening(img_np, element)
    return img_np

def compute_grid(plate, x_expected, y_expected, use_hard_grid, plot = False):
    plate_x = np.sum(plate, axis = 1)
    m = np.median(plate_x)
    plate_x = (plate_x > m).astype(np.uint8)

    xmins_idx = []
    j = 0
    for i in range(len(plate_x)-1): 
        if((plate_x[i] == 0) and (plate_x[i+1] == 1)):
            w = int((i-j)/2)
            xmins_idx.append(i-w)
        if((plate_x[i] == 1) and (plate_x[i+1] == 0)):
            j = i 

    if(plot):
        plt.figure(figsize=(10,4))
        plt.title("X direction")
        plt.plot(np.arange(plate_x.shape[0]), np.sum(plate, axis = 1))
        plt.plot(np.arange(plate_x.shape[0]),plate_x*1000)
        plt.scatter(xmins_idx, np.zeros((len(xmins_idx),)))
    if((len(xmins_idx) != (y_expected)) or use_hard_grid):
        if(use_hard_grid):
            print("WARNING:: Use hard grid in y direction")
            xmins_idx = np.arange(0,plate_x.shape[0], plate_x.shape[0]/(y_expected)).astype(np.int16).tolist()
        else:
            xmins_idx = remove_double_lines(xmins_idx)

            if(len(xmins_idx) != (y_expected)):
                print("WARNING:: Use hard grid in y direction")
                print(len(xmins_idx), y_expected)

                xmins_idx = np.arange(0,plate_x.shape[0], plate_x.shape[0]/(y_expected)).astype(np.int16).tolist()
        
    xmins_idx = xmins_idx[1:]


    plate_y = np.sum(plate, axis = 0)
    m = np.median(plate_y)
    plate_y = plate_y > m

    ymins_idx = []
    j = 0
    for i in range(1,len(plate_y)-1): 
        if((plate_y[i] == 0) and (plate_y[i+1] == 1)):
            w = int((i-j)/2)
            ymins_idx.append(i-w)
        if((plate_y[i] == 1) and (plate_y[i+1] == 0)):
            j = i 

    if(plot):
        plt.figure(figsize=(10,4))
        plt.title("Y direction")
        plt.plot(np.arange(plate_y.shape[0]), np.sum(plate, axis = 0))
        plt.plot(np.arange(plate_y.shape[0]),plate_y*1000)
        plt.scatter(ymins_idx, np.zeros((len(ymins_idx),)))

    if((len(ymins_idx) != (x_expected)) or use_hard_grid):
        if(use_hard_grid):
            print("WARNING:: Use hard grid in x direction")
            ymins_idx = np.arange(0,plate_y.shape[0], plate_y.shape[0]/(x_expected)).astype(np.int16).tolist()
        else: 
            ymins_idx = remove_double_lines(ymins_idx)

            if(len(ymins_idx) != (x_expected)):
                print("WARNING:: Use hard grid in x direction")
                print(len(ymins_idx), x_expected)
                ymins_idx = np.arange(0,plate_y.shape[0], plate_y.shape[0]/(x_expected)).astype(np.int16).tolist()
    ymins_idx = ymins_idx[1:]

    rgb_grid = get_rgbgrid(plate, xmins_idx, ymins_idx)
    sizes, x_start, x_end, y_start, y_end = compute_sizes(plate, xmins_idx, ymins_idx)
    return rgb_grid, sizes, x_start, x_end, y_start, y_end

    
def get_rgbgrid(plate, xmins_idx, ymins_idx):
    red = plate.copy()

    pixel_width = 5
    for i in range(red.shape[0]):
        if(i in xmins_idx):
            red[i-pixel_width:i+pixel_width,:] = 1

    for i in range(red.shape[1]):
        if(i in ymins_idx):
            red[:,i-pixel_width:i+pixel_width] = 1

    rgb_grid_img = np.stack((red,plate,plate), axis = -1)*255
    return rgb_grid_img


def remove_double_lines(indices):
    xmins_idx = np.array(indices)
    x_dist = xmins_idx[1:] - xmins_idx[:-1]
    percentile_75 = np.percentile(x_dist, 75)
    percentile_25 = np.percentile(x_dist, 25)
    iqr = percentile_75 - percentile_25
    min_outlier = percentile_25-1.5*iqr
    # min_outlier = 55

    i = 1
    # for i in range(1,len(xmins_idx)):
    while(i < len(xmins_idx)):
        d = xmins_idx[i] - xmins_idx[i-1]
        if(d<min_outlier):
            xmins_idx = np.delete(xmins_idx, i)
        i += 1    

    return xmins_idx.tolist()



def compute_sizes(plate, xmins_idx, ymins_idx):
    xmins_idx.insert(0,0)
    xmins_idx.append(plate.shape[0]+1)

    ymins_idx.insert(0,0)
    ymins_idx.append(plate.shape[1]+1)

    sizes = np.zeros((len(xmins_idx[:-1]), len(ymins_idx[1:])))
    x_start = np.zeros((len(xmins_idx[:-1]), len(ymins_idx[1:])))
    x_end = np.zeros((len(xmins_idx[:-1]), len(ymins_idx[1:])))
    y_start = np.zeros((len(xmins_idx[:-1]), len(ymins_idx[1:])))
    y_end = np.zeros((len(xmins_idx[:-1]), len(ymins_idx[1:])))

    for i,(ymin_start, ymin_end) in enumerate(zip(ymins_idx[:-1], ymins_idx[1:])):
        for j,(xmin_start, xmin_end) in enumerate(zip(xmins_idx[:-1], xmins_idx[1:])):
            patch = plate[xmin_start:xmin_end,ymin_start:ymin_end]
            sizes[j,i] = np.sum(patch) 
            x_start[j,i] = xmin_start
            x_end[j,i] = xmin_end
            y_start[j,i] = ymin_start
            y_end[j,i] = ymin_end
    return sizes, x_start, x_end, y_start, y_end

def find_valid_quadruples(experiment_sizes, reference_sizes, minimum_size):
    valid_quadruples = np.ones((experiment_sizes.shape[0],experiment_sizes.shape[1]))
    xs = np.arange(0,experiment_sizes.shape[0],2)
    ys = np.arange(0,experiment_sizes.shape[1],4)
    for x in xs: 
        for y in ys: 
            sizes = experiment_sizes[x:x+2, y:y+2]
            sizes = sizes.reshape(-1)
            sizes = [size for size in sizes if (size >= minimum_size) ]
            if(len(sizes)<=3):
                valid_quadruples[x:x+2, y:y+4] = 0

            else:
                sizes = reference_sizes[x:x+2, y:y+2]
                sizes = sizes.reshape(-1)
                sizes = [size for size in sizes if (size >= minimum_size) ]
                if(len(sizes)<=3):
                    valid_quadruples[x:x+2, y:y+4] = 0

    xs = np.arange(0,experiment_sizes.shape[0],2)
    ys = np.arange(2,experiment_sizes.shape[1],4)
    for x in xs: 
        for y in ys: 
            sizes = experiment_sizes[x:x+2, y:y+2]
            sizes = sizes.reshape(-1)
            sizes = [size for size in sizes if (size >= minimum_size) ]
            if(len(sizes)<=3):
                valid_quadruples[x:x+2, y:y-4] = 0

            else:
                sizes = reference_sizes[x:x+2, y:y+2]
                sizes = sizes.reshape(-1)
                sizes = [size for size in sizes if (size >= minimum_size) ]
                if(len(sizes)<=3):
                    valid_quadruples[x:x+2, y:y-4] = 0


    return valid_quadruples 


def combined_highlights(highlights_absolute, highlights):
    highlights_both = np.zeros_like(highlights_absolute)
    highlights_both[(highlights[:,:,1] > 0 ) & (highlights_absolute[:,:,1]>0),1] = 255
    highlights_both[:,:,0] = highlights[:,:,0]
    return highlights_both
    