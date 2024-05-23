'''
Please only set `USE_HARD_GRID` to `True` if the grid (Section *2.2. Compute Colony Sizes*) is not working properly.
WARNING:: This can lead to inaccuracies at colony borders.
'''
USE_HARD_GRID = False 
if(USE_HARD_GRID):
    print("WARNING::Using hard grid. This can lead to inaccuracies at colony borders.")



''' 
`MIN_COLONY_SIZE` is used to exclude colonies that did not grow. 
The value is defined by the smallest 3% of all colonies computed over a set of experiment and reference plates. 
The value was set based on experience. Please only change if you know what you are doing. 
'''
MIN_COLONY_SIZE = 85.0 

'''
`P_VALUE_NULLHYPOTHESIS` is the considered p-value of the statistical tests used for finding significant differences between row A and B. 
Please only change if you know what you are doing. 
'''
P_VALUE_NULLHYPOTHESIS = 0.01
