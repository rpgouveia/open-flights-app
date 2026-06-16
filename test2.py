"""
Script de teste com os dados reais do OpenFlights.

Carrega os aeroportos e rotas, mostra as estatísticas do grafo,
grava em formato Pajek e verifica a conexidade.
"""

import time

from graph_pkg.directed_graph import DirectedGraph
from pajek import write_pajek
from openflights import build_graph
from centrality_log import write_centrality_log


# caminhos dos arquivos de dados
AIRPORTS_PATH = "dataset/airports.dat"
ROUTES_PATH = "dataset/routes.dat"


def _imprimir_top(grafo, centrality: dict, nome: str, formato: str, top: int = 10):
    """Imprime os top vértices de uma medida de centralidade ja calculada."""
    ranking = sorted(centrality.items(), key=lambda par: par[1], reverse=True)
    print(f"Top {top} vértices por centralidade de {nome}:")
    for posicao, (vertice, valor) in enumerate(ranking[:top], start=1):
        rotulo = grafo.vertices[vertice]
        print(f"  {posicao:>2}. {rotulo}: {formato.format(valor)}")


def contar_arcos(grafo: DirectedGraph) -> int:
    """Conta o total de arcos do grafo."""
    return sum(len(grafo.adjacency_list[i]) for i in range(grafo.size))


def main():
    print("=" * 55)
    print("Dados reais do OpenFlights")
    print("=" * 55)

    # carregamento dos dados
    print("\nCarregando aeroportos e rotas...")
    inicio = time.time()
    grafo, id_to_index, _ = build_graph(AIRPORTS_PATH, ROUTES_PATH)
    tempo = time.time() - inicio
    print(f"Grafo construido em {tempo:.2f}s")

    # estatísticas
    total_arcos = contar_arcos(grafo)
    print(f"\nNos (aeroportos): {grafo.size}")
    print(f"Arcos (rotas): {total_arcos}")

    nos_ok = "ATENDE" if grafo.size >= 5000 else "NAO ATENDE"
    arcos_ok = "ATENDE" if total_arcos >= 20000 else "NAO ATENDE"
    print(f"\nRequisito mínimo de 5000 nos: {nos_ok} ({grafo.size})")
    print(f"Requisito mínimo de 20000 arcos: {arcos_ok} ({total_arcos})")

    # gravação em Pajek
    caminho = "openflights.net"
    print(f"\nGravando grafo completo em '{caminho}'...")
    inicio = time.time()
    write_pajek(grafo, caminho)
    tempo = time.time() - inicio
    print(f"Arquivo gravado em {tempo:.2f}s")

    # conexidade
    print("\nVerificando conexidade do grafo real...")
    inicio = time.time()
    grafo.is_connected()
    tempo = time.time() - inicio
    print(f"Verificacao concluida em {tempo:.2f}s")
    grafo.print_connectivity()

    # componentes fracamente conectados
    print("\nIdentificando componentes fracamente conectados...")
    inicio = time.time()
    grafo.print_connected_components()
    tempo = time.time() - inicio
    print(f"\nAnálise de componentes concluída em {tempo:.2f}s")

    # caminho euleriano
    print("\nVerificando existencia de caminho euleriano...")
    inicio = time.time()
    grafo.has_eulerian_path()
    tempo = time.time() - inicio
    print(f"Verificacao concluida em {tempo:.2f}s")
    grafo.print_eulerian_path()

    # ciclicidade
    print("\nVerificando existencia de ciclo...")
    inicio = time.time()
    grafo.is_cyclic()
    tempo = time.time() - inicio
    print(f"Verificacao concluida em {tempo:.2f}s")
    grafo.print_cyclic()

    # centralidades (calculadas sobre o maior componente)
    print("\n" + "=" * 55)
    print("Medidas de centralidade (maior componente)")
    print("=" * 55)

    comps = grafo.connected_components()
    comps.sort(key=len, reverse=True)
    maior_componente = comps[0]
    print(f"\nMaior componente: {len(maior_componente)} aeroportos")
    print("(o calculo leva algumas dezenas de segundos)")

    print("\nCalculando centralidade de proximidade...")
    inicio = time.time()
    closeness = grafo.closeness_centrality(vertices=maior_componente)
    tempo = time.time() - inicio
    _imprimir_top(grafo, closeness, "proximidade", "{:.6f}", top=10)
    print(f"Concluido em {tempo:.1f}s")

    print("\nCalculando centralidade de intermediação...")
    inicio = time.time()
    betweenness = grafo.betweenness_centrality(vertices=maior_componente)
    tempo = time.time() - inicio
    _imprimir_top(grafo, betweenness, "intermediação", "{:.0f}", top=10)
    print(f"Concluido em {tempo:.1f}s")

    # grava o log das centralidades em arquivo de texto
    caminho_log = "centrality.log"
    print(f"\nGravando log das centralidades em '{caminho_log}'...")
    write_centrality_log(
        grafo, closeness, betweenness, caminho_log,
        top=10, component_size=len(maior_componente)
    )
    print("Log gravado.")

    print("\nTeste concluído.")


if __name__ == "__main__":
    main()