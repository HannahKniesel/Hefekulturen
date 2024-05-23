
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from outliers import smirnov_grubbs as grubbs

from Utils import *
from Classes import *

color_invalid = [255,0,0,180]
heatmap = [[45, 234, 64, 255], [59, 191, 79, 255], [79, 156, 108, 255], [76, 118, 92, 255], [73, 91, 80, 255]]

rows = np.array(["1","2","3","4","5","6","7","8","9","10"])
cols = np.array(["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"])

def evaluate(experiment_plate, reference_plate, sizes_experiment, sizes_reference, x_start, x_end, y_start, y_end, layout_names, MIN_COLONY_SIZE, P_VALUE_NULLHYPOTHESIS, log_dir):
    quadruples = generate_quadruples(sizes_experiment, sizes_reference, x_start, x_end, y_start, y_end, layout_names, MIN_COLONY_SIZE)
    # quadruples = remove_outliers(quadruples)
    quadruples = check_reference_plate(quadruples)
    highlights, quadruples = significant_difference(experiment_plate, quadruples, P_VALUE_NULLHYPOTHESIS)
    highlights_absolute, quadruples, minimum_size = absolute_sizes(sizes_reference, sizes_experiment, quadruples, experiment_plate)
    highlights_both = combine(highlights,highlights_absolute)
    visualize(highlights, highlights_absolute, highlights_both,  sizes_experiment, sizes_reference, experiment_plate, reference_plate, quadruples, P_VALUE_NULLHYPOTHESIS, log_dir)
    # quadruples = compute_ordinal_scale(quadruples, P_VALUE_NULLHYPOTHESIS)
    quadruples = sort_quadruples(quadruples, P_VALUE_NULLHYPOTHESIS, minimum_size)
    return quadruples, minimum_size

def sort_quadruples(quadruples, P_VALUE_NULLHYPOTHESIS, minimum_size):
    curr_idx = 0 
    sorted_quadruples = []
    # sort all that are significant in exp 1 and 2 
    sorted_quadruples += [quad for quad in quadruples if ((quad.p_value<P_VALUE_NULLHYPOTHESIS) and (quad.absolute_size>minimum_size) and quad.is_valid)]
    sorted_quadruples = sorted(sorted_quadruples, key = lambda x: x.effect_size, reverse=True)
    curr_idx = len(sorted_quadruples)

    # sort all that are significant in exp 2
    sorted_quadruples += [quad for quad in quadruples if ((quad.p_value<P_VALUE_NULLHYPOTHESIS) and (quad.absolute_size<minimum_size) and quad.is_valid)]
    sorted_quadruples[curr_idx:] = sorted(sorted_quadruples[curr_idx:], key = lambda x: x.effect_size, reverse=True)
    curr_idx = len(sorted_quadruples)

    # sort all that are significant in exp 1
    sorted_quadruples += [quad for quad in quadruples if ((quad.p_value>P_VALUE_NULLHYPOTHESIS) and (quad.absolute_size>minimum_size) and quad.is_valid)]
    sorted_quadruples[curr_idx:] = sorted(sorted_quadruples[curr_idx:], key = lambda x: x.absolute_size, reverse=True)
    curr_idx = len(sorted_quadruples)

    # add all that are not significant in both 
    sorted_quadruples += [quad for quad in quadruples if ((not quad in sorted_quadruples) and quad.is_valid)]

    # add remaining
    sorted_quadruples += [quad for quad in quadruples if (not quad in sorted_quadruples)]

    return sorted_quadruples

