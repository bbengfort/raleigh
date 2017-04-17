import graph_tool.all as gt
from numpy import sqrt

g = gt.load_graph('data/tiny_keyphrases.graphml.gz')

def degree_filter(degree=0):
    def inner(vertex):
        return vertex.out_degree() > degree
    return inner

g = gt.GraphView(g, vfilt=degree_filter(3))

gt.graph_draw(g,
    output='images/tiny_keyphrases.png',
)
