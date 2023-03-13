from PIL import Image, ImageOps
import numpy as np
from sklearn.cluster import KMeans
from tqdm import tqdm
import cv2


# returns binary image 
def open_image(path):
    img = Image.open(path)
    img = ImageOps.grayscale(img)
    img = img.resize((3230, 2180))
    img_np = np.array(img)
    maximum = img_np.max()
    minimum = img_np.min()
    img_np = (img_np - minimum) /(maximum - minimum)
    # init_shape = img_np.shape
    kmeans = KMeans(n_clusters=2, random_state=0).fit(img_np.reshape(-1,1))
    kmeans_t = np.mean(kmeans.cluster_centers_)
    img_np = (img_np>kmeans_t).astype(np.int32)
    return img_np


# find local minima in data
def find_minima(data):
    indices = []
    i = 0
    # pbar = tqdm(total = len(data))
    while(i < len(data)):
        x = data[i]
        if(i == 0):
            left_neighbor = 0
            right_neighbor = data[i+1]
        elif(i == (len(data)-1)):
            left_neighbor = data[i-1]
            right_neighbor = 0
        else:
            left_neighbor = data[i-1]
            right_neighbor = data[i+1]

        # if plateau
        if((left_neighbor > x) and (right_neighbor == x)):
            num_similars = 0
            init_i = i
            while((right_neighbor == x) and ((i+1) < (len(data)-1))):
                i += 1
                # pbar.update(1)
                right_neighbor = data[i+1]
                num_similars+=1
            if(right_neighbor > x):
                indices.append(init_i + (num_similars//2))
        # if minimum
        elif((right_neighbor > x) and (left_neighbor > x)):
            indices.append(i)

        i += 1
        # pbar.update(1)

    # pbar.close()
    return indices

def compute_grid(plate, erosion_iterations = 4):
    kernel = np.ones((5, 5), np.uint8)
    erosion_reference_plate = np.stack((plate,plate,plate), axis = -1)*255
    erosion_reference_plate = cv2.erode((erosion_reference_plate).astype(np.uint8), kernel, iterations=erosion_iterations)
    erosion_reference_plate = np.array(erosion_reference_plate)
    erosion_reference_plate = erosion_reference_plate[:,:,0]
    
    #find local minima
    yaxis = np.max(erosion_reference_plate, axis = 0)
    xaxis = np.max(erosion_reference_plate, axis = 1)
    xmins_idx = find_minima(xaxis)
    ymins_idx = find_minima(yaxis)

    red = plate.copy()

    pixel_width = 5
    for i in range(red.shape[0]):
        if(i in xmins_idx):
            red[i-pixel_width:i+pixel_width,:] = 1

    for i in range(red.shape[1]):
        if(i in ymins_idx):
            red[:,i-pixel_width:i+pixel_width] = 1

    rgb_grid_img = np.stack((red,plate,plate), axis = -1)*255
    return rgb_grid_img, xmins_idx, ymins_idx


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
    