from scipy.stats import ttest_ind
import numpy as np

class Quadrupel():
    def __init__(self, sizes_exp, sizes_ref, minimum_size):
        self.sizes_exp = [size for size in sizes_exp if (size >= minimum_size) ]
        self.sizes_ref = [size for size in sizes_ref if (size >= minimum_size) ]

        if((len(self.sizes_exp)<4) or (len(self.sizes_ref)<4)):
            self.is_valid = False
        else:
            self.is_valid = True
        self.sizes = np.array(sizes_exp/sizes_ref)

class ABQuadrupel():
    def __init__(self, sizesA_exp, sizesB_exp, sizesA_ref, sizesB_ref, x_px_s, x_px_e, y_px_s, y_px_e, position, name, minimum_size):
        self.position = position
        self.name = name
        self.x_px_s = x_px_s
        self.x_px_e = x_px_e
        self.y_px_s = y_px_s
        self.y_px_e = y_px_e
        self.quadrupelA = Quadrupel(sizesA_exp, sizesA_ref, minimum_size)
        self.quadrupelB = Quadrupel(sizesB_exp, sizesB_ref, minimum_size)
        if(self.quadrupelA.is_valid and self.quadrupelB.is_valid):
            self.is_valid = True
            
        else:
            self.is_valid = False

        # find significance in difference
        self.statistic, self.p_value = ttest_ind(self.quadrupelA.sizes, self.quadrupelB.sizes, equal_var=False)

        self.bigger_than_median = False

            

        

        
