import heapq
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

    # Dijkstra
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

    def dijkstra_heap(self, origin: int) -> tuple[list[float], list[int]]:
        """
        Executa o algoritmo de Dijkstra usando fila de prioridade (heap).
        O((n + e) log n)

        Versão otimizada do dijkstra() para grafos esparsos. Em vez de varrer
        todos os vértices a cada passo para achar o de menor distância, usa um
        heap binário (heapq) que entrega o mínimo em tempo logarítmico.

        Retorna (distance, previous), com o mesmo significado de dijkstra():
            distance[i] → custo mínimo de origin até i (float('inf') se inalcançável)
            previous[i] → índice do vértice anterior no caminho mínimo até i (-1 se nenhum)
        """
        distance = [float("inf")] * self.size
        previous = [-1] * self.size
        visited = [False] * self.size

        distance[origin] = 0.0

        # heap de pares (distancia_acumulada, vertice)
        heap = [(0.0, origin)]

        while heap:
            current_distance, current = heapq.heappop(heap)

            # ignora entradas obsoletas
            if visited[current]:
                continue
            visited[current] = True

            for node in self.adjacency_list[current]:
                destination = node.destination
                new_distance = current_distance + node.weight
                if new_distance < distance[destination]:
                    distance[destination] = new_distance
                    previous[destination] = current
                    heapq.heappush(heap, (new_distance, destination))

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

    # Verificação de ciclos, componentes, conectividade
    def is_cyclic_recursive(self, vertex: int, visited: list[bool], rec_stack: list[bool]) -> bool:
        """
        Função auxiliar para detectar ciclos usando DFS. O(v + e)  
        Busca em profundidade recursiva com controle de pilha de recursão para detectar ciclos.
        """
        visited[vertex] = True
        rec_stack[vertex] = True

        for node in self.adjacency_list[vertex]:
            destination = node.destination
            if not visited[destination]:
                if self.is_cyclic_recursive(destination, visited, rec_stack):
                    return True
            elif rec_stack[destination]:
                return True

        rec_stack[vertex] = False
        return False

    def is_cyclic(self) -> bool:
        """
        Verifica se o grafo direcionado possui pelo menos um ciclo. O(v + e)  
        Busca em profundidade iterativa com controle de pilha de recursão para detectar ciclos.

        Um ciclo existe quando, durante a travessia, um arco aponta para um
        vértice que ainda está no caminho atual (pilha de recursão).

        Cada vértice passa por dois momentos na pilha:
            - descoberta: entra na pilha de recursão (caminho atual)
            - finalização: sai da pilha de recursão (todos os vizinhos visitados)

        Retorna True se há ciclo, False caso contrário.
        """
        visited = [False] * self.size
        in_stack = [False] * self.size

        for start in range(self.size):
            if visited[start]:
                continue

            stack = [(start, False)]

            # pilha de pares (vértice, finalizacao)
            # finalizacao=False → descoberta
            # finalizacao=True  → remover da pilha de recursão
            while stack:
                vertex, finishing = stack.pop()

                if finishing:
                    in_stack[vertex] = False
                    continue

                if visited[vertex]:
                    continue

                visited[vertex] = True
                in_stack[vertex] = True

                # agenda a finalização deste vértice
                stack.append((vertex, True))

                for node in self.adjacency_list[vertex]:
                    destination = node.destination
                    if not visited[destination]:
                        stack.append((destination, False))
                    elif in_stack[destination]:
                        return True

        return False

    def print_cyclic(self):
        """Imprime se o grafo possui ciclo ou não."""
        if self.is_cyclic():
            print("O grafo é CÍCLICO.")
        else:
            print("O grafo é ACÍCLICO.")

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

        # travessia em largura
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
        eventual caminho euleriano.
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
            print("O grafo NÃO possui um caminho euleriano.")

    # Medidas de Centralidade
    def closeness_centrality(self, vertices: list[int] = None) -> dict[int, float]:
        """
        Calcula a centralidade de proximidade (closeness) dos vértices. O(k (n+e) log n)

        Usa a fórmula normalizada de Wasserman-Faust, adequada a grafos desconexos.  
        A proximidade de um vértice combina duas ideias:  
            - quão perto ele está dos vértices que alcança (alcançáveis / soma das distâncias)  
            - que fração do total de vértices ele consegue alcançar (alcançáveis / (n - 1))

        O produto dos dois fatores evita a distorção da fórmula clássica, na
        qual um vértice que alcança pouquíssimos outros, mas muito próximos,
        receberia um valor artificialmente alto. Quanto maior o resultado,
        mais central é o vértice.

        Como o grafo é direcionado e ponderado, usa Dijkstra (versão com heap)
        para obter as distâncias mínimas. Vértices inalcançáveis são ignorados
        na soma.

        Referência: 
            Wasserman, S., & Faust, K. (1994). Social Network Analysis: Methods and Applications. Cambridge University Press.
            https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html

        Parâmetros:
            vertices:   lista opcional de índices a considerar como origem.
                        Se None, considera todos os vértices do grafo.
                        Passar apenas os vértices do maior componente acelera o cálculo.

        Retorna um dicionário {indice_do_vertice: valor_de_proximidade}.
        """
        if vertices is None:
            vertices = list(range(self.size))

        # número máximo de outros vértices que poderiam ser alcançados
        max_reachable = self.size - 1

        centrality = {}

        for origin in vertices:
            distance, _ = self.dijkstra_heap(origin)

            # soma as distâncias até os vértices alcançáveis, exceto o próprio
            reachable_count = 0
            distance_sum = 0.0
            for target in range(self.size):
                if target != origin and distance[target] != float("inf"):
                    reachable_count += 1
                    distance_sum += distance[target]

            # proximidade normalizada de Wasserman-Faust
            if distance_sum > 0 and max_reachable > 0:
                proximity = reachable_count / distance_sum
                reach_fraction = reachable_count / max_reachable
                centrality[origin] = proximity * reach_fraction
            else:
                centrality[origin] = 0.0

        return centrality

    def print_closeness_centrality(self, vertices: list[int] = None, top: int = 10):
        """
        Imprime os vértices com maior centralidade de proximidade.

        Calcula a proximidade e exibe os 'top' vértices de maior valor,
        que correspondem aos mais bem posicionados (mais próximos de todos
        os demais em distância de caminho mínimo).
        """
        centrality = self.closeness_centrality(vertices)
        ranking = sorted(centrality.items(), key=lambda pair: pair[1], reverse=True)

        print(f"Top {top} vértices por centralidade de proximidade:")
        for position, (vertex, value) in enumerate(ranking[:top], start=1):
            label = self.vertices[vertex]
            print(f"  {position:>2}. {label}: {value:.6f}")

    def betweenness_centrality(self, vertices: list[int] = None) -> dict[int, float]:
        """
        Calcula a centralidade de intermediação (betweenness) dos vértices. O(k (n+e) log n)

        Esta implementação reaproveita o Dijkstra (versão com heap) e reconstrói
        UM caminho mínimo por par origem-destino, usando o vetor de predecessores.
        Quando há vários caminhos mínimos de mesmo comprimento, apenas um é
        contado, então o resultado é uma APROXIMAÇÃO por caminho único.

        Parâmetros:
            vertices:   lista opcional de índices a considerar como origem.
                        Se None, considera todos os vértices do grafo.
                        Passar apenas os vértices do maior componente acelera o cálculo.

        Retorna um dicionário {indice_do_vertice: contagem_de_intermediação}.
        """
        if vertices is None:
            vertices = list(range(self.size))

        # inicializa a contagem de intermediação de todos os vértices
        centrality = {vertex: 0.0 for vertex in range(self.size)}

        for origin in vertices:
            distance, previous = self.dijkstra_heap(origin)

            # para cada destino alcançável, percorre o caminho mínimo de volta
            for target in range(self.size):
                if target == origin or distance[target] == float("inf"):
                    continue

                # caminha do destino até a origem pelos predecessores
                # creditando apenas os vértices intermediários
                current = previous[target]
                while current != -1 and current != origin:
                    centrality[current] += 1
                    current = previous[current]

        return centrality

    def print_betweenness_centrality(self, vertices: list[int] = None, top: int = 10):
        """
        Imprime os vértices com maior centralidade de intermediação.

        Calcula a intermediação e exibe os 'top' vértices de maior valor,
        que correspondem aos principais pontos de passagem (hubs/pontes) da rede.
        """
        centrality = self.betweenness_centrality(vertices)
        ranking = sorted(centrality.items(), key=lambda pair: pair[1], reverse=True)

        print(f"Top {top} vértices por centralidade de intermediação:")
        for position, (vertex, value) in enumerate(ranking[:top], start=1):
            label = self.vertices[vertex]
            print(f"  {position:>2}. {label}: {int(value)}")
