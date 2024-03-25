from scipy.stats import ttest_ind, levene, shapiro, wilcoxon, ttest_rel, mannwhitneyu
import numpy as np

class Quadrupel():
    def __init__(self, sizes_exp, sizes_ref, minimum_size):
        self.sizes_exp = [size for size in sizes_exp if (size >= minimum_size) ]
        self.sizes_ref = [size for size in sizes_ref if (size >= minimum_size) ]

        if((len(self.sizes_exp)<4) or (len(self.sizes_ref)<4)):
            self.is_valid = False
        else:
            self.is_valid = True
        self.sizes = np.array(sizes_exp/(sizes_ref+1e-10))

        self.mean_growth = np.mean(self.sizes)

class ABQuadrupel():
    def __init__(self, sizesA_exp, sizesB_exp, sizesA_ref, sizesB_ref, x_px_s, x_px_e, y_px_s, y_px_e, position, name, minimum_size):
        self.position = position
        self.name = name
        
        # compute differences on all pairs
        differences = np.subtract.outer(sizesA_ref, sizesB_ref).reshape(-1) #(sizesA_ref - sizesB_ref)
        # use mean instead of median, as it is sensitive to outliers, which means we also exclude values where there is a high std in the measurements. 
        self.ref_rsd = np.sqrt(np.mean(differences**2)) # np.mean(np.abs(sizesA_ref-sizesB_ref))#
        self.x_px_s = x_px_s
        self.x_px_e = x_px_e
        self.y_px_s = y_px_s
        self.y_px_e = y_px_e
        self.quadrupelA = Quadrupel(sizesA_exp, sizesA_ref, minimum_size)
        self.quadrupelB = Quadrupel(sizesB_exp, sizesB_ref, minimum_size)

        self.reason = ""
        if(self.quadrupelA.is_valid and self.quadrupelB.is_valid):
            self.is_valid = True
            
        else:
            self.is_valid = False
            self.reason = "Missing values in quadrupel."
            print(f"WARNING::Exclude {self.name} at position {self.position} from evaluation. Found inaccuracy on reference plate: Missing values in quadrupel.")
        
        
        if(self.is_valid):
            # test for normality 
            stat, p_shapiroA = shapiro(self.quadrupelA.sizes)
            stat, p_shapiroB = shapiro(self.quadrupelB.sizes)

            # test for equal variances
            stat, p_levene = levene(self.quadrupelA.sizes, self.quadrupelB.sizes)
            
            # when variances are not equal, experiment is not useable?
            if(p_levene < 0.01):
                self.statistic, self.p_value = np.inf, np.inf

            elif(np.any(np.array([p_shapiroA, p_shapiroB])<0.01)):
                # normalverteilung kann nicht angenommen werden 
                # print("Use wilcox: Shapiro A = "+str(p_shapiroA)+ " | Shapiro B = "+str(p_shapiroB) + " | Levenes = "+str(p_levene))
                self.statistic, self.p_value = wilcoxon(self.quadrupelA.sizes, self.quadrupelB.sizes)
                # self.statistic, self.p_value = mannwhitneyu(self.quadrupelA.sizes, self.quadrupelB.sizes)
            else: 
                # print("Use ttest")
                self.statistic, self.p_value = ttest_rel(self.quadrupelA.sizes, self.quadrupelB.sizes)
                # self.statistic, self.p_value = ttest_ind(self.quadrupelA.sizes, self.quadrupelB.sizes, equal_var=True)

        else: 
            self.statistic, self.p_value = np.inf, np.inf

        if(not self.p_value == np.inf):
            means = (np.mean(self.quadrupelA.sizes) - np.mean(self.quadrupelB.sizes))
            stds = np.sqrt(((np.std(self.quadrupelA.sizes) ** 2) + (np.std(self.quadrupelB.sizes) ** 2))/2)
            self.effect_size = np.abs(means/stds) 
        else: 
            self.effect_size = 0

        # print("Equal variances: "+str(p)+" are "+str((p>0.01)))
        # find significance in difference
        # self.statistic, self.p_value = ttest_ind(self.quadrupelA.sizes, self.quadrupelB.sizes, equal_var=True)
        # self.statistic, self.p_value = mannwhitneyu(self.quadrupelA.sizes, self.quadrupelB.sizes)


        self.bigger_than_median = False
        max_idx = np.argmax((self.quadrupelA.mean_growth, self.quadrupelB.mean_growth))
        min_idx = np.argmin((self.quadrupelA.mean_growth, self.quadrupelB.mean_growth))

        self.bigger_row = ["A","B"][max_idx]
        self.max_mean_growth = [self.quadrupelA.mean_growth, self.quadrupelB.mean_growth][max_idx]
        self.min_mean_growth = [self.quadrupelA.mean_growth, self.quadrupelB.mean_growth][min_idx]
        self.diff_growth = np.abs(self.max_mean_growth - self.min_mean_growth)

        self.ordinal_scale = -1
        self.size_position = -1
        self.p_position = -1

        self.absolute_size = np.max((np.min(self.quadrupelA.sizes), np.min(self.quadrupelB.sizes)))


            

        

        
