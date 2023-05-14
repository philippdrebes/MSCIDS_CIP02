
# we have scraped Data from the SAC Tour Portal page -> SAC_data_without_index.csv
# we have scraped all gpx tour data, the individual files are in the GPX folder and we have collected all start and end points of the tours -> GXP_start_end.csv
# the gpx files we have uploaded into the Schweizmobile tour creator page  - where we scraped the distance of all tours- > Distance_data_without_index.csv

# Now from these 3 files we create first our stage1 than our stage3 file:
# - SAC_data_without_index.csv
# - Distance_data_without_index.csv
# - GXP_start_end.csv

import pandas as pd
import random
import datetime

print("1. We will create our stage1 document for SAC part:")
####################################################################################
print(80*"*")
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
df_sac_stage1.to_csv("data\\Sac_stage1.csv",sep=',',index = False, encoding="utf-8")

# Remark:
# We have decided to join the csv documents in this order, in order the longer text input are towards the eind of the table
# which creates a better overview at the first sight.

print(" 2. Transformation - creating our artificial stage2 file:")
###################################################################################
print(80*"*")

# The below natural impurities were available in the stage1 file:
# - NaN values: there were some dead tour page links, we have some NaN data -> we need to remove those rows
# - wrong inputs/clean format: difficulty: clean values containing only T1-T6 (no other values, or no + or -)
# - multiple inputs: time ascent and descent: keep only the longer input if there is a range e.g.: 09:00-09:15 - remove h and transform to time
# - number format: min, max, up, down: remove ' and metric (m or km) transform to integer.
# - start and end: remove ""

# Injecting artificial impurities  in stage2:
# - outliers: min, max outliers

def myrandom(seed):
    random.seed(seed)
    x = [random.randint(1,1100) for i in range(1,11)]
    return x

df_sac_stage2 = df_sac_stage1
for number in myrandom(9001):
    #df_sac_stage2['min'][ number] = "99"+df_sac_stage2['min'][ number]
    df_sac_stage2['min'] = df_sac_stage2['min'].replace(df_sac_stage2['min'][number],"99" + df_sac_stage2['min'][number])
for number in myrandom(9003):
    df_sac_stage2['max'] = df_sac_stage2['max'].replace(df_sac_stage2['max'][number], "-" + df_sac_stage2['max'][number])
df_sac_stage2.to_csv("data\\Sac_stage2.csv" ,sep=',',index = False, encoding="utf-8")

print("3. Filtering and removing missing values and not mountain hiking tours:")
# ###############################################################################################
print(80*"*")

print("\n check duplicates: \n")
print(df_sac_stage2[df_sac_stage2.duplicated(keep=False)])
# -> We do not have duplicate rows

#Removing na-s not relevant tours:
df_sac_stage2.info()
# We see that all columns contain 1373 values except map and description.
# We assume these rows are the tours, where dead link or no information could be scraped.
# We look at missing map values more closely:
def get_null_value(df,column):
    df_null_value = df[df[column].isnull()]
    #df_null_value.to_csv("data\\"+column +"_null.csv" ,sep=',',index = False) -> makes easier inspecting the files.
    print(df_null_value)
    return df_null_value

def get_specific_value(df,column,value,boolean):
    df_specific_value = df[df[column].str.contains(value) == boolean]
    #df_specific_value.to_csv("data\\"+column + "_" + value + "_" + str(boolean) +".csv" ,sep=',',index = False)  -> makes easier inspecting the files.
    print(df_specific_value)
    return df_specific_value

print("3.1 NAN values in map")
get_null_value(df_sac_stage2,'map')
# If we look at the page link we can see they are all snowshoeing tours NOT hiking tours, so we can drop them from our database.
df_sac_stage2v1 = df_sac_stage2[df_sac_stage2.map.notnull()]
# our new dataframe is stage2 version 1:
df_sac_stage2v1.info()

print("3.2 NaN values in description")
get_null_value(df_sac_stage2v1,'description')
# here we have 2 mountain hiking tours and 6 via ferrata rows -> we need further investigation on tour types:

print(80*"*")
print("We are filtering out all NON-mountain-hiking tours:")
df_sac_stage2_NoMountainHiking = get_specific_value(df_sac_stage2v1, 'link','mountain-hiking', False)
# we check the unique values of tour type:
print("\n In Non-hikig-tour list are below tour types:\n ")
print(df_sac_stage2_NoMountainHiking.link.str.extract(r'^(?:[^\/]*\/){7}\s*([\w-]+)')[0].unique())
# we see there is no mountain hiking, so we can drop all this values

