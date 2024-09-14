import networkx as nx
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import textwrap
import math

def count_branches(subgraph):
    """Count the number of branches in a subgraph."""
    return sum(1 for node in subgraph if subgraph.out_degree(node) > 1)

def custom_layout(G, iterations=10):
    """
    Create a combined layout for the graph using spectral and force-directed algorithms.
    
    Args:
        G (nx.Graph): Input graph
        iterations (int): Number of iterations for force-directed algorithm
    
    Returns:
        dict: Node positions
    """
    pos = nx.spectral_layout(G)
    pos = nx.fruchterman_reingold_layout(G, pos=pos, iterations=iterations)
    return pos

def visualize_subgraphs(G, subgraphs, account_names, num_to_show=20):
    """
    Visualize interesting subgraphs using Plotly.
    
    Args:
        G (nx.Graph): Full graph
        subgraphs (list): List of subgraphs to visualize
        account_names (dict): Mapping of account IDs to usernames
        num_to_show (int): Number of subgraphs to visualize
    
    Returns:
        plotly.graph_objs._figure.Figure: The Plotly figure object
    """
    grid_size = math.ceil(math.sqrt(num_to_show))
    fig = make_subplots(rows=grid_size, cols=grid_size, subplot_titles=[f"Subgraph {i+1}" for i in range(num_to_show)])

    for i, subgraph_nodes in enumerate(subgraphs[:num_to_show]):
        subgraph = G.subgraph(subgraph_nodes)
        row = i // grid_size + 1
        col = i % grid_size + 1
        
        root_tweet = next(node for node in subgraph if subgraph.in_degree(node) == 0)
        node_data = G.nodes[root_tweet]
        account_id = str(node_data.get('account_id', 'Unknown'))
        author = account_names.get(account_id, f"Unknown (ID: {account_id})")
        text = node_data.get('full_text', 'No text available')

        pos = custom_layout(subgraph)
        
        edge_x = []
        edge_y = []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = [pos[node][0] for node in subgraph.nodes()]
        node_y = [pos[node][1] for node in subgraph.nodes()]

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                colorscale='YlGnBu',
                size=10,
                color=[],
                line_width=2))

        node_adjacencies = []
        node_text = []
        for node in subgraph.nodes():
            node_adjacencies.append(len(list(subgraph.neighbors(node))))
            node_text.append(f'Node: {node}<br>Connections: {len(list(subgraph.neighbors(node)))}')

        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text

        fig.add_trace(edge_trace, row=row, col=col)
        fig.add_trace(node_trace, row=row, col=col)

        num_branches = count_branches(subgraph)
        title = f"Subgraph {i+1} ({len(subgraph_nodes)} nodes, {num_branches} branches)<br>Author: {author}<br>"
        title += textwrap.fill(text, width=40)
        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, row=row, col=col)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=row, col=col)

    fig.update_layout(showlegend=False, title_text="Tweet Subgraphs Visualization", height=1000, width=1000)
    return fig
