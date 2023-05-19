# This code will load the stage 3 document to maria DB.

# Module Imports
import pandas as pd
import mariadb
import sys
# Connect to MariaDB Platform
def sacloader():
    df = pd.read_csv(f"data/Sac_stage3.csv", sep=',', index_col=False, encoding='utf-8')

    # Connect to MariaDB Platform
    conn_params = {
        "user": "cip_user",
        "password": "cip_pw",
        "host": "127.0.0.1",
        "database": "CIP"}

    # Establish a connection
    try:
        connection = mariadb.connect(**conn_params)
        cursor = connection.cursor()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cursor = connection.cursor()
    try:
        cursor.execute(
            "CREATE TABLE sac( tour_id int, start varchar(255), end varchar(255), distance_clean varchar(255), ascent_clean varchar(255), descent_clean varchar(255), time_ascent_clean TIME, time_descent_clean TIME, difficulty varchar(255), difficulty_calc1 varchar(255), fitness_calc2 varchar(255), leistungskm_calc3 varchar(255), min_clean int, max_clean int , title TEXT, subtitle text, link text , map text, description text )" )

        sql = "INSERT INTO sac (tour_id,start,end,distance_clean,ascent_clean,descent_clean,time_ascent_clean," \
          "time_descent_clean,difficulty,difficulty_calc1,fitness_calc2,leistungskm_calc3,min_clean,max_clean,title," \
          "subtitle,link,map,description) " \
          "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        data = []

        for index, row in df.iterrows():
            data.append(
                (row['tour_id'], row['start'], row['end'], row['distance_clean'], row['ascent_clean'], row['descent_clean'],
                 row['time_ascent_clean'], row['time_descent_clean'],row['difficulty'], row['difficulty_calc1'],
                 row['fitness_calc2'], row['leistungskm_calc3'],row['min_clean'], row['max_clean'],
                 row['title'], row['subtitle'], row['link'], row['map'],row['description'])
            )

        # insert data
        cursor.executemany(sql, data)
        connection.commit()
    except:
        print("Table already created.")
    # Print Result
    cursor.execute("SELECT * FROM sac ")
    for (tour) in cursor:
        print(f"Tour : {tour}")

    # free resources
    cursor.close()
    connection.close()

if __name__ == '__main__':
    print("Start Sac Loader")
    sacloader()
    print("Sac Loader has ended")