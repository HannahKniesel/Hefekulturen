# Documentation of the Results Table

- **Position** marks the position of the quadruple A and B, so they can be found more easily on the generated PDF with experiment and reference plates. 
- **Name** is retrieved by the layout of the experiment which is defined by the plate name (differences between plates A,B,C)
- **Exp1: Significant Size** if 'yes', the result of Exp1, considering the abolute growth compared to other colonies is considered significant.
- **Exp1: Absolut Size** is the mean normalized size of all colonies in the quadruple which has grown bigger. 
- **Exp1: Minimum Threshold** is the threshold to define the absolute growth of quadruple A and B compared to others. The threshold is (usually) derived by a outlier detection, taking 1.5xIQR into account. Works with normalized sizes. IT compares the mean of the row which has been grown bigger (normalized).
- **Exp2: Significant Difference** if 'yes', the result of Exp1, considering the difference in growth between row A and B is considered significant.
- **Exp2: P-value** is the result of the statistical test to derive wheather quadruple A has been grown significantly different from row B. 
- **Exp2: Effect Size** defines the effect size of the statistical test (high effect size means more significant difference).
- **Exp2: Growth Factor** defines the factor x such that $mean(B_{norm}) \times x = mean(A_{norm})$, which means that $B$ has $x$ times the size of $A$. If $x$ is $< 1$, row A is bigger, if $x > 1$ B is bigger.
- **Is Valid** is marked as invalid, if it is likely that there is a measuring error
- **Reason** defines the reason if the quadriple was marked as invalid
- **Bigger Row** defines weather row A or B was growing bigger
- **A1 Normalized** defines the normalized size of the first colony in quadruple A
- **A2 Normalized** defines the normalized size of the second colony in quadruple A 
- **A3 Normalized** defines the normalized size of the third colony in quadruple A 
- **A4 Normalized** defines the normalized size of the fourth colony in quadruple A 
- **B1 Normalized** defines the normalized size of the first colony in quadruple B
- **B2 Normalized** defines the normalized size of the second colony in quadruple B 
- **B3 Normalized** defines the normalized size of the third colony in quadruple B
- **B4 Normalized** defines the normalized size of the fourth colony in quadruple B 

- **A1 Raw Experiment** defines the raw size of the first colony in quadruple A on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **A2 Raw Experiment** defines the raw size of the second colony in quadruple A on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **A3 Raw Experiment** defines the raw size of the third colony in quadruple A on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **A4 Raw Experiment** defines the raw size of the fourth colony in quadruple A on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B1 Raw Experiment** defines the raw size of the first colony in quadruple B on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B2 Raw Experiment** defines the raw size of the second colony in quadruple B on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B3 Raw Experiment** defines the raw size of the third colony in quadruple B on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B4 Raw Experiment** defines the raw size of the fourth colony in quadruple B on the experiment plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.

- **A1 Raw Reference** defines the raw size of the first colony in quadruple A on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **A2 Raw Reference** defines the raw size of the second colony in quadruple A on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **A3 Raw Reference** defines the raw size of the third colony in quadruple A on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **A4 Raw Reference** defines the raw size of the fourth colony in quadruple A on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B1 Raw Reference** defines the raw size of the first colony in quadruple B on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B2 Raw Reference** defines the raw size of the second colony in quadruple B on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B3 Raw Reference** defines the raw size of the third colony in quadruple B on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.
- **B4 Raw Reference** defines the raw size of the fourth colony in quadruple B on the reference plate. Will be -1, if smaller than `MIN_COLONY_SIZE`.


# Sorting
The results table is sorted in such way, that experiments that are significant in both Exp1 and Exp2 are at the very top. 
It follows experiments, that are significant in difference between row A and B (Exp2)
It follows experiments, that are significant in absolut growth (Exp1)
Next, there are entities which are neither significant in Exp1 nor Exp2. 
Finally, invalids are shown at the bottom.
