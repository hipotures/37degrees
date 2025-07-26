#!/usr/bin/env python3
"""
Symbol Network Visualization for Kafka's "The Trial"
Creates a network diagram showing relationships between symbols
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Create directed graph
G = nx.DiGraph()

# Define symbol categories with colors
symbol_categories = {
    'Core Symbols': {
        'symbols': ['The Court', 'The Law', 'Doors/Thresholds', 'Cathedral Parable'],
        'color': '#FF6B6B',
        'pos_range': [(0, 2), (2, 4)]
    },
    'Character Symbols': {
        'symbols': ['Josef K.', 'Authority Figures', 'Women Characters', 'The Executioners'],
        'color': '#4ECDC4',
        'pos_range': [(4, 2), (6, 4)]
    },
    'Spatial Symbols': {
        'symbols': ['Labyrinth', 'Attic Courtrooms', 'Public/Private Blur', 'Bank vs Court'],
        'color': '#45B7D1',
        'pos_range': [(0, -2), (2, 0)]
    },
    'Thematic Symbols': {
        'symbols': ['Guilt/Innocence', 'Bureaucracy', 'Power/Powerlessness', 'Alienation'],
        'color': '#96CEB4',
        'pos_range': [(4, -2), (6, 0)]
    }
}

# Add nodes with attributes
pos = {}
node_colors = []
for category, data in symbol_categories.items():
    x_min, x_max = data['pos_range'][0]
    y_min, y_max = data['pos_range'][1]
    for i, symbol in enumerate(data['symbols']):
        G.add_node(symbol, category=category)
        # Distribute nodes within category range
        x = np.linspace(x_min, x_max, len(data['symbols']))[i]
        y = np.linspace(y_min, y_max, len(data['symbols']))[i]
        pos[symbol] = (x, y)
        node_colors.append(data['color'])

# Define relationships (edges)
relationships = [
    # Core to Character
    ('The Court', 'Authority Figures', 'embodies'),
    ('The Law', 'Josef K.', 'seeks access to'),
    ('Doors/Thresholds', 'Josef K.', 'confronts'),
    ('Cathedral Parable', 'Josef K.', 'mirrors'),
    
    # Core to Spatial
    ('The Court', 'Attic Courtrooms', 'manifests in'),
    ('The Law', 'Labyrinth', 'structured as'),
    ('Doors/Thresholds', 'Public/Private Blur', 'creates'),
    
    # Core to Thematic
    ('The Court', 'Bureaucracy', 'represents'),
    ('The Law', 'Power/Powerlessness', 'enforces'),
    ('Cathedral Parable', 'Guilt/Innocence', 'questions'),
    
    # Character to Spatial
    ('Josef K.', 'Labyrinth', 'navigates'),
    ('Authority Figures', 'Attic Courtrooms', 'inhabit'),
    ('Women Characters', 'Public/Private Blur', 'exist in'),
    
    # Character to Thematic
    ('Josef K.', 'Alienation', 'experiences'),
    ('Authority Figures', 'Power/Powerlessness', 'wield'),
    ('The Executioners', 'Guilt/Innocence', 'enforce'),
    
    # Spatial to Thematic
    ('Labyrinth', 'Alienation', 'creates'),
    ('Attic Courtrooms', 'Bureaucracy', 'houses'),
    ('Bank vs Court', 'Power/Powerlessness', 'contrasts'),
]

# Add edges
for source, target, label in relationships:
    G.add_edge(source, target, label=label)

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_title("Symbol Network in Kafka's 'The Trial'", fontsize=20, fontweight='bold', pad=20)

# Draw category backgrounds
for category, data in symbol_categories.items():
    x_min, x_max = data['pos_range'][0]
    y_min, y_max = data['pos_range'][1]
    rect = FancyBboxPatch((x_min-0.5, y_min-0.5), 
                          x_max-x_min+1, y_max-y_min+1,
                          boxstyle="round,pad=0.1",
                          facecolor=data['color'],
                          alpha=0.1,
                          edgecolor=data['color'],
                          linewidth=2)
    ax.add_patch(rect)
    ax.text((x_min+x_max)/2, y_max+0.3, category, 
            fontsize=12, fontweight='bold', 
            ha='center', color=data['color'])

# Draw network
nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                      node_size=3000, alpha=0.9, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
nx.draw_networkx_edges(G, pos, edge_color='gray', 
                      arrows=True, arrowsize=20, 
                      alpha=0.6, arrowstyle='->', ax=ax)

# Draw edge labels
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                           font_size=8, alpha=0.7, ax=ax)

# Add legend
legend_elements = []
for category, data in symbol_categories.items():
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                    label=category, markersize=10, 
                                    markerfacecolor=data['color']))
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))

# Adjust layout
ax.set_xlim(-1, 7)
ax.set_ylim(-3, 5)
ax.axis('off')
plt.tight_layout()

# Save the figure
plt.savefig('/home/xai/DEV/37degrees/books/0033_the_trial/docs/symbol_network.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Create a second visualization for youth-relevant connections
fig2, ax2 = plt.subplots(1, 1, figsize=(14, 10))
ax2.set_title("Modern Youth Relevance of Kafka's Symbols", fontsize=18, fontweight='bold', pad=20)

# Modern parallels graph
M = nx.Graph()

# Classic symbols and their modern equivalents
modern_parallels = {
    'The Court': ['Social Media Judgment', 'Cancel Culture', 'Online Mob'],
    'The Law': ['Terms of Service', 'Community Guidelines', 'Algorithmic Rules'],
    'Josef K.': ['Canceled Individual', 'Digital Native', 'Online User'],
    'Authority Figures': ['Platform Moderators', 'Influencers', 'Tech Companies'],
    'Labyrinth': ['Internet Rabbit Holes', 'Bureaucratic Websites', 'Support Systems'],
    'Surveillance': ['Data Collection', 'Digital Tracking', 'Privacy Invasion'],
    'Guilt/Innocence': ['Public Shaming', 'Viral Mistakes', 'Context Collapse'],
    'Alienation': ['Digital Isolation', 'FOMO', 'Echo Chambers']
}

# Position nodes in two columns
classic_pos = {}
modern_pos = {}
y_offset = 0

for classic, moderns in modern_parallels.items():
    # Classic symbol on the left
    M.add_node(classic, node_type='classic')
    classic_pos[classic] = (0, y_offset)
    
    # Modern equivalents on the right
    for i, modern in enumerate(moderns):
        M.add_node(modern, node_type='modern')
        modern_pos[modern] = (4, y_offset + (i-1)*0.3)
        M.add_edge(classic, modern)
    
    y_offset -= 1.2

# Combine positions
all_pos = {**classic_pos, **modern_pos}

# Draw nodes
classic_nodes = [n for n in M.nodes() if M.nodes[n].get('node_type') == 'classic']
modern_nodes = [n for n in M.nodes() if M.nodes[n].get('node_type') == 'modern']

nx.draw_networkx_nodes(M, all_pos, nodelist=classic_nodes, 
                      node_color='#FF6B6B', node_size=3000, alpha=0.9, ax=ax2)
nx.draw_networkx_nodes(M, all_pos, nodelist=modern_nodes, 
                      node_color='#4ECDC4', node_size=2000, alpha=0.9, ax=ax2)

# Draw edges and labels
nx.draw_networkx_edges(M, all_pos, edge_color='gray', alpha=0.5, ax=ax2)
nx.draw_networkx_labels(M, all_pos, font_size=10, font_weight='bold', ax=ax2)

# Add column headers
ax2.text(0, 1, 'Kafka\'s Symbols', fontsize=14, fontweight='bold', 
        ha='center', transform=ax2.transData)
ax2.text(4, 1, 'Modern Youth Parallels', fontsize=14, fontweight='bold', 
        ha='center', transform=ax2.transData)

# Adjust layout
ax2.set_xlim(-1.5, 5.5)
ax2.set_ylim(-10, 2)
ax2.axis('off')
plt.tight_layout()

# Save the second figure
plt.savefig('/home/xai/DEV/37degrees/books/0033_the_trial/docs/modern_relevance_network.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print("Symbol network visualizations created successfully!")
print("- symbol_network.png: Shows relationships between all symbols")
print("- modern_relevance_network.png: Shows modern youth parallels")