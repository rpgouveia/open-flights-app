from .linked_list import LinkedList


class UndirectedGraph:
    """Grafo não direcionado, ponderado e rotulado representado por listas de adjacência."""

    def __init__(self, size: int):
        self.size = size
        self.adjacency_list = [LinkedList() for _ in range(size)]
        self.vertices = list(range(size))

    # Métodos básicos
    def create_adjacency(self, i: int, j: int, weight: float):
        """
        Cria adjacência NÃO DIRECIONADA entre i e j com o peso especificado.
        Insere i → j e j → i para refletir a natureza bidirecional da aresta.
        """
        self.adjacency_list[i].insert(j, weight)
        self.adjacency_list[j].insert(i, weight)

    def remove_adjacency(self, i: int, j: int):
        """Remove a adjacência NÃO DIRECIONADA entre i e j (ambas as direções)."""
        self.adjacency_list[i].remove(j)
        self.adjacency_list[j].remove(i)

    def update_information(self, i: int, value: str):
        """Atualiza o rótulo do vértice i."""
        self.vertices[i] = value

    def adjacent_vertices(self, vertex: int, adjacent_indices: list) -> int:
        """
        Preenche adjacent_indices com os índices dos vértices adjacentes ao vértice especificado.
        Retorna o número de adjacentes.
        """
        adjacent_indices.clear()
        adjacent_indices.extend(self.adjacency_list[vertex].destinations())
        return len(adjacent_indices)

    def print_adjacency(self):
        """Imprime as listas de adjacência do grafo."""
        for i in range(self.size):
            label = self.vertices[i]
            nodes = [
                f"{self.vertices[node.destination]}(w={node.weight})"
                for node in self.adjacency_list[i]
            ]
            content = " -> ".join(nodes) if nodes else "None"
            print(f"{label} -> {content}")

    def print_adjacent_vertices(self, vertex: int):
        """Imprime os vértices adjacentes ao vértice especificado."""
        adjacent_indices = []
        count = self.adjacent_vertices(vertex, adjacent_indices)
        labels = [self.vertices[j] for j in adjacent_indices]
        print(f"{count} adjacente(s) ao vértice {self.vertices[vertex]}: {labels}")

    # Algoritmo de Prim — Árvore Geradora Mínima
    def prim(self, start: int = 0) -> tuple[list[tuple[int, int, float]], float]:
        """
        Encontra a Árvore Geradora Mínima (AGM) pelo algoritmo de Prim. O(v²)

        Parte de 'start' e cresce a árvore adicionando, a cada passo,
        a aresta de menor peso que conecta um vértice já na árvore
        a um vértice ainda fora dela.

        Retorna:
            (arestas_da_agm, custo_total)
            arestas_da_agm: lista de tuplas (origem, destino, peso)
            custo_total: soma dos pesos das arestas selecionadas
        """
        min_weight = [float("inf")] * self.size
        parent = [-1] * self.size
        in_tree = [False] * self.size

        min_weight[start] = 0

        mst_edges = []
        total_cost = 0

        for _ in range(self.size):
            current = -1
            for vertex in range(self.size):
                if not in_tree[vertex] and (
                    current == -1 or min_weight[vertex] < min_weight[current]
                ):
                    current = vertex

            if min_weight[current] == float("inf"):
                break

            in_tree[current] = True

            if parent[current] != -1:
                mst_edges.append((parent[current], current, min_weight[current]))
                total_cost += min_weight[current]

            for node in self.adjacency_list[current]:
                if not in_tree[node.destination] and node.weight < min_weight[node.destination]:
                    min_weight[node.destination] = node.weight
                    parent[node.destination] = current

        return mst_edges, total_cost

    def print_prim(self, start: int = 0):
        """Imprime a Árvore Geradora Mínima encontrada pelo algoritmo de Prim."""
        mst_edges, total_cost = self.prim(start)
        start_label = self.vertices[start]

        print(f"\nÁrvore Geradora Mínima — Prim (início: {start_label}):")

        if not mst_edges:
            print("  Nenhuma aresta encontrada (grafo vazio ou com um único vértice).")
            return

        for origin, destination, weight in mst_edges:
            origin_label = self.vertices[origin]
            destination_label = self.vertices[destination]
            print(f"  {origin_label} — {destination_label}  (peso: {weight})")

        print(f"\n  Custo total da AGM: {total_cost}")
        print(f"  Arestas na AGM: {len(mst_edges)}")

    # Algoritmo de Kruskal — Árvore Geradora Mínima
    def _collect_edges(self) -> list[tuple[float, int, int]]:
        """
        Coleta todas as arestas únicas do grafo como tuplas (peso, i, j).
        Como cada aresta é armazenada duas vezes na lista de adjacência,
        só inclui (i, j) quando i < j para evitar duplicatas.
        """
        edges = []
        for i in range(self.size):
            for node in self.adjacency_list[i]:
                if i < node.destination:
                    edges.append((node.weight, i, node.destination))
        return edges

    def _find(self, parent: list[int], vertex: int) -> int:
        """
        Encontra a raiz do conjunto ao qual 'vertex' pertence.
        """
        if parent[vertex] != vertex:
            parent[vertex] = self._find(parent, parent[vertex])
        return parent[vertex]

    def _union(self, parent: list[int], rank: list[int], vertex_a: int, vertex_b: int):
        """
        Une os conjuntos de vertex_a e vertex_b usando união por rank.
        O conjunto de menor rank é anexado ao de maior rank para manter a árvore rasa.
        """
        root_a = self._find(parent, vertex_a)
        root_b = self._find(parent, vertex_b)

        if rank[root_a] < rank[root_b]:
            parent[root_a] = root_b
        elif rank[root_a] > rank[root_b]:
            parent[root_b] = root_a
        else:
            parent[root_b] = root_a
            rank[root_a] += 1

    def kruskal(self) -> tuple[list[tuple[int, int, float]], float]:
        """
        Encontra a Árvore Geradora Mínima (AGM) pelo algoritmo de Kruskal. O(e log e)

        Ordena todas as arestas por peso crescente e as adiciona à AGM
        desde que não formem um ciclo.

        Retorna:
            (arestas_da_agm, custo_total)
            arestas_da_agm: lista de tuplas (origem, destino, peso)
            custo_total: soma dos pesos das arestas selecionadas
        """
        edges = self._collect_edges()
        edges.sort(key=lambda edge: edge[0])

        parent = list(range(self.size))
        rank = [0] * self.size

        mst_edges = []
        total_cost = 0

        for weight, origin, destination in edges:
            if self._find(parent, origin) != self._find(parent, destination):
                self._union(parent, rank, origin, destination)
                mst_edges.append((origin, destination, weight))
                total_cost += weight

            if len(mst_edges) == self.size - 1:
                break

        return mst_edges, total_cost

    def print_kruskal(self):
        """Imprime a Árvore Geradora Mínima encontrada pelo algoritmo de Kruskal."""
        mst_edges, total_cost = self.kruskal()

        print("\nÁrvore Geradora Mínima — Kruskal:")

        if not mst_edges:
            print("  Nenhuma aresta encontrada (grafo vazio ou com um único vértice).")
            return

        for origin, destination, weight in mst_edges:
            origin_label = self.vertices[origin]
            destination_label = self.vertices[destination]
            print(f"  {origin_label} — {destination_label}  (peso: {weight})")

        print(f"\n  Custo total da AGM: {total_cost}")
        print(f"  Arestas na AGM: {len(mst_edges)}")
