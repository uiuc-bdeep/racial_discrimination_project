file <- read.csv("~/trulia/stores/los_angeles_ca_rental_house.csv", stringsAsFactors = F)

file$rent_max <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Rent_Per_Month), "-"), `[`, 2)))
file$rent_min <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Rent_Per_Month), "-"), `[`, 1)))

file$Sqft_max <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Sqft), "-"), `[`, 2)))
file$Sqft_min <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Sqft), "-"), `[`, 1)))

write.csv(file, "~/trulia/stores/los_angeles_ca_rental_house.csv", row.names = F)
