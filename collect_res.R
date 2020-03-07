library(data.table)
library(ggplot2)
library(grid)
library(gridExtra)
library(reshape2)
library(lemon)
library(RColorBrewer)
library(ggpubr)

setwd("/Users/mac/a2a-challenge/python")

## Color Pallete
col1 = brewer.pal(n=8, name = "Dark2")

## Additional options for title of plots
ggtitle_opts = theme(plot.title = element_text(color = "red", size = 8, face = "bold", hjust=0.5))


## Function that does plotting of individual summary data
plot_data = function(dat, title1, ylab1) {
  
  y = reshape2::melt(dat)
  colnames(y)[1:2] = c("nClusters", "SummaryStats")
  
  p = ggplot(data=y, aes(fill=nClusters, y=value, x=SummaryStats)) 
  p = p + geom_bar(position="dodge", stat="identity") + scale_fill_manual(values=col1)
  p = p + xlab("") + ylab(ylab1) 
  p = p + ggtitle(title1) + ggtitle_opts
  p = p + guides(fill=guide_legend(nrow=1,byrow=TRUE)) ## make legend in horizontal one row 
  
  return(p)
}

## Plots all the results of any clustering and saves relevant data on disk
a2a_plotAll = function(file.pre) {
  res.pre = paste0("output/clustering/", file.pre, "_")
  out.pre = paste0("output/plots/", file.pre)  #prefix for output files
  
  ## intialization
  dist = matrix(nrow=0, ncol=6)
  time1 = matrix(nrow=0, ncol=6)
  bins = matrix(nrow=0, ncol=6)
  sil = matrix(nrow=0, ncol=6)
  
  ## total 
  tot = matrix(nrow=0, ncol=3)
  colnames(tot) = c("totDist", "totTime", "totBins")
  
  
  for (i in 15:20) {
    fn = paste0(res.pre, i, "_tsp.csv")
    f = fread(fn, header = T, data.table = F)
    
    ## get the relevant columns only
    f1 = f[,c(2,3,7,8 )]
    f2 = f1[1:(nrow(f1) - 2), ] # remove last two stats cols
    dat.sum = apply(f2[, -1], 2, summary)
    
    ## distance
    x1 = t(dat.sum[,1, drop =F])
    rownames(x1) = paste0("n", i)
    dist = rbind(dist, x1)
    
    ## time
    x1 = t(dat.sum[,2, drop =F])
    rownames(x1) = paste0("n", i)
    time1 = rbind(time1, x1)
    
    ## bins
    x1 = t(dat.sum[,3, drop =F])
    rownames(x1) = paste0("n", i)
    bins = rbind(bins, x1)
    
    ## Total 
    tot1 = matrix(apply(f2[, -1], 2, sum), nrow=1)
    rownames(tot1) = paste0("n", i)
    tot = rbind(tot, tot1)
    
    ## Silhouette Calculation
    fn = paste0(res.pre, i, "_clusterized_dataset.csv")
    f = fread(fn, header = T, data.table = F)
    
    x1 = matrix(summary(f$Silhouette), nrow=1)
    rownames(x1) = paste0("n", i)
    sil = rbind(sil, x1)
    colnames(sil) = rownames(dat.sum)
  }
  

  p_dist = plot_data(dist, "SummaryStats - Distance Travelled", "metre")  + theme(axis.text.x = element_text(angle = 30))
  p_time = plot_data(time1, "SummaryStats - Time ","second") + theme(axis.text.x = element_text(angle = 30))
  p_sil = plot_data(sil, "SummaryStats - Silhouette Coefficient","") + theme(axis.text.x = element_text(angle = 30))
  
  ## Bins
  title1 = paste0("SummaryStats - Number of Bins", "\n", "(Total = ", tot[1,3], ")") 
  p_bins = plot_data(bins, title1,"nBins") + theme(axis.text.x = element_text(angle = 30))
  p_bins = p_bins 
  
  #ggarrange(p_dist, p1, p_time, p2, p_bins, p_sil, ncol=2, nrow=3, common.legend =T, labels="auto", label.x = .1, label.y = 1.05)
  
  ## Total Values
  tot.df = data.frame(tot)
  tot.df[,1] = tot.df[,1]/1000 ## Km
  tot.df[,2] = tot.df[,2]/3600 ## Hour
  
  p1 = ggplot(data=tot.df, aes(x=rownames(tot), y=totDist)) + geom_bar(stat="identity", fill=col1[1:6]) 
  p1 = p1 + xlab("Number of Clusters ~ Vehicles") + ylab("Total Distance (Km)") 
  p1 = p1 + ggtitle("Total Distance Vs nClusters") + ggtitle_opts
  p2 = ggplot(data=tot.df, aes(x=rownames(tot), y=totTime)) + geom_bar(stat="identity", fill=col1[1:6])
  p2 = p2 + xlab("Number of Clusters ~ Vehicles") + ylab("Total Time (Hour)")
  p2 = p2 + ggtitle("Total Time Vs nClusters") + ggtitle_opts
  
  ## Final plot
  p = ggarrange(p_dist, p1, p_time, p2, p_bins, p_sil, ncol=2, nrow=3, common.legend =T, 
                labels="auto", label.x = .1, label.y = 1.05)
  
  pdf(paste0(out.pre, ".pdf"))
  print(p)
  dev.off()
  
  png(paste0(out.pre, ".png"))
  print(p)
  dev.off()
  
  ## Save the final data
  dist.df = data.frame(nClusters=rownames(dist), dist, total=tot.df$totDist, type = "distance")
  time.df = data.frame(nClusters=rownames(time1), time1, total=tot.df$totTime, type = "time")
  bins.df = data.frame(nClusters=rownames(bins), bins, total=tot.df$totBins, type = "nBins")
  
  ## Combine all results in 1 table and write to disk
  all.df = rbind(dist.df, time.df, bins.df)
  all.df[,2:8] = sapply(all.df[,2:8], round, 2)
  
  write.table(all.df, paste0(out.pre, ".tsv"), sep = "\t", quote = F, row.names = F )
}

######### First Visit
# The following only used for KMeans eq size (Only 1 turn computed due to huge computation time)
# VISIT1_FILE_PRE = "kmeans_equal_size" 
VISIT1_FILE_PRE = "kmeans_first_visit.20190906"
a2a_plotAll(VISIT1_FILE_PRE)

######### Second Visit
VISIT2_FILE_PRE = "kmeans_second_visit.20190906"
a2a_plotAll(VISIT2_FILE_PRE)



