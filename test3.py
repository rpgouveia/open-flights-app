"""
Script de teste do gerador de grafo aleatório.

Demonstra:
    1. Geração de um grafo pequeno e visualização das adjacências
    2. Aplicação dos algoritmos do projeto sobre o grafo gerado
    3. Reprodutibilidade: mesma semente gera o mesmo grafo
    4. Geração de um grafo grande cumprindo os mínimos do enunciado
    5. Gravação do grafo gerado em formato Pajek
"""

import time

from random_graph import generate_random_graph
from pajek import write_pajek


def contar_arcos(grafo) -> int:
    """Conta o total de arcos do grafo."""
    return sum(len(grafo.adjacency_list[i]) for i in range(grafo.size))


def testar_grafo_pequeno():
    """Gera um grafo pequeno e mostra suas adjacências."""
    print("=" * 55)
    print("TESTE 1: Grafo aleatório pequeno")
    print("=" * 55)

    grafo = generate_random_graph(
        num_vertices=6, num_arcs=10, connected=True,
        min_weight=100.0, max_weight=5000.0,
        seed=42,
    )

    print(f"\nVertices: {grafo.size}, Arcos: {contar_arcos(grafo)}")
    print("\nListas de adjacência (peso em km):") 
    grafo.print_adjacency()


def testar_algoritmos_sobre_gerado():
    """Aplica os algoritmos do projeto sobre grafos gerados (conexo e desconexo)."""
    print("\n" + "=" * 55)
    print("TESTE 2: Algoritmos sobre o grafo gerado")
    print("=" * 55)

    # grafo gerado como conexo
    print("\n--- Grafo gerado com connected=True ---")
    grafo_conexo = generate_random_graph(20, 60, connected=True, seed=7)
    print(f"Grafo: {grafo_conexo.size} vértices, {contar_arcos(grafo_conexo)} arcos")
    grafo_conexo.print_connectivity()
    grafo_conexo.print_cyclic()
    componentes = grafo_conexo.connected_components()
    print(f"Número de componentes: {len(componentes)}")

    # grafo gerado como desconexo
    print("\n--- Grafo gerado com connected=False ---")
    grafo_desconexo = generate_random_graph(20, 60, connected=False, seed=7)
    print(f"Grafo: {grafo_desconexo.size} vértices, {contar_arcos(grafo_desconexo)} arcos")
    grafo_desconexo.print_connectivity()
    grafo_desconexo.print_cyclic()
    componentes = grafo_desconexo.connected_components()
    print(f"Número de componentes: {len(componentes)}")


def testar_reprodutibilidade():
    """Mostra que a mesma semente gera grafos idênticos."""
    print("\n" + "=" * 55)
    print("TESTE 3: Reprodutibilidade com semente")
    print("=" * 55)

    def assinatura(grafo):
        # lista ordenada de (origem, destino, peso arredondado)
        return sorted(
            (i, node.destination, round(node.weight, 3))
            for i in range(grafo.size)
            for node in grafo.adjacency_list[i]
        )

    grafo_a = generate_random_graph(30, 100, connected=True, seed=123)
    grafo_b = generate_random_graph(30, 100, connected=True, seed=123)
    grafo_c = generate_random_graph(30, 100, connected=True, seed=999)

    print(
        f"\nMesma semente (123 e 123) gera grafo idêntico: "
        f"{assinatura(grafo_a) == assinatura(grafo_b)}"
    )
    print(
        f"Sementes diferentes (123 e 999) geram grafos distintos: "
        f"{assinatura(grafo_a) != assinatura(grafo_c)}"
    )


def testar_grafo_grande():
    """Gera um grafo grande."""
    print("\n" + "=" * 55)
    print("TESTE 4: Grafo aleatório grande")
    print("=" * 55)

    inicio = time.time()
    grafo = generate_random_graph(
        num_vertices=5000, num_arcs=20000, connected=True,
        min_weight=1.0, max_weight=10000.0,
        seed=2024,
    )
    tempo = time.time() - inicio

    total_arcos = contar_arcos(grafo)
    print(f"\nGerado em {tempo:.3f}s")
    print(f"Vértices: {grafo.size}")
    print(f"Arcos: {total_arcos}")

    # grava em Pajek
    caminho = "random_graph.net"
    write_pajek(grafo, caminho)
    print(f"\nGrafo gravado em '{caminho}'.")


def main():
    testar_grafo_pequeno()
    testar_algoritmos_sobre_gerado()
    testar_reprodutibilidade()
    testar_grafo_grande()
    print("\nTestes concluídos.")


if __name__ == "__main__":
    main()