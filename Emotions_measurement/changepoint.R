setwd("/Users/rishabhgupta/Downloads/capstone")

#install.packages("changepoint")
library(changepoint)
set.seed(123)

data <- read.csv('emotionsStrength_15day.csv')
data
fear <- data$fear.pred
plot(fear, type="o")

# Mean Change points
meancpts=cpt.mean(fear, penalty = "MBIC", method = "PELT")
print(meancpts)
cpts(meancpts)
plot(meancpts,cpt.col='blue', xlab="Time", ylab="Fear", main="Mean change-points (Fear)")

# ---- Plot formatting
plot(meancpts, xaxt='n')
axis(1, at=1:24, labels=dates)
# ----------------------

# Variance Change points
varcpts = cpt.var(fear)
print(varcpts)
plot(varcpts)

# Mean & Variance
meanvarcpts = cpt.meanvar(fear, method = "PELT")
print(meanvarcpts)
plot(meanvarcpts, cpt.width=2)

# -------------------------------------------------------

library(EnvCpt)

out = envcpt(fear)  # Fit all models at once
out$summary  # Show log-likelihoods
plot(out)

out$meancpt
out$trendcpt

# -------------------------------------------------------

library(stringr)

dates <- str_c(data$day,"-",data$month,"-", data$year)

# for (emotion in colnames(data)[3:ncol(data)]) {
  # ser <- data$emotion
for (col_idx in 2:ncol(data)) {
  ser <- data[,col_idx]
  print(length(ser))
  emotion <- colnames(data)[col_idx]
  emotion <- substring(emotion, 1, nchar(emotion)-5)
  print(emotion)
  
  # Mean Change points
  meancpts=cpt.mean(ser, penalty = "MBIC", method = "PELT")
  png(file=paste0(emotion, "_meancpt.png"),
      width=1800, height=1200, res=300)
  plot(meancpts,
       cpt.col='blue',
       cpt.width=2,
       xlab="Time", ylab=emotion,
       main=paste0(toupper(emotion), "\nMean change-points"),
       xaxt='n')
  axis(1, at=1:length(ser), labels=dates)
  dev.off()

  # Variance Change points
  varcpts = cpt.var(ser)
  png(file=paste0(emotion, "_varcpt.png"),
      width=1800, height=1200, res=300)
  plot(varcpts,
       cpt.width=2,
       xlab="Time", ylab=emotion,
       main=paste0(toupper(emotion), "\nVariance change-points"),
       xaxt='n')
  axis(1, at=1:length(ser), labels=dates)
  dev.off()

  # Mean & Variance
  meanvarcpts = cpt.meanvar(ser, method = "PELT")
  png(file=paste0(emotion, "_meanvarcpt.png"),
      width=1800, height=1200, res=300)
  plot(meanvarcpts,
       cpt.width=2,
       xlab="Time", ylab=emotion,
       main=paste0(toupper(emotion), "\nMean-Variance change-points"),
       xaxt='n')
  axis(1, at=1:length(ser), labels=dates)
  dev.off()

}





