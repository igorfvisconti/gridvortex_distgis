# -*- coding: utf-8 -*-
"""
Modulo de Processamento Topologico e Validacao de Grafos da Rede
"""
import networkx as nx
import pandas as pd

def build_network_graph(gdf_ungraphview, root_pac=None, method='DFS'):
    """
    Constroi o grafo direcionado (DiGraph) da rede de MT/BT a partir de UNGRAPHVIEW.
    Valida conectividade e ordena elementos a partir do PAC inicial do alimentador.
    """
    edges_df = gdf_ungraphview.copy()
    if 'PAC_1' not in edges_df.columns or 'PAC_2' not in edges_df.columns:
        raise ValueError("GeoDataFrame deve conter os barramentos 'PAC_1' e 'PAC_2'")

    edges_df['source'] = edges_df['PAC_1']
    edges_df['target'] = edges_df['PAC_2']

    G = nx.from_pandas_edgelist(
        edges_df,
        source='source',
        target='target',
        edge_attr=True,
        create_using=nx.MultiDiGraph()
    )

    if root_pac and root_pac in G:
        if method == 'DFS':
            dfs_edges = list(nx.dfs_edges(G, source=root_pac))
            sub_nodes = set([root_pac] + [v for u, v in dfs_edges])
            G = G.subgraph(sub_nodes).copy()
        elif method == 'BFS':
            bfs_edges = list(nx.bfs_edges(G, source=root_pac))
            sub_nodes = set([root_pac] + [v for u, v in bfs_edges])
            G = G.subgraph(sub_nodes).copy()

    return G

def clean_dead_leaves(G, sink_nodes):
    """
    Remove ramais e folhas mortas (dead ends) que nao alimentam
    cargas, transformadores MT/BT ou geracao distribuida.
    """
    G_clean = G.copy()
    nodes_to_check = True
    
    while nodes_to_check:
        nodes_to_remove = []
        for node in G_clean.nodes():
            if node not in sink_nodes and G_clean.out_degree(node) == 0:
                nodes_to_remove.append(node)
        if not nodes_to_remove:
            nodes_to_check = False
        else:
            G_clean.remove_nodes_from(nodes_to_remove)

    return G_clean
