from tkinter import Tk, Label, Button, Entry, filedialog, StringVar
from osgeo import ogr, osr

def reverse_geometry_points(geom):
    num_points = geom.GetPointCount()
    reversed_points = [(geom.GetY(i), geom.GetX(i)) for i in range(num_points - 1, -1, -1)]
    
    for i in range(num_points):
        geom.SetPoint(i, *reversed_points[i])

    return geom

def convert_dxf_to_kml(input_file, output_file, epsg):
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
    out_srs.ImportFromEPSG(int(epsg))  # Use the EPSG value from the entry box

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

def select_input_file():
    input_file = filedialog.askopenfilename(title="Select DXF file", filetypes=[("DXF files", "*.dxf")])
    if input_file:
        input_file_entry.delete(0, 'end')
        input_file_entry.insert(0, input_file)

def select_output_file():
    output_file = filedialog.asksaveasfilename(title="Save KML file", filetypes=[("KML files", "*.kml")])
    if output_file:
        if not output_file.lower().endswith('.kml'):
            output_file += '.kml'
        output_file_entry.delete(0, 'end')
        output_file_entry.insert(0, output_file)

def convert():
    input_file = input_file_entry.get()
    output_file = output_file_var.get()
    epsg = epsg_entry.get()
    convert_dxf_to_kml(input_file, output_file, epsg)
    status_label.config(text="Conversion complete!")

# Create the main application window
root = Tk()
root.title("DXF to KML Converter")

# Set window icon
root.iconbitmap('sigla.ico')

# Input file selection
input_file_label = Label(root, text="Input DXF file:")
input_file_label.grid(row=0, column=0, padx=10, pady=5)
input_file_entry = Entry(root, width=50)
input_file_entry.grid(row=0, column=1, padx=10, pady=5)
input_file_button = Button(root, text="Browse", command=select_input_file)
input_file_button.grid(row=0, column=2, padx=5, pady=5)

# Output file selection
output_file_label = Label(root, text="Output KML file:")
output_file_label.grid(row=1, column=0, padx=10, pady=5)
output_file_var = StringVar()
output_file_entry = Entry(root, textvariable=output_file_var, width=50)
output_file_entry.grid(row=1, column=1, padx=10, pady=5)
output_file_button = Button(root, text="Browse", command=select_output_file)
output_file_button.grid(row=1, column=2, padx=5, pady=5)

# EPSG value entry
epsg_label = Label(root, text="EPSG:")
epsg_label.grid(row=2, column=0, padx=10, pady=5)
epsg_entry = Entry(root, width=50)
epsg_entry.grid(row=2, column=1, padx=10, pady=5)

# Convert button
convert_button = Button(root, text="Convert", command=convert)
convert_button.grid(row=3, column=1, padx=10, pady=10)

# Status label
status_label = Label(root, text="")
status_label.grid(row=4, column=0, columnspan=3)

root.mainloop()
