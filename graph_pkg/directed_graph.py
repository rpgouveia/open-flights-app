from .linked_list import LinkedList


class DirectedGraph:
    """Grafo direcionado, ponderado e rotulado representado por listas de adjacência."""

    def __init__(self, size: int):
        self.size = size
        self.adjacency_list = [LinkedList() for _ in range(size)]
        self.vertices = list(range(size))

    # Métodos básicos
    def create_adjacency(self, i: int, j: int, weight: float):
        """Cria adjacência direcionada de i → j com o peso especificado."""
        self.adjacency_list[i].insert(j, weight)

    def remove_adjacency(self, i: int, j: int):
        """Remove a adjacência direcionada de i → j."""
        self.adjacency_list[i].remove(j)

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

    def print_adjacent_vertices(self, vertex: int):
        """Imprime os vértices adjacentes ao vértice especificado."""
        adjacent_indices = []
        count = self.adjacent_vertices(vertex, adjacent_indices)
        labels = [self.vertices[j] for j in adjacent_indices]
        print(f"{count} adjacente(s) ao vértice {self.vertices[vertex]}: {labels}")

    # Warshall e Dijkstra
    def convert_to_adj_matrix(self) -> list[list[int]]:
        """
        Converte as listas de adjacência para uma matriz de adjacência. O(n + m)
        Retorna uma matriz n×n onde matrix[i][j] = 1 se existe aresta i → j.
        Não modifica o estado interno do grafo.
        """
        matrix = [[0] * self.size for _ in range(self.size)]
        for i in range(self.size):
            for node in self.adjacency_list[i]:
                matrix[i][node.destination] = 1
        return matrix

    def warshall(self) -> list[list[int]]:
        """
        Executa o algoritmo de Warshall sobre uma cópia da matriz de adjacência.
        Retorna a matriz de alcançabilidade (fechamento transitivo). O(n³)
        Para cada par (i, j), matrix[i][j] = 1 se j é alcançável a partir de i.
        """
        matrix = self.convert_to_adj_matrix()
        for k in range(self.size):
            for i in range(self.size):
                for j in range(self.size):
                    if matrix[i][k] and matrix[k][j]:
                        matrix[i][j] = 1
        return matrix

    def print_reachability(self):
        """Imprime a matriz de alcançabilidade com os rótulos dos vértices."""
        matrix = self.warshall()
        header = "    " + "  ".join(f"{self.vertices[j]:>2}" for j in range(self.size))
        print(header)
        for i in range(self.size):
            row = "   ".join(str(matrix[i][j]) for j in range(self.size))
            print(f"{self.vertices[i]:>2} [ {row} ]")

    def dijkstra(self, origin: int) -> tuple[list[int], list[int]]:
        """
        Executa o algoritmo de Dijkstra a partir do vértice de origem. O(n²)
        Retorna (distance, previous):
            distance[i] → custo mínimo de origin até i (float('inf') se inalcançável)
            previous[i] → índice do vértice anterior no caminho mínimo até i (-1 se nenhum)
        """
        distance = [float("inf")] * self.size
        previous = [-1] * self.size
        visited = [False] * self.size

        distance[origin] = 0

        for _ in range(self.size):
            min_distance_vertex = -1
            for vertex in range(self.size):
                if not visited[vertex] and (
                    min_distance_vertex == -1
                    or distance[vertex] < distance[min_distance_vertex]
                ):
                    min_distance_vertex = vertex

            if distance[min_distance_vertex] == float("inf"):
                break

            visited[min_distance_vertex] = True

            for node in self.adjacency_list[min_distance_vertex]:
                new_distance = distance[min_distance_vertex] + node.weight
                if new_distance < distance[node.destination]:
                    distance[node.destination] = new_distance
                    previous[node.destination] = min_distance_vertex

        return distance, previous

    def reconstruct_path(self, origin: int, target: int, previous: list[int]) -> str:
        """
        Reconstrói o caminho mínimo de origin até target usando o vetor previous.
        """
        path = []
        current = target
        while current != -1:
            path.append(self.vertices[current])
            current = previous[current]
        if path[-1] != self.vertices[origin]:
            return "inalcançável"
        path.reverse()
        return " → ".join(str(v) for v in path)

    def print_dijkstra(self, origin: int):
        """Imprime as distâncias mínimas e os caminhos a partir da origem."""
        distance, previous = self.dijkstra(origin)
        origin_label = self.vertices[origin]
        print(f"Distâncias mínimas a partir de {origin_label}:")
        for i in range(self.size):
            if distance[i] == float("inf"):
                cost = "∞"
                path = "inalcançável"
            else:
                cost = distance[i]
                path = self.reconstruct_path(origin, i, previous)
            print(
                f"  {origin_label} → {self.vertices[i]:>2}: custo={cost:>4}   caminho: {path}"
            )

    # Busca em profundidade e largura
    def depth_first_search_iterative(self, start: int, visited: list[bool]):
        """Versão iterativa da busca em profundidade. O(v + e)"""
        stack = [start]
        while stack:
            current = stack.pop()
            if not visited[current]:
                visited[current] = True
                print(f"Visitando {self.vertices[current]}")
                for node in reversed(self.adjacency_list[current]):
                    if not visited[node.destination]:
                        stack.append(node.destination)

    def depth_first_search_recursive(self, start: int, visited: list[bool]):
        """Versão recursiva da busca em profundidade. O(v + e)"""
        visited[start] = True
        print(f"Visitando {self.vertices[start]}")
        for node in self.adjacency_list[start]:
            if not visited[node.destination]:
                self.depth_first_search_recursive(node.destination, visited)

    def print_dfs_iterative(self, start: int):
        """Inicia a busca em profundidade e imprime os vértices visitados."""
        visited = [False] * self.size
        print(f"Busca em profundidade a partir de {self.vertices[start]}:")
        self.depth_first_search_iterative(start, visited)

    def print_dfs_recursive(self, start: int):
        """Inicia a busca em profundidade recursiva e imprime os vértices visitados."""
        visited = [False] * self.size
        print(f"Busca em profundidade recursiva a partir de {self.vertices[start]}:")
        self.depth_first_search_recursive(start, visited)

    def breadth_first_search_iterative(self, start: int):
        """Versão iterativa da busca em largura. O(n)"""
        visited = [False] * self.size
        queue = [start]
        visited[start] = True
        while queue:
            current = queue.pop(0)
            print(f"Visitando {self.vertices[current]}")
            for node in self.adjacency_list[current]:
                if not visited[node.destination]:
                    visited[node.destination] = True
                    queue.append(node.destination)

    def breadth_first_search_recursive(self, visited: list[bool], queue: list[int]):
        """Versão recursiva da busca em largura. O(n)"""
        if not queue:
            return
        current = queue.pop(0)
        print(f"Visitando {self.vertices[current]}")
        for node in self.adjacency_list[current]:
            if not visited[node.destination]:
                visited[node.destination] = True
                queue.append(node.destination)
        self.breadth_first_search_recursive(visited, queue)

    def print_bfs_iterative(self, start: int):
        """Inicia a busca em largura e imprime os vértices visitados."""
        print(f"Busca em largura a partir de {self.vertices[start]}:")
        self.breadth_first_search_iterative(start)

    def print_bfs_recursive(self, start: int):
        """Inicia a busca em largura recursiva e imprime os vértices visitados."""
        visited = [False] * self.size
        queue = [start]
        visited[start] = True
        print(f"Busca em largura recursiva a partir de {self.vertices[start]}:")
        self.breadth_first_search_recursive(visited, queue)

