"""
Gerador de grafo direcionado aleatório.
"""

import random

from graph_pkg.directed_graph import DirectedGraph


def _random_weight(rng, min_weight: float, max_weight: float) -> float:
    """Sorteia um peso real dentro do intervalo informado."""
    return rng.uniform(min_weight, max_weight)


def _build_connected_skeleton(graph, rng, created_arcs, min_weight, max_weight):
    """
    Cria um esqueleto que torna o grafo fracamente conexo, usando n-1 arcos.

    Conecta os vértices em ordem aleatória: cada novo vértice é ligado a um
    vértice já incluído, escolhido ao acaso. Ignorando a direção, isso forma
    uma árvore geradora que garante a conexidade fraca.
    """
    order = list(range(graph.size))
    rng.shuffle(order)

    # liga cada vértice (a partir do segundo) a um anterior ja conectado
    for position in range(1, len(order)):
        new_vertex = order[position]
        connected_vertex = order[rng.randrange(position)]

        # direção do arco é sorteada para não privilegiar um sentido
        if rng.random() < 0.5:
            origin, destination = new_vertex, connected_vertex
        else:
            origin, destination = connected_vertex, new_vertex

        created_arcs.add((origin, destination))
        weight = _random_weight(rng, min_weight, max_weight)
        graph.create_adjacency(origin, destination, weight)


def generate_random_graph(
        num_vertices: int, num_arcs: int,
        connected: bool = True,
        min_weight: float = 1.0, max_weight: float = 10000.0,
        seed: int = None
    ) -> DirectedGraph:
    """
    Gera um grafo direcionado aleatório com pesos. O(num_arcs)

    Parâmetros:
        num_vertices: número de vértices do grafo.
        num_arcs: número de arcos a criar (sem laços nem duplicatas).
        connected:  se True, garante grafo fracamente conexo;
                    se False, garante grafo desconexo (ao menos 2 componentes).
        min_weight: peso mínimo possível de um arco.
        max_weight: peso máximo possível de um arco.
        seed: semente opcional para tornar a geração reproduzível.

    Cada vértice é rotulado com um identificador do tipo "V0", "V1", etc.
    Cada arco recebe um peso real sorteado em [min_weight, max_weight].

    Retorna a instância de DirectedGraph gerada.

    Levanta ValueError quando os parâmetros são inviáveis:
        - num_arcs maior que o máximo possível num_vertices * (num_vertices - 1);
        - connected=True com num_arcs < num_vertices - 1 (arcos insuficientes
        para conectar todos os vértices);
        - connected=False com num_arcs grande demais para manter a separação
        (deixar um vértice isolado exige no máximo (n-1)*(n-2) arcos).
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

    if connected:
        # para conectar n vertices sao necessarios ao menos n-1 arcos
        if num_vertices >= 1 and num_arcs < num_vertices - 1:
            raise ValueError(
                f"Para um grafo conexo com {num_vertices} vertices sao "
                f"necessarios ao menos {num_vertices - 1} arcos (pedido {num_arcs})."
            )
    else:
        # para manter ao menos um vertice isolado, os arcos devem caber entre
        # os outros n-1 vertices, cujo maximo e (n-1)*(n-2)
        if num_vertices >= 2:
            max_arcs_keeping_isolated = (num_vertices - 1) * (num_vertices - 2)
            if num_arcs > max_arcs_keeping_isolated:
                raise ValueError(
                    f"Arcos demais para um grafo desconexo: pedido {num_arcs}, "
                    f"maximo {max_arcs_keeping_isolated} para manter a separacao "
                    f"com {num_vertices} vertices."
                )

    # gerador local de aleatórios (não interfere no estado global do random)
    rng = random.Random(seed)

    graph = DirectedGraph(num_vertices)

    # rotular os vértices
    for index in range(num_vertices):
        graph.update_information(index, f"V{index}")

    created_arcs = set()

    # define o universo de vértices que podem receber arcos
    if connected:
        # primeiro o esqueleto que garante a conexidade fraca
        if num_vertices >= 2:
            _build_connected_skeleton(
                graph, rng, created_arcs,
                min_weight, max_weight
            )
        allowed_vertices = list(range(num_vertices))
    else:
        # reserva o ultimo vertice como isolado: arcos so entre os demais
        if num_vertices >= 2:
            allowed_vertices = list(range(num_vertices - 1))
        else:
            allowed_vertices = list(range(num_vertices))

    # completa com arcos aleatorios ate atingir num_arcs
    while len(created_arcs) < num_arcs:
        origin = allowed_vertices[rng.randrange(len(allowed_vertices))]
        destination = allowed_vertices[rng.randrange(len(allowed_vertices))]

        # descarta laços e arcos já existentes
        if origin == destination:
            continue
        arc = (origin, destination)
        if arc in created_arcs:
            continue

        created_arcs.add(arc)
        weight = _random_weight(rng, min_weight, max_weight)
        graph.create_adjacency(origin, destination, weight)

    return graph