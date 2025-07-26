import csv
import geopandas as gpd
import folium.map

with open("./sample.csv") as f:
    csv_san= csv.reader(f)

    l=[row for row in csv_san]
print(l[0])
df=gpd.read_file("./usedata/N02-20_GML/N02-20_RailroadSection.geojson")
import folium
map=folium.Map([35.241669,136.257161])
folium.GeoJson(df, 
              style_function = lambda x: {
                                        'fillOpacity': 0.5,
                                        'fillColor': 'Orange',
                                        'color': 'Red'
              }
              ).add_to(map)
for i in range(1,len(l)):
    folium.Circle([float(l[i][1]),float(l[i][2])],radius=10,color="green" if l[i][-1]=="True" else "blue").add_to(map)

map.save("ex.html")

    # print(csv_san)