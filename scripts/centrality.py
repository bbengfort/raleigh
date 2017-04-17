#!/usr/bin/env python3

import sys
import time
import heapq
import argparse
import networkx as nx

from operator import itemgetter

sys.path.append("..")
from raleigh.notify import notify


def nbest_centrality(G, metric, n=10, attr="centrality", **kwargs):
    # Compute the centrality scores for each vertex
    scores = metric(G, **kwargs)

    # Set the score as a property on each node
    # nx.set_node_attributes(G, attr, scores)

    # Filter scores (do not include in book)
    ntypes = nx.get_node_attributes(G, 'type')
    phrases = [
        item for item in scores.items()
        if ntypes.get(item[0], None) == "keyphrase"
    ]

    # Find the top n scores and print them along with their index
    topn = heapq.nlargest(n, phrases, key=itemgetter(1))
    output = []
    for idx, item in enumerate(topn):
        output.append("{}. {}: {:0.4f}".format(idx+1, *item))

    return "\n".join(output)


def compute_centrality(graphml, metric, n=25, recipient=None):
    start = time.time()
    metric_func = {
        "degree": nx.degree_centrality,
        "betweenness": nx.betweenness_centrality,
        "closeness": nx.closeness_centrality,
        "eigenvector": nx.eigenvector_centrality,
        "katz": nx.katz_centrality,
    }[metric]

    G = nx.read_graphml(graphml)
    output = nbest_centrality(G, metric_func, n)
    delta = time.time() - start

    if recipient:
        subject = "{} centrality computation finished".format(metric)
        message = output + "\n\nFinished in {:0.3f} seconds".format(delta)
        notify(recipient, subject, message)

    else:
        print(output)
        print("\nFinished in {:0.3f} seconds".format(delta))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--metric', help='metric to compute')
    parser.add_argument('-n', '--notify', help='email address to notify on complete')
    parser.add_argument('-t', '--topn', type=int, help='fetch top n results')
    parser.add_argument('graph', nargs=1, help='location on disk of graphml')
    args = parser.parse_args()

    compute_centrality(args.graph[0], args.metric, args.topn, args.notify)
