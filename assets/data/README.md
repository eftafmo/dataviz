# Map layers

Instruction on building the map layers for a new version of NUTS. This process consists of:

 - downloading the NUTS data in GeoJSON format 
 - adjusting the layers as needed
 - packing the geojson data into TopoJSON files

Current TopoJSON objects:

 - `assets/data/layers{YEAR}.topojson`:
   - frameremote
   - framemalta
   - countries
 - `assets/data/nuts{YEAR}.topojson`
   - nuts0
   - nuts1
   - nuts2
   - nuts3

## Requirements

 - Library that can convert TopJSON to GeoJSON: [topojson-client](https://www.npmjs.com/package/topojson-client)
 - Library that can convert GeoJSON to TopoJSON: [topojson-server](https://www.npmjs.com/package/topojson-server)
 - Software that can view/edit geospatial data, e.g. QGIS 

## API used for downloads

NUTS data can be found and downloaded from this [API](https://gisco-services.ec.europa.eu/distribution/v2/).
There are different dataset with different configuration, specific ones need to be selected for this project. 
The naming convention used is: 
```
theme_spatialtype_resolution_year_projection_subset.format
```

In all datasets the following must be the same:

 - `spatialtype` **must** be RG: regions (multipolygons)
 - `resolution` will determine the size of the file, current 20M is being used
 - `year` **must** be consistent between all downloaded files
 - `projection`, **must** be 4326 (WGS84 World Geodetic System 1984, https://epsg.io/4326)

## Downloading GeoJSON data

Unpack older layers topojson

```
npx topo2geo -i assets/data/layers2016.topojson frameremote.geojson framemalta.geojson countries.geojson
```

Identify required files and download them. (**NOTE THAT FILENAME IS IMPORTANT FOR PACKING INTO TOPOJSON LATER**)

#### Download NUTS levels

```
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_20M_2016_4326_LEVL_0.geojson -O nuts0.geojson
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_20M_2016_4326_LEVL_1.geojson -O nuts1.geojson
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_20M_2016_4326_LEVL_2.geojson -O nuts2.geojson
wget https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_20M_2016_4326_LEVL_3.geojson -O nuts3.geojson
```

#### Download countries, overwriting the unpacked one:

```
wget https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_20M_2016_4326.geojson -O countries.geojson
```

Optionally, remove countries that are not required to reduce the size of the layer.

## Adjust map layers

Import all files into a geospatial data editing  (e.g. QGIS) as vector layers, and move overseas territories 
into the frames.

Note that certain layers will have territories grouped into single multipart geometries. (countries, nuts0) For those 
layers the geometry will need to be split into single parts, adjusted and then regrouped and then merge back into the 
original vector layer. 

After all modifications are done export each layer them back into GeoJSON.

## Packing the TopoJSON files

Create `.topojson` files with the year specified in the filename. For example:

```
npx geo2topo -o assets/data/layers2016.topojson --id-property ID --properties name=name -- frameremote.geojson framemalta.geojson countries.geojson
npx geo2topo -o assets/data/nuts2016.topojson --id-property ID --properties name=name -- nuts0.geojson nuts1.geojson nuts2.geojson nuts3.geojson
```

## Use new layers

Adjust [MapBase.vue](../js/components/includes/MapBase.vue) to use the new files as needed.