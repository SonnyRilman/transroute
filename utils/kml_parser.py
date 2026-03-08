import xml.etree.ElementTree as ET

def parse_kml(filepath):
    """
    Parse KML file to extract nodes (Placemark with Point) and edges (Placemark with LineString).
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    # Handle namespace if present
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    nodes = {}
    edges = []

    for placemark in root.findall('.//kml:Placemark', ns):
        name_elem = placemark.find('kml:name', ns)
        name = name_elem.text if name_elem is not None else "Unnamed"
        
        point = placemark.find('.//kml:Point/kml:coordinates', ns)
        linestring = placemark.find('.//kml:LineString/kml:coordinates', ns)
        
        if point is not None:
            # Format: "lon,lat,alt"
            coords = point.text.strip().split(',')
            lon, lat = float(coords[0]), float(coords[1])
            nodes[name] = (lat, lon) # Store as (lat, lon) for Haversine & Folium
            
        elif linestring is not None:
            # Line strings can have multiple coordinates separated by space/newlines
            coords_text = linestring.text.strip().split()
            line_coords = []
            for c in coords_text:
                if c.strip():
                    parts = c.split(',')
                    line_coords.append((float(parts[1]), float(parts[0]))) # Store as (lat, lon)
            edges.append({'name': name, 'coordinates': line_coords})

    return nodes, edges
