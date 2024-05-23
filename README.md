# Hefekulturen

![Qualitative Results](./Documentation/assets/qualitative-results.png)

This code is designed to evaluate the growth of yeast colonies. 
It combines an evaluation of the overall growth of a quadruple as well as the difference in growth between row A and B. 

**Exp1** evaluates the growth of the smallest normalized colony within the bigger quadruple. If it is an outlier defined by $1.5 \times IQR$, it is marked as significant. All other quadruples on the plates are taken as a reference. 

**Exp2** evaluates the significant difference of quadruple in row A with quadruple in row B. This is done by the use of statistical tests (like t-test). We assume significance, if the p-value is smaller than 0.01. 


Finally, the intersection of both experiments is considered. 

Green marks significant outcomes of the experiments. Red marks invalid quadruples, which can be due to multiple reasons. For details please see `./Documentation/`



# TODO more detailed description from biologists?! 



