#!/usr/bin/env python3
"""Create visual symbol diagrams for To Kill a Mockingbird analysis"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

# Ensure output directory exists
output_dir = "/home/xai/DEV/37degrees/books/0034_to_kill_a_mockingbird/docs"
os.makedirs(output_dir, exist_ok=True)

# 1. Mockingbird Symbol Network
def create_mockingbird_network():
    # Create graph
    G = nx.Graph()

    # Main node
    G.add_node("DROZD", size=3000, color='gold')

    # Mockingbird traits
    traits = ["Niewinność", "Piękno", "Bezinteresowność", "Bezbronność", "Radość"]
    for trait in traits:
        G.add_node(trait, size=1500, color='lightblue')
        G.add_edge("DROZD", trait)

    # Characters as mockingbirds
    characters = ["Tom Robinson", "Boo Radley", "Scout", "Jem"]
    for char in characters:
        G.add_node(char, size=2000, color='lightgreen')
        G.add_edge("DROZD", char)

    # Modern parallels
    modern = ["Cancel culture", "Cyberbullying", "Hejt online", "Wykluczenie"]
    for m in modern:
        G.add_node(m, size=1200, color='lightcoral')
        G.add_edge("DROZD", m)

    # Drawing
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, k=3, iterations=50)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, 
                          node_size=[G.nodes[node].get('size', 1000) for node in G.nodes()],
                          node_color=[G.nodes[node].get('color', 'gray') for node in G.nodes()],
                          alpha=0.8)

    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=2)

    # Labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    plt.title("Sieć symboliczna DROZDA w 'Zabić drozda'", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mockingbird_symbol_network.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("Created: mockingbird_symbol_network.png")

# 2. Radley Tree Timeline
def create_tree_timeline():
    fig, ax = plt.subplots(figsize=(12, 8))

    # Items in tree
    items = [
        ("Guma do żucia", 1, "Pierwsza próba kontaktu"),
        ("Figurki z mydła", 2, "Personalizowane prezenty"),
        ("Zegarek kieszonkowy", 3, "Cenny dar osobisty"),
        ("Medal", 4, "Uznanie odwagi"),
        ("Nożyk", 5, "Symbol zaufania"),
        ("CEMENT", 6, "Koniec komunikacji")
    ]

    colors = ['lightgreen', 'lightblue', 'gold', 'silver', 'orange', 'red']

    for i, (item, pos, desc) in enumerate(items):
        if item == "CEMENT":
            ax.scatter(pos, 1, s=500, c=colors[i], marker='X', linewidth=3)
        else:
            ax.scatter(pos, 1, s=300, c=colors[i], alpha=0.8)
        
        ax.annotate(item, (pos, 1), xytext=(pos, 1.2), 
                    ha='center', fontsize=10, fontweight='bold')
        ax.annotate(desc, (pos, 1), xytext=(pos, 0.8), 
                    ha='center', fontsize=8, style='italic')

    # Timeline
    ax.plot([0.5, 6.5], [1, 1], 'k--', alpha=0.3)

    ax.set_xlim(0, 7)
    ax.set_ylim(0.5, 1.5)
    ax.set_title("Drzewo Radleyów: Od komunikacji do cenzury", fontsize=14, fontweight='bold')
    ax.axis('off')

    # Legend
    legend_text = "Drzewo = Miejsce wymiany\nX = Zablokowana komunikacja"
    ax.text(3.5, 0.6, legend_text, ha='center', fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'radley_tree_timeline.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("Created: radley_tree_timeline.png")

# 3. Character Symbolism Map
def create_character_symbolism():
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Character positions and their symbolic meanings
    characters = {
        'Atticus Finch': {'pos': (0.5, 0.8), 'symbol': 'Moralny kompas', 'color': 'navy'},
        'Tom Robinson': {'pos': (0.2, 0.5), 'symbol': 'Kozioł ofiarny', 'color': 'darkred'},
        'Boo Radley': {'pos': (0.8, 0.5), 'symbol': 'Niezrozumiany outsider', 'color': 'purple'},
        'Scout': {'pos': (0.3, 0.2), 'symbol': 'Niewinna perspektywa', 'color': 'pink'},
        'Jem': {'pos': (0.7, 0.2), 'symbol': 'Utracona niewinność', 'color': 'orange'},
        'Mrs. Dubose': {'pos': (0.5, 0.35), 'symbol': 'Nieoczekiwana odwaga', 'color': 'green'}
    }
    
    # Draw connections
    connections = [
        ('Atticus Finch', 'Scout'), ('Atticus Finch', 'Jem'),
        ('Tom Robinson', 'Atticus Finch'), ('Boo Radley', 'Scout'),
        ('Boo Radley', 'Jem'), ('Mrs. Dubose', 'Jem')
    ]
    
    for start, end in connections:
        x_vals = [characters[start]['pos'][0], characters[end]['pos'][0]]
        y_vals = [characters[start]['pos'][1], characters[end]['pos'][1]]
        ax.plot(x_vals, y_vals, 'gray', alpha=0.3, linewidth=2)
    
    # Draw characters
    for name, info in characters.items():
        circle = plt.Circle(info['pos'], 0.08, color=info['color'], alpha=0.7)
        ax.add_patch(circle)
        ax.text(info['pos'][0], info['pos'][1], name.split()[0], 
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        ax.text(info['pos'][0], info['pos'][1]-0.12, info['symbol'], 
                ha='center', va='center', fontsize=8, style='italic')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Mapa symbolizmu postaci", fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'character_symbolism_map.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("Created: character_symbolism_map.png")

# 4. Modern Parallels Visualization
def create_modern_parallels():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))
    
    # Left side: Original symbols
    original = ['Drozd', 'Drzewo Radleyów', 'Gmach sądu', 'Kostium szynki', 'Zegarek']
    modern = ['Cancel culture victim', 'Blocked social media', 'Biased algorithms', 'Cringe protection', 'Inherited trauma']
    
    y_positions = np.arange(len(original))
    
    # Original symbols
    ax1.barh(y_positions, [1]*len(original), color='lightblue', alpha=0.7)
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels(original)
    ax1.set_xlabel('Oryginalne symbole', fontsize=12, fontweight='bold')
    ax1.set_xlim(0, 1.2)
    ax1.axis('off')
    
    for i, label in enumerate(original):
        ax1.text(0.5, i, label, ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Modern parallels
    ax2.barh(y_positions, [1]*len(modern), color='lightcoral', alpha=0.7)
    ax2.set_yticks(y_positions)
    ax2.set_yticklabels(modern)
    ax2.set_xlabel('Współczesne paralele', fontsize=12, fontweight='bold')
    ax2.set_xlim(0, 1.2)
    ax2.axis('off')
    
    for i, label in enumerate(modern):
        ax2.text(0.5, i, label, ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Draw arrows
    for i in range(len(original)):
        ax1.annotate('', xy=(1.1, i), xytext=(0.9, i),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2))
    
    plt.suptitle("Symbole wczoraj i dziś", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'modern_parallels.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("Created: modern_parallels.png")

# 5. Thematic Symbols Web
def create_thematic_web():
    # Create circular layout for themes
    G = nx.Graph()
    
    # Central theme
    G.add_node("SPRAWIEDLIWOŚĆ", size=3000, color='gold')
    
    # Main themes
    themes = {
        "Niewinność": ['Scout', 'Jem', 'Dill', 'Drozd'],
        "Odwaga": ['Atticus', 'Mrs. Dubose', 'Boo'],
        "Uprzedzenia": ['Bob Ewell', 'Mieszkańcy', 'Jury'],
        "Edukacja": ['Szkoła', 'Życie', 'Atticus'],
        "Klasa społeczna": ['Finchowie', 'Ewellowie', 'Czarni mieszkańcy']
    }
    
    # Add nodes and edges
    for theme, elements in themes.items():
        G.add_node(theme, size=2000, color='lightblue')
        G.add_edge("SPRAWIEDLIWOŚĆ", theme)
        for element in elements:
            G.add_node(element, size=1000, color='lightgreen')
            G.add_edge(theme, element)
    
    plt.figure(figsize=(14, 12))
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Draw
    nx.draw_networkx_nodes(G, pos,
                          node_size=[G.nodes[node].get('size', 800) for node in G.nodes()],
                          node_color=[G.nodes[node].get('color', 'gray') for node in G.nodes()],
                          alpha=0.7)
    
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=1.5)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    
    plt.title("Sieć tematów i symboli", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'thematic_symbols_web.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("Created: thematic_symbols_web.png")

# Run all visualizations
if __name__ == "__main__":
    print("Creating symbol visualizations for 'To Kill a Mockingbird'...")
    create_mockingbird_network()
    create_tree_timeline()
    create_character_symbolism()
    create_modern_parallels()
    create_thematic_web()
    print("All visualizations created successfully!")