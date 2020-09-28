# coding=utf-8
import networkx as nx
import matplotlib.pyplot as plt

import networkx as nx  # pip install networkx
import matplotlib.pyplot as plt  # pip install matplotlib

G = nx.read_shp('E:\\360MoveData\Users\\truekai\\Desktop\\测试graph\\Net3_pipes\\Net3_pipes.shp')  # pip install C:\Software\GDAL-3.0.4-cp38-cp38-win_amd64.whl

print G.nodes


# pos = {k: v for k, v in enumerate(G.nodes())}
# print pos.keys()
# X = nx.Graph()  # Empty graph
# X.add_nodes_from(pos.keys())  # Add nodes preserving coordinates
# l = [set(x) for x in G.edges()]  # To speed things up in case of large objects
# edg = [tuple(k for k, v in pos.items() if v in sl) for sl in l]  # Map the G.edges start and endpoints onto pos
# nx.draw_networkx_nodes(X, pos, node_size=10, node_color='b')
# X.add_edges_from(edg)
# nx.draw_networkx_edges(X, pos)
# plt.xlim(-8232250, -8228920)  # This changes and is problem specific
# plt.ylim(5280000, 5284500)  # This changes and is problem specific
#
# plt.xlabel('X [m]')
# plt.ylabel('Y [m]')
# plt.title('From shapefiles to NetworkX')
# plt.show()
