file <- read.csv("/Users/Chris/Research/trulia_project/test_folder/losangeles_data/los_angeles_ca_rental_5_21_2018.csv", stringsAsFactors = F)

file$rent_max <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Rent_Per_Month), "-"), `[`, 2)))
file$rent_min <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Rent_Per_Month), "-"), `[`, 1)))

file$Sqft_max <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Sqft), "-"), `[`, 2)))
file$Sqft_min <- as.numeric(gsub('[$,]', '', sapply(strsplit(as.character(file$Sqft), "-"), `[`, 1)))

write.csv(file, "/Users/Chris/Research/trulia_project/test_folder/losangeles_data/los_angeles_ca_rental_5_21_2018_2.csv", row.names = F)
