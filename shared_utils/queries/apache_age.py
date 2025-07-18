from typing import Optional, Dict, Any, List
from psycopg import Connection
from psycopg.cursor import Cursor
from psycopg.sql import SQL, Literal
from re import compile

WHITESPACE = compile('\s')

# From apache age official repository
def execute_cypher(conn:Connection, graphName:str, cypherStmt:str, cols:list=None, params:tuple=None) -> Cursor :
    if conn == None or conn.closed:
        raise Exception("Connection is closed or None")

    cursor = conn.cursor()
    #clean up the string for mogrification
    cypherStmt = cypherStmt.replace("\n", "")
    cypherStmt = cypherStmt.replace("\t", "")
    cypher = str(cursor.mogrify(cypherStmt, params))
    cypher = cypher.strip()

    preparedStmt = "SELECT * FROM age_prepare_cypher({graphName},{cypherStmt})"

    cursor = conn.cursor()
    try:
        cursor.execute(SQL(preparedStmt).format(graphName=Literal(graphName),cypherStmt=Literal(cypher)))
    except SyntaxError as cause:
        conn.rollback()
        raise cause
    except Exception as cause:
        conn.rollback()
        raise Exception(f"Execution error: {cause}\nQuery: {preparedStmt}") from cause

    stmt = _build_cypher(graphName, cypher, cols)

    cursor = conn.cursor()
    try:
        cursor.execute(stmt)
        return cursor
    except SyntaxError as cause:
        conn.rollback()
        raise cause
    except Exception as cause:
        conn.rollback()
        raise Exception(f"Execution error: {cause}\nQuery: {stmt}") from cause

# From apache age official repository
def _build_cypher(graphName: str, cypherStmt: str, columns: list) -> str:
    if graphName == None:
        raise Exception("Graph name cannot be None")

    columnExp = []
    if columns != None and len(columns) > 0:
        for col in columns:
            if col.strip() == '':
                continue
            elif WHITESPACE.search(col) != None:
                columnExp.append(col)
            else:
                columnExp.append(col + " agtype")
    else:
        columnExp.append('v agtype')

    stmtArr = []
    stmtArr.append("SELECT * from cypher(NULL,NULL) as (")
    stmtArr.append(','.join(columnExp))
    stmtArr.append(");")
    return "".join(stmtArr)


# AGE-specific operations
# def execute_cypher(conn: Connection, graph_name: str, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
#     """Execute a Cypher query and return results."""
#     # Prepare the AGE query
#     if params: 
#         query = query % tuple(map(lambda v: f"'{v}'" if isinstance(v, str) else v, params))
    
#     cypher_sql = sql.SQL(
#         "SELECT * FROM cypher({}, $$ {} $$) as (result agtype);"
#     ).format(
#         sql.Literal(graph_name),
#         sql.SQL(query)
#     )

#     # age_query = f"SELECT * FROM cypher('{graph_name}', $${query}$$) as (result agtype);"


#     with conn.cursor() as cur:
#         cur.execute(cypher_sql, params or {})
#         return cur.fetchall()


def graph_exists(conn: Connection, graph_name: str) -> bool:
    """Check if the AGE graph with the given name exists."""
    try:
        query = f"SELECT * FROM ag_graph WHERE name = '{graph_name}';"
        with conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchone()
            return result is not None
    except Exception:
        # If there's an error (e.g., ag_graph table doesn't exist), assume graph doesn't exist
        return False


def create_graph(conn: Connection, graph_name: str) -> bool:
    """Create the AGE graph if it doesn't exist."""
    try:
        query = f"SELECT create_graph('{graph_name}');"
        with conn.cursor() as cur:
            cur.execute(query)
        return True
    except Exception:
        # Graph might already exist
        return False


def drop_graph(conn: Connection, graph_name: str) -> bool:
    """Drop the AGE graph."""
    try:
        query = f"SELECT drop_graph('{graph_name}', true);"
        with conn.cursor() as cur:
            cur.execute(query)
        return True
    except Exception:
        return False
