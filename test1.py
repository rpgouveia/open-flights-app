"""
Script de teste para os módulos já implementados do projeto.

Parte 1 - Testes didáticos com grafos pequenos montados à mão:
    1. Gravação em formato Pajek (write_pajek)
    2. Carregamento de formato Pajek (read_pajek)
    3. Verificação de conexidade fraca (is_connected)

Parte 2 - Teste com os dados reais do OpenFlights:
    4. Carregamento dos aeroportos e rotas
    5. Estatísticas do grafo (nós, arcos)
    6. Gravação do grafo real em formato Pajek
    7. Verificação de conexidade do grafo real
"""

import time
from graph_pkg.directed_graph import DirectedGraph
from pajek import write_pajek, read_pajek
from openflights import build_graph


AIRPORTS_PATH = "dataset/airports.dat"
ROUTES_PATH = "dataset/routes.dat"


def construir_grafo_exemplo() -> DirectedGraph:
    """
    Constrói um grafo direcionado de exemplo simulando rotas aéreas.
    Cinco aeroportos brasileiros com algumas rotas entre eles.
    Os pesos representam distâncias aproximadas em quilômetros.
    """
    rotulos = ["GRU", "GIG", "BSB", "CWB", "SSA"]
    grafo = DirectedGraph(len(rotulos))
    for indice, rotulo in enumerate(rotulos):
        grafo.update_information(indice, rotulo)

    # rotas direcionadas (origem, destino, distancia_km)
    rotas = [
        (0, 1, 357.5),   # GRU -> GIG
        (1, 0, 357.5),   # GIG -> GRU
        (0, 2, 873.0),   # GRU -> BSB
        (2, 3, 1078.4),  # BSB -> CWB
        (3, 0, 408.1),   # CWB -> GRU
        (1, 4, 1209.0),  # GIG -> SSA
    ]
    for origem, destino, distancia in rotas:
        grafo.create_adjacency(origem, destino, distancia)

    return grafo


def contar_arcos(grafo: DirectedGraph) -> int:
    """Conta o total de arcos do grafo."""
    return sum(len(grafo.adjacency_list[i]) for i in range(grafo.size))


def testar_gravacao_e_carregamento():
    """Testa o ciclo de gravar em Pajek e carregar de volta."""
    print("=" * 55)
    print("TESTE 1: Gravacao e carregamento em formato Pajek")
    print("=" * 55)

    grafo = construir_grafo_exemplo()

    print("\nGrafo original (listas de adjacencia):")
    grafo.print_adjacency()

    caminho = "grafo_teste.net"
    write_pajek(grafo, caminho)
    print(f"\nGrafo gravado em '{caminho}'. Conteudo do arquivo:\n")
    with open(caminho, "r", encoding="utf-8") as arquivo:
        print(arquivo.read())

    grafo_carregado = read_pajek(caminho)
    print("Grafo carregado do arquivo (listas de adjacencia):")
    grafo_carregado.print_adjacency()


def testar_conexidade():
    """Testa a verificacao de conexidade fraca em diferentes grafos."""
    print("\n" + "=" * 55)
    print("TESTE 2: Verificacao de conexidade fraca")
    print("=" * 55)

    print("\nGrafo de exemplo (rotas conectadas):")
    grafo_conexo = construir_grafo_exemplo()
    grafo_conexo.print_connectivity()

    print("\nGrafo com dois grupos isolados:")
    grafo_desconexo = DirectedGraph(4)
    for indice, rotulo in enumerate(["GRU", "GIG", "JFK", "LAX"]):
        grafo_desconexo.update_information(indice, rotulo)
    grafo_desconexo.create_adjacency(0, 1, 357.5)
    grafo_desconexo.create_adjacency(2, 3, 3974.0)
    grafo_desconexo.print_connectivity()


def testar_dados_reais():
    """Carrega os dados reais do OpenFlights e executa as etapas sobre eles."""
    print("\n" + "=" * 55)
    print("TESTE 3: Dados reais do OpenFlights")
    print("=" * 55)

    print("\nCarregando aeroportos e rotas...")
    inicio = time.time()
    grafo, id_to_index, _ = build_graph(AIRPORTS_PATH, ROUTES_PATH)
    tempo = time.time() - inicio
    print(f"Grafo construido em {tempo:.2f}s")

    # estatisticas
    total_arcos = contar_arcos(grafo)
    print(f"\nNos (aeroportos): {grafo.size}")
    print(f"Arcos (rotas): {total_arcos}")

    # gravacao em Pajek
    caminho = "openflights.net"
    print(f"\nGravando grafo completo em '{caminho}'...")
    inicio = time.time()
    write_pajek(grafo, caminho)
    tempo = time.time() - inicio
    print(f"Arquivo gravado em {tempo:.2f}s")

    # conexidade do grafo real
    print("\nVerificando conexidade do grafo real...")
    inicio = time.time()
    conexo = grafo.is_connected()
    tempo = time.time() - inicio
    print(f"Verificacao concluida em {tempo:.2f}s")
    grafo.print_connectivity()


def main():
    testar_gravacao_e_carregamento()
    testar_conexidade()
    testar_dados_reais()
    print("\nTestes concluidos.")


if __name__ == "__main__":
    main()