print(80*"*")
print("We filter all tours containing mountain hiking values and store in our stage2v2 dataframe:")
df_sac_stage2v2 = get_specific_value(df_sac_stage2v1, 'link','mountain-hiking', True)
df_sac_stage2v2.info()

# we have still missing values in description column:
get_null_value(df_sac_stage2v2,'description')
# Missing description is ok, we decide to keep those tours.

print("4. Inspecting, cleaning na values")
###############################################################################################
print(80*"*")

# 4.1 Checking "na" values in start and end coordinates:
get_specific_value(df_sac_stage2v2, 'start','na', True) # -> We have 10 rows
# Given we do not have the GPX coordinates, we do not have distance and start and end dates,
# we will not be able to join them in the overall database (stage3 merge) and calculating of fitness level wil not be possible
# so we exclude them from our dataframe.

# Our new dataframe going forward is:
df_sac_stage2v3 = get_specific_value(df_sac_stage2v2, 'start','na', False)

# 4.2 Inspecting rows where we have added "na" values while the scraping process:

# We filter rows which are NOT connected to elevation, ascent and descent and any values are "na"
# This is an empty list -> no more na values in these columns.
df_sac_stage2v3.query('tour_id =="na" | start =="na" | end =="na" | distance =="na" | title =="na" | subtitle =="na" | difficulty =="na" | link =="na" | map =="na" | description =="na"')#.to_csv("data\\query1.csv" ,sep=';',index = False)

# We filter rows which are connected to elevation:
df_sac_stage2v3.query('time_ascent =="na" | ascent =="na" | time_descent =="na" | descent =="na" | up =="na" | down =="na" | min =="na" | max =="na"')#.to_csv("data\\query2.csv" ,sep=',',index = False)
# We keep all the remaining "na" values in the data frame, given there are often either ascent or descent data available.

print("5 Removing metrics & outliers")
###############################################################################################

# 5.1 Remove metric & time units: m, km and h and format numbers
def remove_metrics(df, column, metrics, dtype):
    return df.join( df[column].str.replace(metrics, "", regex=True).astype(dtype=dtype, errors="ignore"), rsuffix='_clean')

# Align time format
def convert_time(value):
    if len(value) == 1:
        value = "0"+value + ":00"
    elif value == "na":
        value = "00:00"
    return value

df_sac_stage2v4 = df_sac_stage2v3
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'distance','km',float) #remove metrics km and format number to float
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'up','[^\\d]',int) #remove metrics m and format number to integer
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'down','[^\\d]',int) #remove metrics m and format number to integer
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'min','[^\\d]',int) #remove metrics m and format number to integer, outliers negative values already corrected
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'max','[^\\d]',int) #remove metrics m and format number to integer, outliers negative values already corrected
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'ascent','m',int) #remove metrics m and format number to integer
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'descent','m',int) #remove metrics m and format number to integer
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'difficulty','[^T\\d]',str) #remove + or - in string
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'time_ascent','(?!(\w)|\d*\:?\d+).*',str) #remove h and take the last duration if multiple available
df_sac_stage2v4 = remove_metrics(df_sac_stage2v4,'time_descent','(?!(\w)|\d*\:?\d+).*',str) #remove h and take the last duration if multiple available

# Convert the string column to a time column
df_sac_stage2v4['time_ascent_clean'] = df_sac_stage2v4['time_ascent_clean'].apply(convert_time)
df_sac_stage2v4['time_ascent_clean'] = pd.to_datetime(df_sac_stage2v4['time_ascent_clean'], format='%H:%M').dt.time

df_sac_stage2v4['time_descent_clean'] = df_sac_stage2v4['time_descent_clean'].apply(convert_time)
df_sac_stage2v4['time_descent_clean'] = pd.to_datetime(df_sac_stage2v4['time_descent_clean'], format='%H:%M').dt.time

#Optional to inspect csv document:
#df_sac_stage2v4.to_csv("data\\clean.csv" ,sep=',',index = False, encoding="utf-8")

# 5.2. Checking further outliers
# We take as borders the highest and lowers point of Switzerland
# - Dufourspitze is with 4.634 m
# - Lago Maggiore is with 193 m
# For Ascent and descent we take the difference as maximum ascent (as it is a trail running, if someone is climbing more than this elevation in a tour / one day).
# For diestance we take as upper limit 50km as it is longer as marathon distance and very demanding distance for hiking tours for 1 day.

