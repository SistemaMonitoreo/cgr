import matplotlib.pyplot as plt
import networkx as nx

# Crear el grafo para el diagrama
G = nx.DiGraph()

# Agregar nodos
nodes = [
    ("Agentes de Recolección", {"color": "skyblue"}),
    ("Servidor Central", {"color": "orange"}),
    ("Base de Datos", {"color": "lightgreen"}),
    ("Red Neuronal", {"color": "pink"}),
    ("Sistema de Alertas", {"color": "lightcoral"}),
    ("Interfaz Web", {"color": "lightblue"}),
    ("Usuarios (Administrador/Técnico)", {"color": "yellow"})
]

# Agregar nodos con colores
for node, attributes in nodes:
    G.add_node(node, **attributes)

# Agregar conexiones
edges = [
    ("Agentes de Recolección", "Servidor Central"),
    ("Servidor Central", "Base de Datos"),
    ("Servidor Central", "Red Neuronal"),
    ("Red Neuronal", "Sistema de Alertas"),
    ("Sistema de Alertas", "Interfaz Web"),
    ("Base de Datos", "Interfaz Web"),
    ("Interfaz Web", "Usuarios (Administrador/Técnico)")
]

G.add_edges_from(edges)

# Colores para los nodos
colors = [data["color"] for _, data in G.nodes(data=True)]

# Dibujar el grafo
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42)  # Layout gráfico
nx.draw(
    G, pos, with_labels=True, node_color=colors, node_size=3000,
    font_size=10, font_weight="bold", edge_color="gray", arrowsize=20
)
plt.title("Diagrama de Arquitectura del Sistema", fontsize=14)
plt.savefig("/diagrama_arquitectura_sistema.png", format="png")
plt.show()
