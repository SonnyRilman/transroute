from utils.kml_parser import parse_kml
from utils.graph_logic import build_graph
import networkx as nx

n, e = parse_kml()
G = build_graph(n, e)

start = "Terminal Prambanan"
dest = "Malioboro 1"

print(f"Start node in G: {start in G}")
print(f"Dest node in G: {dest in G}")

if start in G and dest in G:
    has_path = nx.has_path(G, start, dest)
    print(f"Path exists: {has_path}")
    if not has_path:
        # If no path, find which nodes are reachable from start
        reachable = nx.descendants(G, start)
        print(f"Reachable from {start}: {len(reachable)} nodes")
        
        # Check specific bottleneck
        r1a = [r for r in e if '1A' in r['name']][0]
        print(f"Checking 1A sequence for {r1a['name']}:")
        stops = r1a['stops']
        for i in range(len(stops)-1):
            s1, s2 = stops[i], stops[i+1]
            if not G.has_edge(s1, s2):
                print(f"BREAK between '{s1}' and '{s2}'")
                if s1 not in G: print(f"  '{s1}' NOT IN GRAPH")
                if s2 not in G: print(f"  '{s2}' NOT IN GRAPH")
                
        # Let's see if Malioboro 1 is in ANY connected component
        cc = list(nx.connected_components(G))
        print(f"Total Connected Components: {len(cc)}")
        for i, component in enumerate(cc):
            if start in component:
                print(f"Start is in CC {i} (size {len(component)})")
            if dest in component:
                print(f"Dest is in CC {i} (size {len(component)})")
