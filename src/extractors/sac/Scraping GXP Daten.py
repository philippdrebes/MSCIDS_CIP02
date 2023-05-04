
# Source of the below code: https://github.com/wirhabenzeit/sac-cas-gpx#readme
# Licence of code and usage: https://github.com/wirhabenzeit/sac-cas-gpx/blob/main/LICENSE

# Additional data for scraping SAC Tour POrtal GXP Tour data
# Reason we expect to use this data to calculate / extract the distance of the individual tours,
#given this data was missing on the Tour webpages which we have scraped, but will be needed for comparison

from pyproj import Transformer
import gpxpy
import gpxpy.gpx
import json
import requests
import argparse
import browser_cookie3
import re

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts SAC routes to GPX files')
    parser.add_argument('id', metavar='route_id', type=int, help='SAC ID of the route (last part of the URL)')
#    parser.add_argument('-lang', type=str, default="en", help="language [de/en/it/fr]")

    args_lang = "en"

    with open(f"data\SAC_page_links.csv","r") as urls:
        urls.readline()
        for url in urls:
            print(url)
            args_id = re.search(r'(\d+)(?!.*\d)', url).group(1)
            print(args_id)

            cj = browser_cookie3.chrome()
            with requests.get(f"https://www.sac-cas.ch/en/?type=1567765346410&tx_usersaccas2020_sac2020%5BrouteId%5D={args_id}&output_lang={args_lang}", cookies=cj) as url:
                data = json.loads(url.content)

            gpx = gpxpy.gpx.GPX()
            # gpx.name = f'{data["destination_poi"]["display_name"]} ({data["title"]})'
            # gpx.description = data["teaser"]
            # gpx.author_name = data["author"]["full_name"]

            transformer = Transformer.from_crs('epsg:2056', 'epsg:4326')

            for seg in data['segments']:
              #  if seg['description'] == title:
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

            # wps = [data['departure_point']] + [wp['reference_poi'] for wp in data['waypoints']] + [data['destination_poi']]
            # for wp in wps:
            #     gpx_wp=gpxpy.gpx.GPXWaypoint(*transformer.transform(*wp['geom']['coordinates']),name=wp['display_name'])
            #     gpx.waypoints.append(gpx_wp)
                break # Stop, after the first track.
            with open(f'data\GPX\SAC-{args_id}.gpx','w', encoding="utf-8") as f:
                f.write(gpx.to_xml())

    print("program end")