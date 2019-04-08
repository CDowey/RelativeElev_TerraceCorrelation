# RelativeElev_TerraceCorrelation
### Relative Elevation Models and Fluvial Terrace Correlation for paleo-river gradients.

A popular cartographic technique for creating eye-catching maps of rivers and their past meanders is to detrend a DEM by the gradient of the modern river. I was first exposed to this technique through the work of [Daniel Coe](https://kartopics.com/portfolio/).

My idea is to try to use this techinque to build detrended DEM's and correlate Late Pleistocene and Holocene river terraces preserved adjacent to modern rivers in Vermont. 

One of the challenges this presents is that these paleo-rivers had different gradients in the past. The paleo-river gradients were controlled by now-eroded sediment in the river valleys, ice-fronts, and glacial lakes, that provided different base-levels and knick-points that can be hard to recreate or esitmate. In addition, during this period a decreasing mass of ice compressed the continental crust in New England and isostatic rebound adjusted the slope of the entire landscape. Best estimates suggest this uplift is equivalent to 0.9m/km in this part of Vermont ([Koeteff and Larsen, 1989](https://link.springer.com/chapter/10.1007%2F978-94-009-2311-9_8)); another factor to consider.

However, if we can streamline the process of building these relative elevation models (allowing for further tweaking) we can efficiently test numerous paleo-river gradients derived from clues on the landscape.

LiDAR information from the [Vermont Center for Geographic Information](http://geodata.vermont.gov/) provides incredible detail on the morphology and elevation of these terraces. Combined with geologic mapping from the Vermont Geological Survey and my own identification of alluvial terraces we have information about the size, shape, and elevation of these features.

The relative elevation models are constructed following the three techniques described in [Olson et al., 2014](https://fortress.wa.gov/ecy/publications/documents/1406025.pdf). The models are constructed using arcpy tools so they can be shared amongst Vermont Geological Survey mappers and run in the Python window of ArcGIS Pro or ArcMap, software that most mappers use.
