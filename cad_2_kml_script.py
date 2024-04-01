from osgeo import ogr, osr

def reverse_geometry_points(geom):
    num_points = geom.GetPointCount()
    reversed_points = [(geom.GetY(i), geom.GetX(i)) for i in range(num_points - 1, -1, -1)]
    
    for i in range(num_points):
        geom.SetPoint(i, *reversed_points[i])

    return geom

def convert_dxf_to_kml(input_file, output_file):
    # Get the input layer
    driver = ogr.GetDriverByName('DXF')
    input_data = driver.Open(input_file, 0)
    input_layer = input_data.GetLayer()

    # Create the output layer
    kml_driver = ogr.GetDriverByName('KML')
    if kml_driver.DeleteDataSource(output_file) != 0:
        print(f'Could not delete {output_file}')
    output_data = kml_driver.CreateDataSource(output_file)

    # Create a spatial reference object for the output projection
    out_srs = osr.SpatialReference()
    out_srs.ImportFromEPSG(proj_epsj)  # Stereo 70, using Longitude/Latitude

    output_layer = output_data.CreateLayer('', srs=out_srs)

    # Copy features from input_layer to output_layer
    output_layer.StartTransaction()
    for feature in input_layer:
        geom = feature.GetGeometryRef()
        geom.TransformTo(out_srs)

        # Reverse the order of points in the geometry
        reversed_geom = reverse_geometry_points(geom)

        out_feature = ogr.Feature(output_layer.GetLayerDefn())
        out_feature.SetGeometry(reversed_geom)
        output_layer.CreateFeature(out_feature)
        out_feature.Destroy()
    output_layer.CommitTransaction()

    # Close the files
    input_data.Destroy()
    output_data.Destroy()

# Define your input and output files
input_file = 'CADASTRE_GEOM.dxf'  # replace with your input file
output_file = 'case.kml'  # replace with your output file

#Set EPSG for your KML output
proj_epsj = 31700

# Call the function
convert_dxf_to_kml(input_file, output_file)
