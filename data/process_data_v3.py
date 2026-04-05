import os
import json
import xml.etree.ElementTree as ET
import re

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
HALTE_KML = os.path.join("data", "Halte.kml")
JALUR_KML = os.path.join("data", "Jalur Rute.kml")
HALTE_JSON = os.path.join("data", "halte_info.json")
KORIDOR_JSON = os.path.join("data", "koridor.json")
SAMPLE_V3_KML = os.path.join("data", "sample_route_v3.kml")

# ══════════════════════════════════════════════════════════════════════════════
# DATA PARSERS & HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def parse_description(desc):
    """
    Parse KML description CDATA to extract koridor and their specific destinations.
    Example: 1A _ Trans Jogja<br><br>Tujuan / Destination => Demangan
    """
    if not desc: return [], []
    parts = re.split(r'<br\s*/?>', desc)
    koridors = []
    destinations = []
    current_k = None
    for p in parts:
        p = p.strip()
        if not p: continue
        # Koridor detection
        k_match = re.search(r'^([A-Z0-9L-]+)\s*_\s*Trans Jogja', p, re.I)
        if k_match:
            current_k = k_match.group(1).upper()
            if current_k not in koridors: koridors.append(current_k)
            continue
        # Destination detection
        d_match = re.search(r'Tujuan\s*/\s*Destination\s*=>\s*(.*)', p, re.I)
        if d_match and current_k:
            dest = d_match.group(1).strip()
            destinations.append(f"{current_k} → {dest}")
    return koridors, destinations

def infer_region(name):
    """
    Infer region (Yogyakarta, Sleman, Bantul) based on stop name keywords.
    """
    n = name.lower()
    sleman = ['sleman', 'condongcatur', 'depok', 'gamping', 'mlati', 'ngaglik', 'seyegan', 'godean', 'kalasan', 'maguwo', 'babarsari', 'jombor']
    bantul = ['bantul', 'sewon', 'kasihan', 'banguntapan', 'piyungan', 'imogiri', 'pundong', 'giwangan', 'parangtritis']
    if any(k in n for k in sleman): return "Kabupaten Sleman"
    if any(k in n for k in bantul): return "Kabupaten Bantul"
    return "Kota Yogyakarta"

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PROCESSING
# ══════════════════════════════════════════════════════════════════════════════

def process_v3():
    print("Starting Data Processing v3...")
    
    if not os.path.exists(HALTE_KML):
        print(f"Error: {HALTE_KML} not found.")
        return

    # 1. Parse Halte (Stops)
    tree_h = ET.parse(HALTE_KML)
    root_h = tree_h.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    halte_data = {}
    koridor_stops = {} # kode -> set of stop names
    
    for placemark in root_h.findall('.//kml:Placemark', ns):
        name_elem = placemark.find('kml:name', ns)
        name = name_elem.text if name_elem is not None else "Unknown"
        
        desc_elem = placemark.find('kml:description', ns)
        description = desc_elem.text if desc_elem is not None else ""
        
        point = placemark.find('.//kml:Point/kml:coordinates', ns)
        lat, lon = 0.0, 0.0
        if point is not None:
            c = point.text.strip().split(',')
            lon, lat = float(c[0]), float(c[1])
            
        koridors, dests = parse_description(description)
        region = infer_region(name)
        
        halte_data[name] = {
            "alamat": f"{name}, {region}",
            "wilayah": region,
            "fasilitas": ["Shelter", "Rambu Informasi", "Kursi Tunggu"],
            "koridor": koridors,
            "tujuan": dests,
            "lat": lat,
            "lon": lon,
            "jam_operasi": "05:00 - 21:00",
            "status": "Aktif"
        }
        
        for k in koridors:
            if k not in koridor_stops: koridor_stops[k] = []
            if name not in koridor_stops[k]: koridor_stops[k].append(name)

    # 2. Save JSONs
    with open(HALTE_JSON, 'w', encoding='utf-8') as f:
        json.dump(halte_data, f, indent=2)
    print(f"Saved {len(halte_data)} stops to {HALTE_JSON}")

    # Generate Koridor List
    colors = ["#3b82f6", "#10b981", "#a78bfa", "#f59e0b", "#f43f5e", "#8b5cf6", "#14b8a6", "#f97316", "#db2777"]
    koridor_list = []
    for i, (kode, stops) in enumerate(sorted(koridor_stops.items())):
        koridor_list.append({
            "kode": kode,
            "nama": f"Koridor TransJogja {kode}",
            "rute": f"{stops[0]} → {stops[-1]}",
            "halte": stops,
            "jam_operasi": "05:30 – 21:00",
            "tarif": "Rp 3.500",
            "interval": "15–20 menit",
            "warna": colors[i % len(colors)]
        })
    with open(KORIDOR_JSON, 'w', encoding='utf-8') as f:
        json.dump(koridor_list, f, indent=2)
    print(f"Saved {len(koridor_list)} corridors to {KORIDOR_JSON}")

    # 3. Generate sample_route_v3.kml (Merging all into one KML for visualization)
    # This KML will contain all points and lines from Jalur Rute.kml
    print("Generating sample_route_v3.kml...")
    kml_v3 = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc_v3 = ET.SubElement(kml_v3, 'Document')
    name_v3 = ET.SubElement(doc_v3, 'name')
    name_v3.text = "TransJogja Complete Network v3"
    
    # Add Stops to KML
    for name, data in halte_data.items():
        pm = ET.SubElement(doc_v3, 'Placemark')
        nm = ET.SubElement(pm, 'name')
        nm.text = name
        pt = ET.SubElement(pm, 'Point')
        co = ET.SubElement(pt, 'coordinates')
        co.text = f"{data['lon']},{data['lat']},0"
        
    # Add Lines if exist
    if os.path.exists(JALUR_KML):
        tree_j = ET.parse(JALUR_KML)
        for pm_j in tree_j.getroot().findall('.//kml:Placemark', ns):
            if pm_j.find('.//kml:LineString', ns) is not None:
                doc_v3.append(pm_j) # Copy lines
                
    tree_v3 = ET.ElementTree(kml_v3)
    tree_v3.write(SAMPLE_V3_KML, encoding='utf-8', xml_declaration=True)
    print(f"sample_route_v3.kml generated successfully.")

if __name__ == "__main__":
    process_v3()
