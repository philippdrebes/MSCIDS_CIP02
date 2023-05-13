
# Source of the below code: https://github.com/wirhabenzeit/sac-cas-gpx#readme
# Licence of code and usage: https://github.com/wirhabenzeit/sac-cas-gpx/blob/main/LICENSE

# Additional code for scraping SAC Tour Portal GPX Tour data
# Reason: we expect to use this data to calculate / extract the distance of the individual SAC tours,
# This data was missing on the tour webpages which we have scraped, but will be needed for comparison for our later calculations

# We follow the below steps:
# - open the SAC_data_without_index.csv, extract tour IDs
# - we use IDs to open the GXP page information
# - we download the GPX information of the first track in a GPX file, which we will use calculating the distance of the tour
#  - we collect each start and end point coordinates in a separate GPX_start_end.csv, which we will use find duplicates with comparison of tours from other websites

from pyproj import Transformer
import gpxpy
import gpxpy.gpx
import json
import requests
import argparse
import browser_cookie3
import re
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts SAC routes to GPX files')
    parser.add_argument('id', metavar='route_id', type=int, help='SAC ID of the route (last part of the URL)')

    args_lang = "en"
    tour_coord = [] #we create this list - outside of the for loop to save all start and end coordinates, after saving the gxp files

    # Opening the SAC_data file and extracting the tour id column, which we use below
    df_sac_id = pd.read_csv(f"data\SAC_data_without_index0.csv" , sep=';', usecols = ['tour_id'], index_col= False)
    print(df_sac_id)

    # we iterate trough all tour id rows to access the GXP information of the tours, write the first section in a separate GXP file
    for index, id in df_sac_id.iterrows():
        args_id = id['tour_id']
        print(args_id)
        # Access the GXP data
        cj = browser_cookie3.chrome()
        with requests.get(f"https://www.sac-cas.ch/en/?type=1567765346410&tx_usersaccas2020_sac2020%5BrouteId%5D={args_id}&output_lang={args_lang}", cookies=cj) as url:
            data = json.loads(url.content)
        gpx = gpxpy.gpx.GPX()
        transformer = Transformer.from_crs('epsg:2056', 'epsg:4326')

        # We write the GXP data of the first version of the tour in a GXP file
        # Remark: we only take the first track, even if multiple track versions are available
        # Reason: we only scraped the information only about the first tour version previously - keep consistency
        for seg in data['segments']:
            try:
                gpx_track = gpxpy.gpx.GPXTrack(name=re.sub(r'[^A-Za-z0-9\s]+', '', seg['title']),description=re.sub(r'[^A-Za-z0-9\s]+', '', seg['description']))
            except:
                gpx_track = gpxpy.gpx.GPXTrack(name='notitle',description='nodescription')
            gpx.tracks.append(gpx_track)
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)

            if 'geom' in seg and seg['geom']:
                for x,y in map(lambda xy: transformer.transform(*xy),seg['geom']['coordinates']):
                    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(x,y))
            break # Stop, after the first track.
        # Write the data in a GXP file and save it:
        with open(f'data\GPX\SAC-{args_id}.gpx','w', encoding="utf-8") as f:
            f.write(gpx.to_xml())

        # We save the start and end coordinates of each tour in a separate output csv
        try:
            startpoint = str(gpx_segment.points[0].latitude)+";"+str(gpx_segment.points[0].longitude)
            endpoint = str(gpx_segment.points[-1].latitude)+";"+str(gpx_segment.points[-1].longitude)
        except:
            startpoint = "na"
            endpoint = "na"
        tour_coord_dict = {
            'tour_id': args_id,
            'start': startpoint,
            'end': endpoint}
        tour_coord.append(tour_coord_dict)
        df_coord = pd.DataFrame(tour_coord)
        print(df_coord.head(10))
        df_coord.to_csv(f"data\GPX_start_end.csv", sep=';', index=False)

    print("end SacExtractorGPX.py")
    print("end")