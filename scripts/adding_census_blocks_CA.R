###################################
# Prelimilary
rm(list=ls())
pkgTest <- function(x) {
  if (!require(x, character.only = TRUE))
  {
    install.packages(x, dep = TRUE)
    if(!require(x, character.only = TRUE)) stop("Package not found")
  }
}

## These lines load the required packages
packages <- c("readxl", "data.table", "rgdal", "sp")
lapply(packages, pkgTest)

get_layerName <- function(shp_file_path)
{
  relative_path <- path.expand(shp_file_path)
  print(relative_path)
  return(ogrListLayers(relative_path)[1])
}

input_points <- read.csv("~/trulia/stores/LA_trulia.csv")
#input_points <- LA_final
points <- input_points
## remove NAs for lat and lon for shapefile
points <- points[which(!is.na(points$Longitude) & !is.na(points$Latitude)),]
# step 2-2: transfer it into shapefile #
coordinates(points) <- cbind(points$Longitude, points$Latitude)
proj4string(points) <- CRS("+proj=longlat")


polygons_path <- paste0("~/share/projects/Zillow_Housing/stores/CensusBlocks/06/tl_2016_06_tabblock10.shp") # "~/share/projects/zillow/stores/CensusBlocks/09/tl_2016_09_tabblock10.shp"
# step 4: preprocess for the polygons #
shpLayerName <- get_layerName(polygons_path)
shp_poly <- readOGR(path.expand(polygons_path), shpLayerName)
# step 4-1: checking for default projection #
if(is.na(proj4string(shp_poly))){
  default_projection <- CRS("+proj=longlat +datum=WGS84 +ellps=WGS84 +towgs84=0,0,0")
  proj4string(shp_poly) <- CRS(default_projection)
}

# step 5: transform the projection from points to the projection of the shapefile #
points <- spTransform(points, proj4string(shp_poly))
proj4string(points) <- proj4string(shp_poly)

# step 6: perform the over operation #
res <- over(points, shp_poly)

# step 7: Appending the polygons' information to points dataframe #
#points_res <- as.data.frame(points_raw)
points_res <- cbind(input_points, res)

write.csv(points_res, "~/trulia/stores/LA_trulia_tract.csv", row.names = F)
