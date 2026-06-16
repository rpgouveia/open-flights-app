"""
Módulo de gravação de log das medidas de centralidade.

Recebe os dicionários de centralidade já calculados (proximidade e
intermediação) e grava um arquivo de texto legível com duas partes:

    1. Resumo: os top N vértices de cada medida, em tabelas alinhadas.
    2. Completo: todos os vértices avaliados, com as duas medidas lado a lado,
        ordenados pela intermediação.

O módulo apenas formata e grava; o cálculo das centralidades é feito antes,
no grafo, e passado pronto para cá.
"""

from graph_pkg.directed_graph import DirectedGraph


def _format_ranking(graph: DirectedGraph, centrality: dict, top: int,
                    value_format: str) -> list[str]:
    """
    Monta as linhas de uma tabela de ranking para uma medida de centralidade.

    Retorna uma lista de linhas (strings) já alinhadas, da maior para a
    menor centralidade, limitada aos 'top' primeiros vértices.
    """
    ranking = sorted(centrality.items(), key=lambda pair: pair[1], reverse=True)

    lines = []
    lines.append(f"{'Pos':>4}  {'Aeroporto':<12}  {'Valor':>16}")
    lines.append(f"{'-' * 4}  {'-' * 12}  {'-' * 16}")

    for position, (vertex, value) in enumerate(ranking[:top], start=1):
        label = str(graph.vertices[vertex])
        formatted_value = value_format.format(value)
        lines.append(f"{position:>4}  {label:<12}  {formatted_value:>16}")

    return lines


def write_centrality_log(
        graph: DirectedGraph, closeness: dict, betweenness: dict,
        path: str, top: int = 10,
        component_size: int = None
    ) -> None:
    """
    Grava um log de texto com o resumo e a listagem completa das centralidades.

    Parâmetros:
        graph: o grafo, usado para obter os rótulos dos vértices.
        closeness: dicionário {indice: valor} da centralidade de proximidade.
        betweenness: dicionário {indice: valor} da centralidade de intermediação.
        path: caminho do arquivo de log a ser gravado.
        top: quantos vértices exibir no resumo de cada medida.
        component_size: tamanho do componente avaliado (opcional, vai no cabeçalho).
    """
    # vértices avaliados: os que aparecem nos dicionários de centralidade
    evaluated = sorted(
        closeness.keys(),
        key=lambda vertex: betweenness.get(vertex, 0.0),
        reverse=True,
    )

    with open(path, "w", encoding="utf-8") as output_file:
        # cabeçalho
        output_file.write("=" * 60 + "\n")
        output_file.write("Log das medidas de centralidade - OpenFlights\n")
        output_file.write("=" * 60 + "\n")
        output_file.write(f"Vertices avaliados: {len(evaluated)}\n")
        if component_size is not None:
            output_file.write(f"Tamanho do componente: {component_size}\n")
        output_file.write("\n")

        # parte 1: resumo (top N de cada medida)
        output_file.write("-" * 60 + "\n")
        output_file.write(f"RESUMO - Top {top} por proximidade (closeness)\n")
        output_file.write("-" * 60 + "\n")
        for line in _format_ranking(graph, closeness, top, "{:.6f}"):
            output_file.write(line + "\n")
        output_file.write("\n")

        output_file.write("-" * 60 + "\n")
        output_file.write(f"RESUMO - Top {top} por intermediação (betweenness)\n")
        output_file.write("-" * 60 + "\n")
        for line in _format_ranking(graph, betweenness, top, "{:.0f}"):
            output_file.write(line + "\n")
        output_file.write("\n")

        # parte 2: listagem completa (todos os vértices, ordenados por intermediação)
        output_file.write("-" * 60 + "\n")
        output_file.write("COMPLETO - Todos os vértices (ordenado por intermediação)\n")
        output_file.write("-" * 60 + "\n")
        header = f"{'Aeroporto':<12}  {'Proximidade':>14}  {'Intermediação':>14}"
        output_file.write(header + "\n")
        output_file.write(f"{'-' * 12}  {'-' * 14}  {'-' * 14}\n")

        for vertex in evaluated:
            label = str(graph.vertices[vertex])
            close_value = closeness.get(vertex, 0.0)
            between_value = betweenness.get(vertex, 0.0)
            output_file.write(
                f"{label:<12}  {close_value:>14.6f}  {between_value:>14.0f}\n"
            )