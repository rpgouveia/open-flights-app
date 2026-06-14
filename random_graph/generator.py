"""
Gerador de grafo direcionado aleatório.

Cria um DirectedGraph com um número fixo de vértices e de arcos, escolhidos
de forma aleatória. Cada arco recebe um peso sorteado dentro de um intervalo
configurável (por exemplo, distâncias em quilômetros).

O gerador evita laços (arco de um vértice para ele mesmo) e arcos duplicados.
Por ser direcionado, o arco i para j é distinto do arco j para i.
"""

import random

from graph_pkg.directed_graph import DirectedGraph


def generate_random_graph(
        num_vertices: int, num_arcs: int,
        min_weight: float = 1.0, max_weight: float = 10000.0,
        seed: int = None
    ) -> DirectedGraph:
    """
    Gera um grafo direcionado aleatório com pesos. O(num_arcs)

    Parâmetros:
        num_vertices: número de vértices do grafo.
        num_arcs: número de arcos a criar (sem laços nem duplicatas).
        min_weight: peso mínimo possível de um arco.
        max_weight: peso máximo possível de um arco.
        seed: semente opcional para tornar a geração reproduzível.

    Cada vértice é rotulado com um identificador do tipo "V0", "V1", etc.
    Os arcos são pares (origem, destino) distintos, com origem diferente de
    destino, e cada um recebe um peso real sorteado em [min_weight, max_weight].

    Retorna a instância de DirectedGraph gerada.

    Levanta ValueError se o número de arcos pedido exceder o máximo possível
    para um grafo direcionado simples, que é num_vertices * (num_vertices - 1).
    """
    if num_vertices < 0:
        raise ValueError("O numero de vertices nao pode ser negativo.")
    if num_arcs < 0:
        raise ValueError("O numero de arcos nao pode ser negativo.")

    # número máximo de arcos num grafo direcionado simples
    max_possible_arcs = num_vertices * (num_vertices - 1)
    if num_arcs > max_possible_arcs:
        raise ValueError(
            f"Arcos demais: pedido {num_arcs}, maximo possivel "
            f"{max_possible_arcs} para {num_vertices} vertices."
        )

    # gerador local de aleatórios
    rng = random.Random(seed)

    graph = DirectedGraph(num_vertices)

    # rotular os vértices
    for index in range(num_vertices):
        graph.update_information(index, f"V{index}")

    # criar arcos únicos até atingir num_arcs
    created_arcs = set()
    while len(created_arcs) < num_arcs:
        origin = rng.randrange(num_vertices)
        destination = rng.randrange(num_vertices)

        # descarta laços e arcos já existentes
        if origin == destination:
            continue
        arc = (origin, destination)
        if arc in created_arcs:
            continue

        created_arcs.add(arc)
        weight = rng.uniform(min_weight, max_weight)
        graph.create_adjacency(origin, destination, weight)

    return graph
