#!/usr/bin/env python3
"""
Wizualizacja sieci symboli w "Cierpieniach młodego Wertera"
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches

# Tworzenie grafu
G = nx.Graph()

# Główne symbole (węzły)
symbols = {
    'Werter': {'color': '#1a1a1a', 'size': 3000, 'type': 'postać'},
    'Niebieski płaszcz': {'color': '#4169E1', 'size': 2500, 'type': 'przedmiot'},
    'Żółta kamizelka': {'color': '#FFD700', 'size': 2500, 'type': 'przedmiot'},
    'Listy': {'color': '#8B4513', 'size': 2500, 'type': 'forma'},
    'Natura': {'color': '#228B22', 'size': 2500, 'type': 'motyw'},
    'Burza': {'color': '#4682B4', 'size': 2000, 'type': 'zjawisko'},
    'Osjan': {'color': '#8B008B', 'size': 2000, 'type': 'literatura'},
    'Homer': {'color': '#FF6347', 'size': 2000, 'type': 'literatura'},
    'Pistolety': {'color': '#2F4F4F', 'size': 2500, 'type': 'przedmiot'},
    'Lotta': {'color': '#FF69B4', 'size': 2500, 'type': 'postać'},
    'Albert': {'color': '#696969', 'size': 2000, 'type': 'postać'},
    'Śmierć': {'color': '#000000', 'size': 2500, 'type': 'motyw'},
    'Miłość': {'color': '#DC143C', 'size': 2500, 'type': 'motyw'},
    'Izolacja': {'color': '#483D8B', 'size': 2000, 'type': 'motyw'},
    'Romantyzm': {'color': '#8A2BE2', 'size': 2000, 'type': 'epoka'},
}

# Dodawanie węzłów
for symbol, attrs in symbols.items():
    G.add_node(symbol, **attrs)

# Powiązania (krawędzie)
connections = [
    # Werter jako centrum
    ('Werter', 'Niebieski płaszcz', {'weight': 3, 'meaning': 'tożsamość'}),
    ('Werter', 'Żółta kamizelka', {'weight': 3, 'meaning': 'tożsamość'}),
    ('Werter', 'Listy', {'weight': 3, 'meaning': 'ekspresja'}),
    ('Werter', 'Natura', {'weight': 3, 'meaning': 'lustro emocji'}),
    ('Werter', 'Lotta', {'weight': 3, 'meaning': 'obsesja'}),
    ('Werter', 'Pistolety', {'weight': 3, 'meaning': 'finał'}),
    ('Werter', 'Śmierć', {'weight': 3, 'meaning': 'tragedia'}),
    
    # Symbole modowe
    ('Niebieski płaszcz', 'Żółta kamizelka', {'weight': 3, 'meaning': 'strój'}),
    ('Niebieski płaszcz', 'Romantyzm', {'weight': 2, 'meaning': 'estetyka'}),
    ('Żółta kamizelka', 'Romantyzm', {'weight': 2, 'meaning': 'estetyka'}),
    
    # Natura i emocje
    ('Natura', 'Burza', {'weight': 3, 'meaning': 'intensyfikacja'}),
    ('Burza', 'Miłość', {'weight': 2, 'meaning': 'metafora'}),
    ('Natura', 'Romantyzm', {'weight': 2, 'meaning': 'filozofia'}),
    
    # Literatura
    ('Osjan', 'Homer', {'weight': 2, 'meaning': 'kontrast'}),
    ('Osjan', 'Romantyzm', {'weight': 3, 'meaning': 'wzorzec'}),
    ('Osjan', 'Śmierć', {'weight': 2, 'meaning': 'ciemność'}),
    ('Homer', 'Albert', {'weight': 2, 'meaning': 'racjonalizm'}),
    
    # Trójkąt miłosny
    ('Lotta', 'Albert', {'weight': 3, 'meaning': 'małżeństwo'}),
    ('Lotta', 'Miłość', {'weight': 3, 'meaning': 'obiekt'}),
    ('Albert', 'Pistolety', {'weight': 3, 'meaning': 'ironia'}),
    
    # Izolacja i śmierć
    ('Listy', 'Izolacja', {'weight': 3, 'meaning': 'samotność'}),
    ('Izolacja', 'Śmierć', {'weight': 2, 'meaning': 'konsekwencja'}),
    ('Pistolety', 'Śmierć', {'weight': 3, 'meaning': 'narzędzie'}),
]

# Dodawanie krawędzi
G.add_edges_from([(u, v) for u, v, _ in connections])

# Tworzenie wykresu
plt.figure(figsize=(16, 12))
plt.style.use('seaborn-v0_8-darkgrid')

# Layout - spring layout dla lepszego rozmieszczenia
pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

# Tło
ax = plt.gca()
ax.set_facecolor('#f5f5f5')

# Rysowanie krawędzi
for u, v, attrs in connections:
    x = [pos[u][0], pos[v][0]]
    y = [pos[u][1], pos[v][1]]
    plt.plot(x, y, 'gray', alpha=0.3, linewidth=attrs['weight'], zorder=1)

# Rysowanie węzłów
for node, (x, y) in pos.items():
    attrs = G.nodes[node]
    plt.scatter(x, y, s=attrs['size'], c=attrs['color'], alpha=0.8, 
                edgecolors='black', linewidth=2, zorder=2)

# Dodawanie etykiet
for node, (x, y) in pos.items():
    plt.text(x, y, node, fontsize=12, fontweight='bold', 
             ha='center', va='center', color='white' if node == 'Śmierć' else 'black',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=G.nodes[node]['color'], 
                      alpha=0.7, edgecolor='black'))

# Tytuł i legenda
plt.title('Sieć symboli w "Cierpieniach młodego Wertera"', fontsize=20, fontweight='bold', pad=20)

# Legenda typów symboli
legend_elements = [
    mpatches.Patch(color='#1a1a1a', label='Postaci'),
    mpatches.Patch(color='#4169E1', label='Przedmioty'),
    mpatches.Patch(color='#8B4513', label='Forma literacka'),
    mpatches.Patch(color='#228B22', label='Motywy'),
    mpatches.Patch(color='#8A2BE2', label='Epoka/Styl'),
]
plt.legend(handles=legend_elements, loc='upper right', fontsize=12)

# Dodatkowe informacje
plt.text(0.02, 0.02, 'Grubość linii = siła powiązania\nWielkość węzła = znaczenie symbolu', 
         transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
         bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8))

plt.axis('off')
plt.tight_layout()

# Zapisywanie
plt.savefig('werther_symbol_network.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# Analiza centralizacji
print("\nAnaliza centralizacji symboli:")
print("-" * 40)
centrality = nx.degree_centrality(G)
sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
for symbol, score in sorted_centrality[:5]:
    print(f"{symbol}: {score:.3f}")

print("\nNajsilniejsze powiązania:")
print("-" * 40)
for u, v, attrs in sorted(connections, key=lambda x: x[2]['weight'], reverse=True)[:5]:
    print(f"{u} <-> {v}: {attrs['meaning']}")