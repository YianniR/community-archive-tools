from .subgraph_utils import load_data, find_interesting_subgraphs, get_unique_subgraphs
from .visualize import visualize_subgraphs

def thread_explorer_main(args):
    """
    Main function for the Thread Explorer.
    
    Args:
        args: Parsed command-line arguments.
    """
    print("Running Thread Explorer with args:", args)
    
    # Load data
    G, account_names = load_data()
    
    if G.number_of_nodes() == 0:
        print("Error: The graph is empty. Please run the graph builder first.")
        print("You can build the graph by running: python main.py graph")
        return None
    
    # Find interesting subgraphs
    method = args.method if hasattr(args, 'method') else 'size'
    all_subgraphs = find_interesting_subgraphs(G, method=method)
    
    if not all_subgraphs:
        print("No interesting subgraphs found.")
        return None
    
    # Get unique subgraphs
    num_subgraphs = args.num_subgraphs if hasattr(args, 'num_subgraphs') else 20
    interesting_subgraphs = get_unique_subgraphs(all_subgraphs, num_subgraphs)
    
    # Visualize subgraphs
    fig = visualize_subgraphs(G, interesting_subgraphs, account_names, num_to_show=num_subgraphs)
    
    print(f"Thread exploration complete. {len(interesting_subgraphs)} subgraphs visualized.")

    return fig
