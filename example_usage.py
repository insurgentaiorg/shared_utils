"""
Example usage of AGEClient with apache_age query functions.

This demonstrates the correct way to use the AGE client and query functions
together, ensuring compatibility between psycopg Connection and the query functions.
"""

from shared_utils.clients.age_client import create_age_client
from shared_utils.queries import apache_age


def example_usage():
    """Example of how to use AGEClient with apache_age functions."""
    
    # Create the AGE client
    age_client = create_age_client()
    
    # Method 1: Using scoped session (recommended)
    print("Method 1: Using scoped session")
    with age_client.scoped_session() as conn:
        graph_name = age_client.get_graph_name()
        
        # Create the graph
        apache_age.create_graph(conn, graph_name)
        
        # Create a node
        node_props = {"name": "John", "age": 30}
        node = apache_age.create_node(conn, graph_name, "Person", node_props)
        print(f"Created node: {node}")
        
        # Find nodes
        found_nodes = apache_age.find_nodes(conn, graph_name, "Person")
        print(f"Found nodes: {found_nodes}")
    
    # Method 2: Using execute_with_graph convenience method
    print("\nMethod 2: Using convenience method")
    result = age_client.execute_with_graph(
        apache_age.find_nodes,
        "Person",
        {"name": "John"}
    )
    print(f"Found nodes with convenience method: {result}")
    
    # Method 3: Using persistent session (caller handles lifecycle)
    print("\nMethod 3: Using persistent session")
    conn = age_client.get_persistent_session()
    try:
        graph_name = age_client.get_graph_name()
        
        # Execute custom cypher query
        cypher_query = "MATCH (n:Person) WHERE n.age > 25 RETURN n"
        results = apache_age.execute_cypher(conn, graph_name, cypher_query)
        print(f"Custom cypher results: {results}")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    example_usage()
