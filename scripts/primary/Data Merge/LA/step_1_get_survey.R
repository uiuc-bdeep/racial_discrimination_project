library(jsonlite)
library(dplyr)

URL <- "https://api.ona.io/api/v1/data?owner=chkim12"

options(timeout=1000000)

json <- fromJSON(URL)

response <- list()

for (i in 1:nrow(json)){
  response[[length(response) + 1]] <- fromJSON(json[i,"url"])
}

df <- bind_rows(response)
df$`_notes` <- NULL
df$`_tags` <- NULL
df$`_geolocation` <- NULL
df$`_attachments` <- NULL

write.csv(df, "responses_concatenated.csv", row.names = F)