# Verificação de ciclos, componentes, conectividade
    def has_cycle_util(self, vertex: int, visited: list[bool], rec_stack: list[bool]) -> bool:
        """Função auxiliar para detectar ciclos usando DFS. O(v + e)"""
        visited[vertex] = True
        rec_stack[vertex] = True

        for node in self.adjacency_list[vertex]:
            destination = node.destination
            if not visited[destination]:
                if self.has_cycle_util(destination, visited, rec_stack):
                    return True
            elif rec_stack[destination]:
                return True

        rec_stack[vertex] = False
        return False

    def _build_undirected_adjacency(self) -> list[list[int]]:
        """
        Constrói uma visão NÃO DIRECIONADA das adjacências do grafo. O(v + e)
        Para cada arco i → j, registra j como vizinho de i e i como vizinho de j.
        Usada nas análises de conexidade fraca e componentes fracamente conectados.
        Não modifica o estado interno do grafo.
        """
        neighbors = [[] for _ in range(self.size)]
        for origin in range(self.size):
            for node in self.adjacency_list[origin]:
                destination = node.destination
                neighbors[origin].append(destination)
                neighbors[destination].append(origin)
        return neighbors

    def is_connected(self) -> bool:
        """
        Verifica se o grafo é fracamente conexo. O(v + e)

        Um grafo direcionado é fracamente conexo quando, ignorando a direção
        dos arcos, existe caminho entre qualquer par de vértices. Ou seja,
        ao tratar os arcos como bidirecionais, uma única travessia a partir
        de um vértice qualquer alcança todos os demais.

        Retorna True se o grafo é fracamente conexo, False caso contrário.
        Um grafo vazio ou com um único vértice é considerado conexo.
        """
        if self.size <= 1:
            return True

        neighbors = self._build_undirected_adjacency()
        visited = [False] * self.size

        # travessia em largura a partir do vértice 0
        queue = [0]
        visited[0] = True
        visited_count = 1

        while queue:
            current = queue.pop(0)
            for neighbor in neighbors[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    visited_count += 1
                    queue.append(neighbor)

        # conexo se a travessia alcançou todos os vértices
        return visited_count == self.size

    def print_connectivity(self):
        """Imprime se o grafo é fracamente conexo ou não."""
        if self.is_connected():
            print("O grafo é fracamente conexo.")
        else:
            print("O grafo NÃO é fracamente conexo (possui componentes separados).")

    def connected_components(self) -> list[list[int]]:
        """
        Encontra os componentes fracamente conectados do grafo. O(v + e)

        Trata os arcos como bidirecionais e percorre o grafo a partir de
        cada vértice ainda não visitado. Cada travessia descobre todos os
        vértices de um componente.

        Retorna uma lista de componentes, onde cada componente é a lista
        dos índices dos vértices que o compõem.
        """
        neighbors = self._build_undirected_adjacency()
        visited = [False] * self.size
        components = []

        for start in range(self.size):
            if visited[start]:
                continue

            # travessia em largura
            component = []
            queue = [start]
            visited[start] = True

            while queue:
                current = queue.pop(0)
                component.append(current)
                for neighbor in neighbors[current]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)

            components.append(component)

        return components

    def print_connected_components(
            self, max_components_shown: int = 10,
            max_vertices_shown: int = 10
        ):
        """
        Imprime os componentes fracamente conectados do grafo.

        Exibe o número total de componentes e detalha os maiores, limitado
        por max_components_shown. Componentes de um único vértice (isolados)
        são resumidos numa contagem, evitando milhares de linhas.

        Para componentes grandes, mostra apenas os primeiros rótulos
        (limitados por max_vertices_shown).
        """
        components = self.connected_components()
        components.sort(key=len, reverse=True)

        isolated = [c for c in components if len(c) == 1]
        non_isolated = [c for c in components if len(c) > 1]

        print(f"Total de componentes fracamente conectados: {len(components)}")
        print(f"  Componentes com mais de um vertice: {len(non_isolated)}")
        print(f"  Vertices isolados (sem conexao): {len(isolated)}")

        shown_count = min(len(non_isolated), max_components_shown)
        if shown_count > 0:
            print(f"\nMaiores componentes (ate {max_components_shown}):")

        for position in range(shown_count):
            component = non_isolated[position]
            size = len(component)
            labels = [str(self.vertices[index]) for index in component]

            if size > max_vertices_shown:
                shown = ", ".join(labels[:max_vertices_shown])
                print(f"  Componente {position + 1} ({size} vertices): {shown}, ...")
            else:
                shown = ", ".join(labels)
                print(f"  Componente {position + 1} ({size} vertices): {shown}")

        remaining = len(non_isolated) - shown_count
        if remaining > 0:
            print(f"  ... e mais {remaining} componente(s) com mais de um vertice.")

    def _degrees(self) -> tuple[list[int], list[int]]:
        """
        Calcula o grau de entrada e o grau de saída de cada vértice. O(v + e)

        Retorna (out_degree, in_degree):
            out_degree[i] → número de arcos que saem do vértice i
            in_degree[i]  → número de arcos que chegam ao vértice i
        """
        out_degree = [0] * self.size
        in_degree = [0] * self.size

        for origin in range(self.size):
            for node in self.adjacency_list[origin]:
                out_degree[origin] += 1
                in_degree[node.destination] += 1

        return out_degree, in_degree

    def _has_eulerian_connectivity(self) -> bool:
        """
        Verifica se todos os vértices que possuem algum arco (de entrada ou
        saída) pertencem a um único componente fracamente conectado. O(v + e)

        Vértices sem nenhum arco são ignorados, pois não participam de um
        eventual caminho euleriano. Essa conexão é pré-requisito para a
        existência de caminho ou circuito euleriano.
        """
        out_degree, in_degree = self._degrees()
        neighbors = self._build_undirected_adjacency()

        # encontra um vértice de partida que tenha pelo menos um arco
        start = -1
        for vertex in range(self.size):
            if out_degree[vertex] + in_degree[vertex] > 0:
                start = vertex
                break

        if start == -1:
            return True

        # travessia em largura
        visited = [False] * self.size
        queue = [start]
        visited[start] = True

        while queue:
            current = queue.pop(0)
            for neighbor in neighbors[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)

        # todo vértice com algum arco precisa ter sido alcançado
        for vertex in range(self.size):
            if out_degree[vertex] + in_degree[vertex] > 0 and not visited[vertex]:
                return False

        return True

    def has_eulerian_path(self) -> bool:
        """
        Verifica se o grafo direcionado possui um caminho euleriano. O(v + e)

        Um caminho euleriano percorre cada arco exatamente uma vez, sem
        necessariamente retornar ao vértice de origem. Para um grafo
        direcionado, existe caminho euleriano quando:

        1. No máximo um vértice tem (saída - entrada) = 1 — seria o início.
        2. No máximo um vértice tem (entrada - saída) = 1 — seria o fim.
        3. Todos os demais vértices têm grau de entrada igual ao de saída.
        4. Os vértices com arcos formam um único componente conexo.

        Retorna True se existe caminho euleriano, False caso contrário.
        """
        out_degree, in_degree = self._degrees()

        start_vertices = 0   # vértices com um arco de saída a mais
        end_vertices = 0     # vértices com um arco de entrada a mais

        for vertex in range(self.size):
            difference = out_degree[vertex] - in_degree[vertex]
            if difference == 1:
                start_vertices += 1
            elif difference == -1:
                end_vertices += 1
            elif difference != 0:
                return False

        degrees_ok = start_vertices <= 1 and end_vertices <= 1

        return degrees_ok and self._has_eulerian_connectivity()

    def print_eulerian_path(self):
        """Imprime se o grafo possui um caminho euleriano."""
        if self.has_eulerian_path():
            print("O grafo possui um caminho euleriano.")
        else:
            print("O grafo NAO possui um caminho euleriano.")