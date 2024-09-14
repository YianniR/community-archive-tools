import networkx as nx
from common.utils import load_pickle

from typing import Tuple, Dict
import networkx as nx

def load_data(graph_file: str = 'data/tweet_graph.pkl', account_file: str = 'data/accounts.pkl') -> Tuple[nx.DiGraph, Dict[str, str]]:
    """
    Load graph and account data from pickle files.
    If graph file is not found, create an empty graph.
    
    Returns:
        Tuple[nx.DiGraph, Dict[str, str]]: (NetworkX graph, dict of account names)
    """
    try:
        G = load_pickle(graph_file)
    except FileNotFoundError:
        print(f"Warning: {graph_file} not found. Creating an empty graph.")
        G = nx.DiGraph()
    
    try:
        accounts = load_pickle(account_file)
        account_names = {str(a['account_id']): a.get('username', f"Unknown (ID: {a['account_id']})") for a in accounts}
    except FileNotFoundError:
        print(f"Warning: {account_file} not found. Using an empty account dictionary.")
        account_names = {}
    
    return G, account_names

def find_interesting_subgraphs(G, method='size', min_chain_length=5, min_component_size=10, min_size=5, max_size=100):
    """
    Find interesting subgraphs in the given graph.
    
    Args:
        G (nx.Graph): Input graph
        method (str): Method to use for finding subgraphs ('size', 'branching', or 'influence')
        min_chain_length (int): Minimum chain length for 'size' method
        min_component_size (int): Minimum component size for 'size' method
        min_size (int): Minimum subgraph size for 'branching' method
        max_size (int): Maximum subgraph size for 'branching' method
    
    Returns:
        list: List of interesting subgraphs
    """
    if method == 'influence':
        def influence_score(subgraph):
            return sum(subgraph.out_degree(node) for node in subgraph)
        
        components = list(nx.weakly_connected_components(G))
        interesting_components = [
            c for c in components 
            if min_size <= len(c) <= max_size
        ]
        return sorted(interesting_components, key=lambda c: influence_score(G.subgraph(c)), reverse=True)
    if method == 'size':
        chains = [set(nx.dfs_preorder_nodes(G, node)) for node in G if G.in_degree(node) == 0]
        chains = [c for c in chains if len(c) >= min_chain_length]
        components = [c for c in nx.weakly_connected_components(G) if len(c) >= min_component_size]
        return sorted(chains + components, key=len, reverse=True)
    elif method == 'branching':
        def branching_factor(subgraph):
            return sum(1 for node in subgraph if subgraph.out_degree(node) > 1) / len(subgraph)
        
        components = list(nx.weakly_connected_components(G))
        interesting_components = [
            c for c in components 
            if min_size <= len(c) <= max_size
        ]
        return sorted(interesting_components, key=lambda c: branching_factor(G.subgraph(c)), reverse=True)
    else:
        raise ValueError("Method must be either 'size' or 'branching'")

def get_unique_subgraphs(subgraphs, num_subgraphs=20):
    """
    Get a list of unique subgraphs from the given subgraphs.
    
    Args:
        subgraphs (list): List of subgraphs
        num_subgraphs (int): Number of unique subgraphs to return
    
    Returns:
        list: List of unique subgraphs
    """
    seen = set()
    unique = []
    for subgraph in subgraphs:
        key = frozenset(subgraph)
        if key not in seen and len(unique) < num_subgraphs:
            unique.append(subgraph)
            seen.add(key)
    return unique
