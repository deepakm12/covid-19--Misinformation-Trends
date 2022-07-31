setwd("/Users/rishabhgupta/Downloads/capstone/cross")


### Stationarity example code -------------------------------------
# Prereq for CCF analysis

library(tseries)
# Stationarity of time series
# TS1, TS2

ts1=c(rnorm(100,0,1),rnorm(100,5,10), rnorm(100,10,1))
ts2=c(rnorm(100,24,1),rnorm(100,5,10))

ts2_processed = diff(diff(ts2))

plot(ts1)
plot(ts2)
plot(ts2_processed)

# ADF test
adf.test(ts1) # p < 0.05? - If Yes -> Stationary
adf.test(ts2)
adf.test(ts2_processed)

fear_tc <- read.csv('fear_si.csv')
fear_tc
#ccf(fear_tc[400:nrow(fear_tc),1], fear_tc[400:nrow(fear_tc),2])
ccf(fear_tc['stringency_index'], fear_tc['fear'])
#ccf(fear_tc['fear'], fear_tc['new_cases'])


library(tseries)
adf.test(fear_tc$stringency_index)

#test befor plotting
adf.test(fear_tc$fear)
plot(fear_tc$new_cases)
plot(fear_tc$fear)

