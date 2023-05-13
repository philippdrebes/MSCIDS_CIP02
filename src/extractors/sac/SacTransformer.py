
# we have scraped Data from the SAC Tour Portal page -> SAC_data_without_index.csv
# we have scraped all gpx tour data, the individual files are in the GPX folder and we have collected all start and end points of the tours -> GXP_start_end.csv
# the gpx files we have uploaded into the Schweizmobile tour creator page  - where we scraped the distance of all tours- > Distance_data_without_index.csv

# Now from these 3 files:
# - SAC_data_without_index.csv
# - Distance_data_without_index.csv
# - GXP_start_end.csv

import pandas as pd

####################################################################################
# We will create our stage1 document for SAC part:

# 1. We load and join all data in one dataframe, the key is the tour id which is given in all 3 files:

#open and load all 3 csv documents into the dataframes:
df_sac_data = pd.read_csv(f"data\SAC_data_without_index0.csv", sep=';', index_col=False)
df_sac_GPX = pd.read_csv(f"data\GPX_start_end.csv", sep=';', index_col=False)
df_sac_distance = pd.read_csv(f"data\Distance_data_without_index0.csv", sep=';', index_col=False)

# join GPX_start_end with Distance_data
df_sac_stage1 = df_sac_GPX.join(df_sac_distance.set_index('id'), on='tour_id', how = "outer")

# join stage1_joined with SAC_data
df_sac_stage1 = df_sac_stage1.join(df_sac_data.set_index('tour_id'), on='tour_id', how = "outer")

print(df_sac_stage1)
df_sac_stage1.to_csv("data\\Sac_stage1.csv",sep=';',index = False, encoding="utf-8")

# Remark:
# We have decided to join the csv documents in this order, in order the longer text input are towards the eind of the table
# which creates a better overview at the first sight.

###################################################################################
# Transformation - cleaning of impurities:

# The below natural impurities were available in the stage1 file:
# - NaN values: there were some dead tour page links, we have some NaN data -> we need to remove those rows
# - wrong inputs/clean format: difficulty: clean values containing only T1-T6 (no other values, or no + or -)
# - multiple inputs: time ascent and descent: keep only the longer input if there is a range e.g.: 09:00-09:15 - remove h and transform to time
# - number format: min, max, up, down: remove ' and metric (m or km) transform to integer.
# - start and end: remove ""

# Artifitial impurities introduced in stage2:
# - outliers: min, max outliers: above 5000 and below 0 (given this is the highest and lovest elevation of the tour, this is not possible)

# 2.a. Loading stage2 file with natural and artificial impurities:
df_sac_stage2 = pd.read_csv(f"data\Sac_stage2.csv", sep=';')

# 2.b. Filtering and removing NaN rows:

df_sac_stage2[df_sac_stage2.isnull().any(axis=1)]

# 2.c.




#####################################################################################
# Adding below calculated fields to our data frame:

# To answer our questions we need below calculated columns:
# - Transform the difficulty from T1 - T6 in the same scale as Schweizmobile: easy, medium, difficult
# - Calculate fitness level with the scale of Schweizmobile
# - Calculate a separate columns: start_longitude / start_latitude, end_longitude / end_latitude

#####################################################################################
# Creating and printing stage 3 csv file:




print("end SacTransformer.py")
print("end")