def outliers_CH(df, column,min_value, max_value):
    print(80 * "*")
    print("Outliers "+ column)
    print(df[(df[column] < min_value) | (df[column] > max_value )][column])
    return df[(df[column] < min_value) | (df[column] > max_value )]

print(outliers_CH(df_sac_stage2v4, 'min_clean', 193, 4634))
print(outliers_CH(df_sac_stage2v4, 'max_clean', 193, 4634))
print(outliers_CH(df_sac_stage2v4, 'distance_clean', 0, 50))
print(outliers_CH(df_sac_stage2v4, 'up_clean', 0, 4634-193))
print(outliers_CH(df_sac_stage2v4, 'down_clean', 0, 4634-193))

# We can see we do only have outliers in min_clean column -> where we have the lowest points of the tours.
# We see a pattern that all outliers begin with a pattern of 99 - so we decide to remove this 2 digits in front of the numbers:

def clean_99(value):
    if str(value).startswith("99") and value > 9000: # min high is over 100m, a dirty value must be over 9000
        value_str = str(value)[2:]
        value = int(value_str)
    return value

df_sac_stage2v5 = df_sac_stage2v4
df_sac_stage2v5['min_clean'] = df_sac_stage2v5['min_clean'].apply(clean_99)

#Optional to inspect csv document:
#df_sac_stage2v5.to_csv("data\\clean2.csv" ,sep=',',index = False, encoding="utf-8")

print("6. Calculated fields")
###############################################################################################
print(80*"*")

# We will calculate below fields with conditions:
#  - difficulty: easy(T1), medium(T2+T3), difficult(T4+T5+T6)
#  - fitness level:
#    easy: distance ≤ 12 km ,elevation difference ≤ 400 hm, total time: ≤ 3 h
#    medium: distance ≤ 20 km ,elevation difference ≤ 900 hm, total time: ≤ 5 h
#    difficult: distance > 20 km ,elevation difference > 900 hm, total time: > 5 h

print("6.1 Difficulty levels -> calculated column 1")

def difficulty(value):
    if value == "T1":
        value = "easy"
    elif value == "T2" or value == "T3":
        value = "medium"
    else:
        value = "difficult"
    return value

df_sac_stage2v5['difficulty_calc1'] = df_sac_stage2v5['difficulty_clean'].apply(difficulty)
print(df_sac_stage2v5['difficulty_calc1'])

print(" 6.2 Fitness level -> calculated column 2")

def fitness(distance,ascent,time_ascent, time_descent):
    try:
        if distance<= 12 and int(ascent) <= 400 and (time_ascent <= datetime.time(3, 0) or time_descent <= datetime.time(3, 0)):
            value = "easy"
        elif distance <= 20 and int(ascent) <= 900 and (time_ascent <= datetime.time(5, 0) or time_descent <= datetime.time(5, 0)):
            value = "medium"
        else:
            value = "difficult"
    except:
        value = "na"
    return value

df_sac_stage2v5['fitness_calc2'] = df_sac_stage2v5.apply(lambda x: fitness(x['distance_clean'],x['ascent_clean'], x['time_ascent_clean'], x['time_descent_clean']), axis=1)
print(df_sac_stage2v5['fitness_calc2'])

print("6.3  'leistungskilometer' -> calculated column 3")
# Calculation: Distance + total ascent / 100m

def leistungskm(distance, ascent):
    try:
        value = round(distance + int(ascent)/100)
    except:
        value = round(distance)
    return value

df_sac_stage2v5['leistungskm_calc3'] = df_sac_stage2v5.apply(lambda x: leistungskm(x['distance_clean'],x['ascent_clean']), axis=1)
print(df_sac_stage2v5['leistungskm_calc3'])

print("7. Remove unwanted columns and print stage3 csv")
###############################################################################################
print(80*"*")

# Drop the original string column
df_sac_stage3 = df_sac_stage2v5.drop(['distance','up','down','min','max','time_ascent','ascent','time_descent','descent','difficulty_clean', 'up_clean','down_clean',], axis=1)
df_sac_stage3 = df_sac_stage3.loc[:,['tour_id','start','end','distance_clean','ascent_clean','descent_clean','time_ascent_clean','time_descent_clean','difficulty','difficulty_calc1','fitness_calc2','leistungskm_calc3','min_clean','max_clean','title','subtitle', 'link','map','description']]
df_sac_stage3.to_csv("data\\Sac_stage3.csv" ,sep=',',index = False, encoding="utf-8")

print("end SacTransformer.py")
print("end")
