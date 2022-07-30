# Comparison of Changepoint algorithms: https://arxiv.org/pdf/2003.06222.pdf
# PELT (Pruned Exact Linear Time) & basics (v useful): https://arxiv.org/pdf/1101.1438.pdf

# A) m changepts split the data into m+1 segments. We would like to minimize the NLL of the
# segments (in an optimal split - probab of each segment will be high)
# B) In order to not have every point as a changept, we add a penalty. This can be a linear
# penalty (km), AIC, BIC

install.packages(c("changepoint", "EnvCpt"))
library(changepoint)

set.seed(1)

# change in variance
x=c(rnorm(100,0,1),rnorm(100,0,10))
ansvar=cpt.var(x)
plot(ansvar)
print(ansvar)

# change in mean
y=c(rnorm(100,0,1),rnorm(100,5,1), rnorm(100,0,1))
ansmean=cpt.mean(y)
plot(ansmean,cpt.col='blue')

# ansmean=cpt.mean(y, penalty = "BIC")
ansmean=cpt.mean(y, penalty = "MBIC", method = "PELT") # AMOC, PELT (yes), SegNeigh, BinSeg (yes)
print(ansmean) 
cpts(ansmean)
plot(ansmean,cpt.col='blue')


# change in mean and variance
z=c(rnorm(100,0,1),rnorm(100,5,10), rnorm(100,10,1))
ansmeanvar=cpt.meanvar(z)
plot(ansmeanvar,cpt.width=3)
print(ansmeanvar)


# -------------------------------------------------------

library(EnvCpt)
out = envcpt(y)  # Fit all models at once
out$summary  # Show log-likelihoods
plot(out)

out$meancpt
out$trendcpt