# checks if there might be errors on the reference plate, and if so remove those from evaluation
def check_reference_plate(quadruples):
    rows_mean_diff = {}

    for quad in quadruples:
        if(quad.is_valid):
            row = quad.position[0]
            try: 
                rows_mean_diff[row].append(quad.ref_rsd) # use root squared difference to get rid of negative values
            except:
                rows_mean_diff[row] = [quad.ref_rsd]

    #### OUTLIER BASED ON GRUBBS TEST ####
    for row in rows_mean_diff.keys(): 
        values = rows_mean_diff[row]
        remaining_values = grubbs.test(values, alpha=.05)
        rows_mean_diff[row] = remaining_values


    for quad in quadruples: 
        if(quad.is_valid):
            row = quad.position[0]
            remaining_values = rows_mean_diff[row]
            if(not(quad.ref_rsd in remaining_values)):
                quad.is_valid = False
                quad.reason = "Inaccuracy on reference plate. Reliable normalization not possible as difference in row A to B differs from others in same row."
                print(f"WARNING::Exclude {quad.name} at position {quad.position} from evaluation. Found inaccuracy on reference plate: Reliable normalization not possible as difference in row A to B differs from others in same row.")
    
        


    #### OUTLIER BASED ON IQR ####
    # compute interquantile (range) for outlier detection
    """for row in rows_mean_diff.keys(): 
        values = rows_mean_diff[row]
        q75, q25 = np.percentile(values, [75 ,25])
        iqr = q75 - q25

        irange = 1.5
        minimum = q25 - (irange*iqr)
        maximum = q75 + (irange*iqr)
        rows_mean_diff[row] = (maximum,minimum)
    print(f"Collected row means = {rows_mean_diff}")

    for quad in quadruples: 
        rsd = quad.ref_rsd
        row = quad.position[0]
        maximum,minimum = rows_mean_diff[row]
        if((rsd < minimum) or (rsd > maximum)): 
            quad.is_valid = False
            quad.reason = "Inaccuracy on reference plate. Reliable normalization not possible as difference in row A to B differs from others in same row."
            print(f"WARNING::Exclude {quad.name} at position {quad.position} from evaluation. Found inaccuracy on reference plate: Reliable normalization not possible as difference in row A to B differs from others in same row.")
    """
    
    return quadruples

# only removes really hard outliers 
def remove_outliers(quadruples):
    sizes = []
    for quad in quadruples: 
        sizes.extend(quad.quadrupelA.sizes)
        sizes.extend(quad.quadrupelB.sizes)

    percentile_75 = np.percentile(sizes, 75)
    percentile_25 = np.percentile(sizes, 25)
    iqr = percentile_75 - percentile_25
    max_outlier = percentile_75+100*iqr
    min_outlier = percentile_25-100*iqr

    for quad in quadruples: 
        if((np.any(quad.quadrupelA.sizes<min_outlier))): 
            quad.is_valid = False
            quad.sizes = [0,0,0,0]
            print("INFO::remove outlier = "+str(quad.quadrupelA.sizes)+ " smaller than "+str(min_outlier))
        elif((np.any(quad.quadrupelB.sizes<min_outlier))):
            quad.is_valid = False
            quad.sizes = [0,0,0,0]
            print("INFO::remove outlier = "+str(quad.quadrupelB.sizes)+ " smaller than "+str(min_outlier))
        elif((np.any(quad.quadrupelA.sizes>max_outlier))):
            quad.is_valid = False
            quad.sizes = [0,0,0,0]
            print("INFO::remove outlier = "+str(quad.quadrupelA.sizes)+ " bigger than "+str(max_outlier))
        elif((np.any(quad.quadrupelB.sizes>max_outlier))):
            quad.is_valid = False
            quad.sizes = [0,0,0,0]
            print("INFO::remove outlier = "+str(quad.quadrupelB.sizes)+ " bigger than "+str(max_outlier))
    return quadruples


