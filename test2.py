"""
Script de teste com os dados reais do OpenFlights.

Carrega os aeroportos e rotas, mostra as estatisticas do grafo,
grava em formato Pajek e verifica a conexidade.
"""

import time

from graph_pkg.directed_graph import DirectedGraph
from pajek import write_pajek
from openflights import build_graph


# caminhos dos arquivos de dados
AIRPORTS_PATH = "dataset/airports.dat"
ROUTES_PATH = "dataset/routes.dat"


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
    grafo, id_to_index = build_graph(AIRPORTS_PATH, ROUTES_PATH)
    tempo = time.time() - inicio
    print(f"Grafo construido em {tempo:.2f}s")

    # estatisticas
    total_arcos = contar_arcos(grafo)
    print(f"\nNos (aeroportos): {grafo.size}")
    print(f"Arcos (rotas): {total_arcos}")

    nos_ok = "ATENDE" if grafo.size >= 5000 else "NAO ATENDE"
    arcos_ok = "ATENDE" if total_arcos >= 20000 else "NAO ATENDE"
    print(f"\nRequisito minimo de 5000 nos: {nos_ok} ({grafo.size})")
    print(f"Requisito minimo de 20000 arcos: {arcos_ok} ({total_arcos})")

    # gravacao em Pajek
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
    print(f"\nAnalise de componentes concluida em {tempo:.2f}s")

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

    # centralidades (calculadas sobre o maior componente, por desempenho)
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
    grafo.print_closeness_centrality(vertices=maior_componente, top=10)
    tempo = time.time() - inicio
    print(f"Concluido em {tempo:.1f}s")

    print("\nCalculando centralidade de intermediacao...")
    inicio = time.time()
    grafo.print_betweenness_centrality(vertices=maior_componente, top=10)
    tempo = time.time() - inicio
    print(f"Concluido em {tempo:.1f}s")

    print("\nTeste concluido.")


if __name__ == "__main__":
    main()