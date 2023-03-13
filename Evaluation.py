
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from Utils import *
from Classes import *

rows = np.array(["1","2","3","4","5","6","7","8","9","10"])
cols = np.array(["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"])

def evaluate(experiment_plate, reference_plate, sizes_experiment, sizes_reference, x_start, x_end, y_start, y_end, MIN_COLONY_SIZE, P_VALUE_NULLHYPOTHESIS, log_dir):
    quadruples = generate_quadruples(sizes_experiment, sizes_reference, x_start, x_end, y_start, y_end, MIN_COLONY_SIZE)
    highlights, quadruples = significant_difference(experiment_plate, quadruples, P_VALUE_NULLHYPOTHESIS)
    highlights_absolute, quadruples = absolute_sizes(sizes_reference, sizes_experiment, quadruples, experiment_plate)
    highlights_both = combine(highlights,highlights_absolute)
    visualize(highlights, highlights_absolute, highlights_both,  sizes_experiment, sizes_reference, experiment_plate, reference_plate, quadruples, P_VALUE_NULLHYPOTHESIS, log_dir)
    return quadruples

def generate_quadruples(sizes_experiment, sizes_reference, x_start, x_end, y_start, y_end, MIN_COLONY_SIZE):
    p_values = np.zeros((sizes_experiment.shape[0]//4, sizes_experiment.shape[1]//2)) -1
    quadruples = []

    pos_x = 0
    pos_y = 0

    for i in range(0,sizes_experiment.shape[0],4):
        for j in range(0,sizes_experiment.shape[1],2):       
            sizesA_exp = sizes_experiment[i:i+2, j:j+2].reshape(-1)
            sizesB_exp = sizes_experiment[i+2:i+4, j:j+2].reshape(-1)

            sizesA_ref = sizes_reference[i:i+2, j:j+2].reshape(-1)
            sizesB_ref = sizes_reference[i+2:i+4, j:j+2].reshape(-1)
            
            x_px_s = int(x_start[i,j])
            x_px_e = int(x_end[i+3,j])
            y_px_s = int(y_start[i,j])
            y_px_e = int(y_end[i,j+1])

            ab_quadrupel = ABQuadrupel(sizesA_exp, sizesB_exp, sizesA_ref, sizesB_ref, x_px_s, x_px_e, y_px_s, y_px_e, [rows[pos_x],cols[pos_y]], name="", minimum_size=MIN_COLONY_SIZE)
            quadruples.append(ab_quadrupel)

            if(ab_quadrupel.is_valid):
                p_values[pos_x,pos_y] = ab_quadrupel.p_value
            pos_y +=1
            pos_y = pos_y % (sizes_experiment.shape[1]//2)
        pos_x +=1
        pos_x = pos_x % (sizes_experiment.shape[0]//4)
    return quadruples

def significant_difference(experiment_plate, quadruples, P_VALUE_NULLHYPOTHESIS):
    highlights = np.zeros_like(experiment_plate)
    highlights = np.stack((highlights,highlights,highlights), axis = -1)

    for quad in quadruples: 
        if(quad.is_valid and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            scaled_p_value = quad.p_value/P_VALUE_NULLHYPOTHESIS
            highlights[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, 1] = (1-scaled_p_value)*255
        if(quad.is_valid == False):
            highlights[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, 0] = 255
    return highlights, quadruples

def absolute_sizes(sizes_reference, sizes_experiment, quadruples, experiment_plate):
    median_size_reference = np.median(sizes_experiment)
    for quad in quadruples:
        if((np.all(quad.quadrupelA.sizes_exp>median_size_reference)) or (np.all(quad.quadrupelB.sizes_exp > median_size_reference))):
            quad.bigger_than_median = True


    highlights_absolute = np.zeros_like(experiment_plate)
    highlights_absolute = np.stack((highlights_absolute,highlights_absolute,highlights_absolute), axis = -1)

    for quad in quadruples: 
        if(quad.is_valid and (quad.bigger_than_median)):
            highlights_absolute[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, 1] = 255
        if(quad.is_valid == False):
            highlights_absolute[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, 0] = 255
    return highlights_absolute, quadruples

def combine(highlights,highlights_absolute): 
    highlights_both = np.zeros_like(highlights_absolute)
    highlights_both[(highlights[:,:,1] > 0 ) & (highlights_absolute[:,:,1]>0),1] = 255
    highlights_both[:,:,0] = highlights[:,:,0]
    return highlights_both



def visualize(highlights, highlights_absolute, highlights_both,  sizes_experiment, sizes_reference, experiment_plate, reference_plate, quadruples, P_VALUE_NULLHYPOTHESIS, log_dir):
    tick_distance_y = highlights.shape[0] / ((sizes_experiment.shape[0]//4))
    tick_distance_x = highlights.shape[1] / ((sizes_experiment.shape[1]//2))
    num_y, num_x = sizes_experiment.shape
    num_x = num_x//2
    num_y = num_y//4


    fig, axs = plt.subplots(3,4, figsize=(7*4,7*2))
    axs[0,0].set_title("Reference plate")
    axs[0,0].imshow(highlights, alpha=1.0)
    axs[0,0].imshow(reference_plate, cmap="gray",alpha=0.5)
    axs[0,0].set_ylabel("Significant differences\nin size between A and B")
    axs[0,1].set_title("Experiment plate")
    axs[0,1].imshow(highlights, alpha=1.0)
    axs[0,1].imshow(experiment_plate, cmap="gray", alpha=0.5)
    axs[0,2].set_title("Normalized experiment plate")
    axs[0,2].imshow(sizes_experiment/sizes_reference)
    axs[0,3].set_title("Green - significant difference in sizes\nRed - invalid experiment")
    axs[0,3].imshow(highlights, alpha=0.5)
    axs[0,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[0,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[0,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[0,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[0,2].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[0,2].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[0,3].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[0,3].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines


    axs[1,0].set_ylabel("Sizes > median size of plate")
    axs[1,0].set_title("Reference plate")
    axs[1,0].imshow(highlights_absolute, alpha=1.0)
    axs[1,0].imshow(reference_plate, cmap="gray",alpha=0.5)
    axs[1,1].set_title("Experiment plate")
    axs[1,1].imshow(highlights_absolute, alpha=1.0)
    axs[1,1].imshow(experiment_plate, cmap="gray", alpha=0.5)
    axs[1,2].set_title("Normalized experiment plate")
    axs[1,2].imshow(sizes_experiment/sizes_reference)
    axs[1,3].set_title("Green - significant difference in sizes\nRed - invalid experiment")
    axs[1,3].imshow(highlights_absolute, alpha=0.5)
    axs[1,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[1,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[1,2].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[1,2].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[1,3].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,3].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines

    axs[2,0].set_ylabel("Combination")
    axs[2,0].set_title("Reference plate")
    axs[2,0].imshow(highlights_both, alpha=1.0)
    axs[2,0].imshow(reference_plate, cmap="gray",alpha=0.5)
    axs[2,1].set_title("Experiment plate")
    axs[2,1].imshow(highlights_both, alpha=1.0)
    axs[2,1].imshow(experiment_plate, cmap="gray", alpha=0.5)
    axs[2,2].set_title("Normalized experiment plate")
    axs[2,2].imshow(sizes_experiment/sizes_reference)
    axs[2,3].set_title("Green - significant difference in sizes\nRed - invalid experiment")
    axs[2,3].imshow(highlights_both, alpha=0.5)
    axs[2,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[2,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[2,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[2,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[2,2].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[2,2].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    axs[2,3].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[2,3].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines


    for quad in quadruples:
        if(quad.is_valid and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y-.1, x-.1),w, h, linewidth=1.5, edgecolor='g', facecolor='none')
            axs[0,2].add_patch(rect)
        if(quad.is_valid == False):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y, x),w, h, linewidth=1.5, edgecolor='r', facecolor='none')
            axs[0,2].add_patch(rect)

        if(quad.is_valid and (quad.bigger_than_median)):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y-.1, x-.1),w, h, linewidth=1.5, edgecolor='g', facecolor='none')
            axs[1,2].add_patch(rect)
        if(quad.is_valid == False):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y, x),w, h, linewidth=1.5, edgecolor='r', facecolor='none')
            axs[1,2].add_patch(rect)

        if(quad.is_valid and (quad.bigger_than_median) and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y-.1, x-.1),w, h, linewidth=1.5, edgecolor='g', facecolor='none')
            axs[2,2].add_patch(rect)
        if(quad.is_valid == False):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y, x),w, h, linewidth=1.5, edgecolor='r', facecolor='none')
            axs[2,2].add_patch(rect)
    plt.savefig(log_dir, dpi = 300)
    plt.show()