def generate_quadruples(sizes_experiment, sizes_reference, x_start, x_end, y_start, y_end, layout_names, MIN_COLONY_SIZE):
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

            name = layout_names[rows[pos_x]+cols[pos_y]]

            ab_quadrupel = ABQuadrupel(sizesA_exp, sizesB_exp, sizesA_ref, sizesB_ref, x_px_s, x_px_e, y_px_s, y_px_e, [rows[pos_x],cols[pos_y]], name=name, minimum_size=MIN_COLONY_SIZE)
            quadruples.append(ab_quadrupel)

            if(ab_quadrupel.is_valid):
                p_values[pos_x,pos_y] = ab_quadrupel.p_value
            pos_y +=1
            pos_y = pos_y % (sizes_experiment.shape[1]//2)
        pos_x +=1
        pos_x = pos_x % (sizes_experiment.shape[0]//4)
    return quadruples

# visualization purposes
def significant_difference(experiment_plate, quadruples, P_VALUE_NULLHYPOTHESIS):
    highlights = np.zeros_like(experiment_plate)
    highlights = np.stack((highlights,highlights,highlights,highlights), axis = -1)

    effect_sizes = []
    for quad in quadruples:
        if(quad.is_valid and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            effect_sizes.append(quad.effect_size)

    # p2,p4,p6,p8 = np.percentile(effect_sizes, [20,40,60,80])
    e_small, e_medium, e_large = np.percentile(effect_sizes, [25,50,75]) # 0.2, 0.5, 0.8

    for quad in quadruples: 
        if(quad.is_valid and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            color = heatmap[4]
            if(quad.effect_size > e_small):
                color = heatmap[3]
            if(quad.effect_size > e_medium):
                color = heatmap[2]
            if(quad.effect_size > e_large):
                color = heatmap[1]
            highlights[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, :] = color
        if(quad.is_valid == False):
            highlights[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, :] = [255,0,0,180]
    return highlights.astype(np.uint8), quadruples

def absolute_sizes(sizes_reference, sizes_experiment, quadruples, experiment_plate):
    sizes = sizes_experiment/(sizes_reference+1e-10)
    percentile_75 = np.percentile(sizes, 75)
    percentile_25 = np.percentile(sizes, 25)
    iqr = percentile_75 - percentile_25
    max_outlier = percentile_75+1.5*iqr
    # min_outlier = percentile_25-1.5*iqr
    minimum_size = max_outlier

    absolute_sizes = []
    for quad in quadruples:
        if(quad.absolute_size>minimum_size): #(np.all(quad.quadrupelA.sizes>minimum_size)) or (np.all(quad.quadrupelB.sizes > minimum_size))):
            quad.bigger_than_median = True
            if(quad.is_valid):
                absolute_sizes.append(quad.absolute_size)
    
    e_small, e_medium, e_large = np.percentile(absolute_sizes, [25,50,75]) # 0.2, 0.5, 0.8

    highlights_absolute = np.zeros_like(experiment_plate)
    highlights_absolute = np.stack((highlights_absolute,highlights_absolute,highlights_absolute, highlights_absolute), axis = -1)

    for quad in quadruples: 
        if(quad.is_valid and (quad.bigger_than_median)):
            # highlights_absolute[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, 1] = 255
            color = heatmap[4]
            if(quad.absolute_size > e_small):
                color = heatmap[3]
            if(quad.absolute_size > e_medium):
                color = heatmap[2]
            if(quad.absolute_size > e_large):
                color = heatmap[1]
            highlights_absolute[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, :] = color

        if(quad.is_valid == False):
            highlights_absolute[quad.x_px_s:quad.x_px_e, quad.y_px_s:quad.y_px_e, :] = color_invalid
    return highlights_absolute.astype(np.uint8), quadruples, minimum_size

def combine(highlights,highlights_absolute): 
    highlights_both = np.zeros_like(highlights_absolute)
    highlights_both[(highlights[:,:,1] > 0 ) & (highlights_absolute[:,:,1]>0)] = highlights[(highlights[:,:,1] > 0 ) & (highlights_absolute[:,:,1]>0)]
    highlights_both[(highlights[:,:,0] == 255 ) & (highlights_absolute[:,:,0]==255)] = color_invalid
    # highlights_both[:,:,0] = highlights[:,:,0]
    return highlights_both.astype(np.uint8)



def visualize(highlights, highlights_absolute, highlights_both,  sizes_experiment, sizes_reference, experiment_plate, reference_plate, quadruples, P_VALUE_NULLHYPOTHESIS, log_dir):
    tick_distance_y = highlights.shape[0] / ((sizes_experiment.shape[0]//4))
    tick_distance_x = highlights.shape[1] / ((sizes_experiment.shape[1]//2))
    num_y, num_x = sizes_experiment.shape
    num_x = num_x//2
    num_y = num_y//4

    normalized_plate = sizes_experiment/(sizes_reference+1e-10)
    percentile_75 = np.percentile(normalized_plate, 75)
    percentile_25 = np.percentile(normalized_plate, 25)
    iqr = percentile_75 - percentile_25
    max_outlier = percentile_75+50*iqr
    min_outlier = percentile_25-50*iqr

    # print(highlights)
    # print(highlights.shape)
    normalized_plate[normalized_plate>max_outlier] = 0
    normalized_plate[normalized_plate<min_outlier] = 0
    # normalized_plate[highlights[:,:,0]==255] = 0

    for quad in quadruples:
        if(not quad.is_valid):
            y = np.argwhere(cols == quad.position[1])
            x =  np.argwhere(rows == quad.position[0])
            normalized_plate[int(x*4):int(x*4+4),int(y*2):int(y*2+2)] = 0
    s = 7
    fig, axs = plt.subplots(2, 3, figsize=(s*3,s*2))
    plt.suptitle("Results")
    # spalte, zeile
    axs[0,0].set_title("Reference Plate")
    axs[0,0].imshow(reference_plate, cmap="gray",alpha=1.0)
    axs[0,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[0,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    

    axs[0,1].set_title("Experiment Plate")
    axs[0,1].imshow(experiment_plate, cmap="gray", alpha=1.0)
    axs[0,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[0,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    

    axs[0,2].set_title("Normalized Experiment Plate")
    axs[0,2].imshow(normalized_plate)
    axs[0,2].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[0,2].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) 

    axs[1,0].set_title("Exp1: Absolute Growth\nExperiment Plate")
    axs[1,0].imshow(experiment_plate, cmap="gray", alpha=1.0)
    axs[1,0].imshow(highlights_absolute, alpha=0.7)
    axs[1,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[1,1].set_title("Exp2: Differences\nExperiment Plate")
    axs[1,1].imshow(experiment_plate, cmap="gray", alpha=1.0)
    axs[1,1].imshow(highlights, alpha=0.7)
    axs[1,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[1,2].set_title("Exp1 + Exp2\nExperiment Plate")
    axs[1,2].imshow(experiment_plate, cmap="gray", alpha=1.0)
    axs[1,2].imshow(highlights_both, alpha=0.7)
    axs[1,2].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,2].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    

    """fig, axs = plt.subplots(3,4, figsize=(7*4,7*2))

    axs[0,0].set_ylabel("EXP1\nAbsolut Growth")
    
    axs[0,0].set_title("Reference Plate")
    axs[0,0].imshow(reference_plate, cmap="gray",alpha=1.0)
    axs[0,0].set_yticks([])
    axs[0,0].set_xticks([])

    axs[0,1].set_title("Experiment Plate")
    axs[0,1].imshow(experiment_plate, cmap="gray", alpha=1.0)
    axs[0,1].set_yticks([])
    axs[0,1].set_xticks([])

    axs[0,2].set_title("Results\nExperiment Plate")
    axs[0,2].imshow(experiment_plate, cmap="gray", alpha=1.0)
    axs[0,2].imshow(highlights_absolute, alpha=0.7)
    axs[0,2].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[0,2].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[0,3].set_title("Normalized Experiment Plate")
    axs[0,3].imshow(normalized_plate)
    axs[0,3].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[0,3].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    
    
    axs[1,0].set_ylabel("EXP2\nSignificant differences\n between A and B")
    axs[1,0].set_title("Reference Plate")
    axs[1,0].imshow(highlights, alpha=1.0)
    axs[1,0].imshow(reference_plate, cmap="gray",alpha=0.5)
    axs[1,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[1,1].set_title("Experiment plate")
    axs[1,1].imshow(highlights, alpha=1.0)
    axs[1,1].imshow(experiment_plate, cmap="gray", alpha=0.5)
    axs[1,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[1,2].set_title("Normalized experiment plate")
    axs[1,2].imshow(normalized_plate)
    axs[1,2].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[1,2].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[1,3].set_title("Green - significant difference in sizes\nRed - invalid experiment")
    axs[1,3].imshow(highlights, alpha=0.5)
    axs[1,3].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[1,3].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines


    
    axs[2,0].set_ylabel("EXP1 + EXP2\nCombination")
    axs[2,0].set_title("Reference plate")
    axs[2,0].imshow(highlights_both, alpha=1.0)
    axs[2,0].imshow(reference_plate, cmap="gray",alpha=0.5)
    axs[2,0].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[2,0].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[2,1].set_title("Experiment plate")
    axs[2,1].imshow(highlights_both, alpha=1.0)
    axs[2,1].imshow(experiment_plate, cmap="gray", alpha=0.5)
    axs[2,1].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[2,1].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines
    
    axs[2,2].set_title("Normalized experiment plate")
    axs[2,2].imshow(normalized_plate)
    axs[2,2].set_xticks(np.linspace(0.5, (num_x*2)-1, num=num_x), cols[:sizes_experiment.shape[1]//2])
    axs[2,2].set_yticks(np.linspace(1, (num_y*4)-2, num=num_y), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines

    axs[2,3].set_title("Green - significant difference in sizes\nRed - invalid experiment")
    axs[2,3].imshow(highlights_both, alpha=0.5)
    axs[2,3].set_xticks(np.linspace(tick_distance_x//2, highlights.shape[1]-(tick_distance_x//2), num=sizes_experiment.shape[1]//2), cols[:sizes_experiment.shape[1]//2])
    axs[2,3].set_yticks(np.linspace(tick_distance_y//2, highlights.shape[0]-(tick_distance_y//2), num=(sizes_experiment.shape[0]//4)), np.arange((sizes_experiment.shape[0]//4))+1) # TODO do by grid lines


    for quad in quadruples:
        if(quad.is_valid and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y-.1, x-.1),w, h, linewidth=1.5, edgecolor='g', facecolor='none')
            axs[0,3].add_patch(rect)
        if(quad.is_valid == False):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y, x),w, h, linewidth=1.5, edgecolor='r', facecolor='none')
            axs[0,3].add_patch(rect)

        if(quad.is_valid and (quad.bigger_than_median)):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y-.1, x-.1),w, h, linewidth=1.5, edgecolor='g', facecolor='none')
            axs[1,3].add_patch(rect)
        if(quad.is_valid == False):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y, x),w, h, linewidth=1.5, edgecolor='r', facecolor='none')
            axs[1,3].add_patch(rect)

        if(quad.is_valid and (quad.bigger_than_median) and (quad.p_value < P_VALUE_NULLHYPOTHESIS)):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y-.1, x-.1),w, h, linewidth=1.5, edgecolor='g', facecolor='none')
            axs[2,3].add_patch(rect)
        if(quad.is_valid == False):
            y = np.argwhere(cols == quad.position[1])*2-0.5
            x =  np.argwhere(rows == quad.position[0])*4 -0.5
            w = 2
            h = 4
            rect = patches.Rectangle((y, x),w, h, linewidth=1.5, edgecolor='r', facecolor='none')
            axs[2,3].add_patch(rect)"""
    plt.tight_layout()
    plt.savefig(log_dir, dpi = 300)
    plt.show()


def compute_ordinal_scale(quadruples, P_VALUE_NULLHYPOTHESIS):
    # Sort by effect size
    # The P values do not tell how 2 groups are different. The degree of difference is referred as ‘effect size’.
    quadruples = sorted(quadruples, key=lambda quad: quad.effect_size, reverse = False)
    for i,quad in enumerate(quadruples):
        quad.effectsize_position = i+1

    # Sort by maximum mean growth 
    quadruples = sorted(quadruples, key=lambda quad: quad.max_mean_growth)
    for i,quad in enumerate(quadruples):
        quad.size_position = i+1


    for quad in quadruples:
        if((not quad.is_valid) or (quad.p_value >= P_VALUE_NULLHYPOTHESIS) or (not quad.bigger_than_median)):
            quad.ordinal_scale =-1

        else:
            quad.ordinal_scale = quad.size_position + quad.effectsize_position 


    quadruples = sorted(quadruples, key=lambda quad: quad.ordinal_scale, reverse = True)
    return quadruples




