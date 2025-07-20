from psycopg import sql, Connection, Cursor
from re import compile
from psycopg import AsyncConnection, AsyncCursor

WHITESPACE = compile('\s')

# From apache age official repository
def exec_cypher(conn:Connection, graph_name:str, cypher_stmt:str, cols:list=None, params:tuple=None) ->Cursor :
    if conn == None or conn.closed:
        raise Exception("Connection is not open or is closed")

    cursor:Cursor = conn.cursor()
    #clean up the string for parameter injection
    cypher_stmt = cypher_stmt.replace("\n", "")
    cypher_stmt = cypher_stmt.replace("\t", "")

    # Simple parameter injection for backend-only use
    # (not sql injection safe)
    if params:
        cypher = cypher_stmt % params
    else:
        cypher = cypher_stmt
    
    cypher = cypher.strip()

    # prepate the statement (validates)
    preparedStmt = "SELECT * FROM age_prepare_cypher({graphName},{cypherStmt})"
    cursor = conn.cursor()
    try:
        cursor.execute(sql.SQL(preparedStmt).format(graphName=sql.Literal(graph_name),cypherStmt=sql.Literal(cypher)))
    except SyntaxError as cause:
        conn.rollback()
        raise cause
    except Exception as cause:
        conn.rollback()
        raise Exception("Execution ERR[" + str(cause) +"](" + preparedStmt +")") from cause

    # build and execute the cypher statement
    stmt = build_cypher(graph_name, cypher, cols)
    cursor = conn.cursor()
    try:
        cursor.execute(stmt)
        return cursor
    except SyntaxError as cause:
        conn.rollback()
        raise cause
    except Exception as cause:
        conn.rollback()
        raise Exception("Execution ERR[" + str(cause) +"](" + stmt +")") from cause

# From apache age official repository
def build_cypher(graphName:str, cypherStmt:str, columns:list) ->str:
    if graphName == None:
        raise Exception("Graph name cannot be None")
    
    columnExp=[]
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

# - - - -async 
async def async_exec_cypher(conn:AsyncConnection, graph_name:str, cypher_stmt:str, cols:list=None, params:tuple=None) ->AsyncCursor:
    if conn == None or conn.closed:
        raise Exception("Connection is not open or is closed")

    cursor:AsyncCursor = conn.cursor()
    #clean up the string for parameter injection
    cypher_stmt = cypher_stmt.replace("\n", "")
    cypher_stmt = cypher_stmt.replace("\t", "")

    # Simple parameter injection for backend-only use
    # (not sql injection safe)
    if params:
        cypher = cypher_stmt % params
    else:
        cypher = cypher_stmt
    
    cypher = cypher.strip()

    # prepate the statement (validates)
    preparedStmt = "SELECT * FROM age_prepare_cypher({graphName},{cypherStmt})"
    cursor: AsyncCursor = conn.cursor()
    try:
        await cursor.execute(sql.SQL(preparedStmt).format(graphName=sql.Literal(graph_name),cypherStmt=sql.Literal(cypher)))
    except SyntaxError as cause:
        await conn.rollback()
        raise cause
    except Exception as cause:
        await conn.rollback()
        raise Exception("Execution ERR[" + str(cause) +"](" + preparedStmt +")") from cause

    # build and execute the cypher statement
    stmt = build_cypher(graph_name, cypher, cols)
    cursor: AsyncCursor = conn.cursor()
    try:
        await cursor.execute(stmt)
        return cursor
    except SyntaxError as cause:
        await conn.rollback()
        raise cause
    except Exception as cause:
        await conn.rollback()
        raise Exception("Execution ERR[" + str(cause) +"](" + stmt +")") from cause




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
