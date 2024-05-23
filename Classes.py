from scipy.stats import ttest_ind, levene, shapiro, wilcoxon, ttest_rel, mannwhitneyu
import numpy as np

def cohend(d1, d2):
    # calculate the size of samples
    n1, n2 = len(d1), len(d2)
    # calculate the variance of the samples
    s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
    # calculate the pooled standard deviation
    s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    # calculate the means of the samples
    u1, u2 = np.mean(d1), np.mean(d2)
    # calculate the effect size
    return (u1 - u2) / s

class Quadrupel():
    def __init__(self, sizes_exp, sizes_ref, minimum_size):
        self.sizes_exp = [size if (size >= minimum_size) else -1 for size in sizes_exp]
        self.sizes_ref = [size if (size >= minimum_size) else -1 for size in sizes_ref]

        if((-1 in self.sizes_exp) or (-1 in self.sizes_ref)):
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
            print(f"WARNING::Exclude {self.name} at position {self.position} from evaluation. {self.reason}")

        
        # only apply statistical test when there are 4 samples.
        if(self.is_valid):
            # test for normality 
            stat, p_shapiroA = shapiro(self.quadrupelA.sizes)
            stat, p_shapiroB = shapiro(self.quadrupelB.sizes)

            # test for equal variances
            stat, p_levene = levene(self.quadrupelA.sizes, self.quadrupelB.sizes)
            
            # when variances are not equal, experiment is not useable?
            if(p_levene < 0.01):
                self.statistic, self.p_value = np.inf, np.inf
                self.effect_size = 0
                self.is_valid = False
                self.reason = "Variances of row A and B are not equal. A comparison is not recommended."
                print(f"WARNING::Exclude {self.name} at position {self.position} from evaluation. {self.reason}")


            elif(np.any(np.array([p_shapiroA, p_shapiroB])<0.01)):
                # normalverteilung kann nicht angenommen werden 
                self.is_valid = False
                self.reason = "Normality of the samples cannot be assumed. T-test is not applicable. We will apply wilcoxon test."
                self.statistic, self.p_value = wilcoxon(self.quadrupelA.sizes, self.quadrupelB.sizes)
                print(f"WARNING::Exclude {self.name} at position {self.position} from evaluation. {self.reason}")
                # Compute effect size (r)
                N = len(self.quadrupelA.sizes)
                self.effect_size = self.statistic / np.sqrt(N)

            else: 
                self.statistic, self.p_value = ttest_rel(self.quadrupelA.sizes, self.quadrupelB.sizes)

                


                # Compute effect size by Cohen's d
                self.effect_size = cohend(self.quadrupelA.sizes, self.quadrupelB.sizes)
                # Compute mean difference
                # mean_diff = np.mean(self.quadrupelA.sizes - self.quadrupelB.sizes)
                # # Compute standard deviation of the differences
                # sd_diff = np.std(self.quadrupelA.sizes - self.quadrupelB.sizes, ddof=1)  # ddof=1 for sample standard deviation
                # # Compute Cohen's d
                # self.effect_size = mean_diff / sd_diff

               

        else: 
            self.statistic, self.p_value = np.inf, np.inf
            self.effect_size = 0



        self.bigger_than_median = False
        max_idx = np.argmax((self.quadrupelA.mean_growth, self.quadrupelB.mean_growth))
        # min_idx = np.argmin((self.quadrupelA.mean_growth, self.quadrupelB.mean_growth))
        self.bigger_row = ["A","B"][max_idx]

        self.growthfactor = self.quadrupelA.mean_growth / (self.quadrupelB.mean_growth + 1e-10)
        # self.max_mean_growth = [self.quadrupelA.mean_growth, self.quadrupelB.mean_growth][max_idx]
        # self.min_mean_growth = [self.quadrupelA.mean_growth, self.quadrupelB.mean_growth][min_idx]
        # self.diff_growth = np.abs(self.max_mean_growth - self.min_mean_growth)

        # self.ordinal_scale = -1
        # self.size_position = -1
        # self.p_position = -1

        # mean growth of bigger quadruple, used for Exp1: growth of colonies in comparison to others on plate
        self.absolute_size = np.max((np.mean(self.quadrupelA.sizes), np.mean(self.quadrupelB.sizes))) #np.max((np.min(self.quadrupelA.sizes), np.min(self.quadrupelB.sizes)))


            

        

        
