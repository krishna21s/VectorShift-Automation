from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str = None
    targetHandle: str = None

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

@app.get('/')
def read_root():
    return {'Ping': 'Pong', 'status': 'Backend is running!'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: Pipeline):
    """
    Parse pipeline and return:
    - Number of nodes
    - Number of edges
    - Whether it's a DAG (Directed Acyclic Graph)
    """
    nodes = pipeline.nodes
    edges = pipeline.edges
    
    num_nodes = len(nodes)
    num_edges = len(edges)
    
    # Check if graph is a DAG (no cycles)
    is_dag = check_is_dag(nodes, edges)
    
    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'is_dag': is_dag
    }

def check_is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    """
    Check if the graph is a Directed Acyclic Graph (DAG)
    Uses DFS to detect cycles
    """
    if not nodes:
        return True
    
    # Build adjacency list
    graph = {node.id: [] for node in nodes}
    for edge in edges:
        if edge.source in graph:
            graph[edge.source].append(edge.target)
    
    # Track visited nodes and recursion stack
    visited = set()
    rec_stack = set()
    
    def has_cycle(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        
        # Check all neighbors
        for neighbor in graph.get(node_id, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Cycle detected
                return True
        
        rec_stack.remove(node_id)
        return False
    
    # Check all nodes for cycles
    for node in nodes:
        if node.id not in visited:
            if has_cycle(node.id):
                return False  # Cycle found, not a DAG
    
    return True  # No cycles, it's a DAG
