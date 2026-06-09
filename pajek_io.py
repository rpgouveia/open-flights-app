"""
Módulo de gravação e carregamento de grafo em formato Pajek.

O formato Pajek representa um grafo direcionado em duas seções:
    *Vertices N      lista os N vértices, cada um com índice (base 1) e rótulo
    *Arcs            conexões direcionadas (origem destino peso)

Como o pacote de grafos usa índices baseados em 0 e o Pajek usa índices
baseados em 1, este módulo soma 1 a cada índice na gravação e subtrai 1
no carregamento.
"""

from graph_pkg import DirectedGraph


def _format_label(label) -> str:
    """
    Formata o rótulo de um vértice para o padrão Pajek (entre aspas duplas).
    Caso o rótulo contenha aspas, elas são substituídas por aspas simples.
    """
    text = str(label)
    text = text.replace('"', "'")
    return f'"{text}"'


def write_pajek(graph: DirectedGraph, path: str):
    """
    Grava o grafo direcionado no arquivo indicado usando o formato Pajek.

    Escreve a seção *Vertices com os rótulos e a seção *Arcs com cada
    arco no formato origem destino peso (índices em base 1).
    """
    with open(path, "w", encoding="utf-8") as output_file:
        # Seção de vértices
        output_file.write(f"*Vertices {graph.size}\n")
        for index in range(graph.size):
            label = _format_label(graph.vertices[index])
            # converte índice base 0 para base 1
            output_file.write(f"{index + 1} {label}\n")

        # Seção de arcos
        output_file.write("*Arcs\n")
        for origin in range(graph.size):
            for node in graph.adjacency_list[origin]:
                destination = node.destination
                weight = node.weight
                output_file.write(f"{origin + 1} {destination + 1} {weight}\n")


def _parse_vertex_line(line: str) -> tuple[int, str]:
    """
    Interpreta uma linha da seção *Vertices.
    Formato esperado: indice "rotulo"
    Retorna (indice_base_0, rotulo).
    """
    line = line.strip()
    first_space = line.find(" ")
    if first_space == -1:
        # linha com apenas o índice, sem rótulo
        return int(line) - 1, ""

    index = int(line[:first_space]) - 1
    remainder = line[first_space + 1:].strip()

    # remove aspas duplas do rótulo, se houver
    if remainder.startswith('"') and remainder.endswith('"') and len(remainder) >= 2:
        label = remainder[1:-1]
    else:
        label = remainder

    return index, label


def _parse_arc_line(line: str) -> tuple[int, int, float]:
    """
    Interpreta uma linha da seção *Arcs.
    Formato esperado: origem destino peso
    O peso é opcional; quando ausente, assume 1.0.
    Retorna (origem_base_0, destino_base_0, peso).
    """
    parts = line.split()
    origin = int(parts[0]) - 1
    destination = int(parts[1]) - 1
    weight = float(parts[2]) if len(parts) >= 3 else 1.0
    return origin, destination, weight


def read_pajek(path: str) -> DirectedGraph:
    """
    Carrega um grafo direcionado a partir de um arquivo no formato Pajek.

    Lê a seção *Vertices para os rótulos e a seção *Arcs para os arcos.
    O peso é sempre interpretado como float. Os índices são convertidos
    de base 1 (Pajek) para base 0 (pacote de grafos).

    Retorna a instância de DirectedGraph carregada.
    """
    vertices = []     # lista de (indice, rotulo)
    arcs = []         # lista de (origem, destino, peso)
    section = None    # seção atual sendo lida

    with open(path, "r", encoding="utf-8") as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            if not line:
                continue

            lowered = line.lower()
            if lowered.startswith("*vertices"):
                section = "vertices"
                continue
            if lowered.startswith("*arcs"):
                section = "arcs"
                continue

            if section == "vertices":
                vertices.append(_parse_vertex_line(line))
            elif section == "arcs":
                arcs.append(_parse_arc_line(line))

    size = len(vertices)
    graph = DirectedGraph(size)

    # aplica os rótulos
    for index, label in vertices:
        if 0 <= index < size:
            graph.update_information(index, label)

    # cria os arcos
    for origin, destination, weight in arcs:
        graph.create_adjacency(origin, destination, weight)

    return graph