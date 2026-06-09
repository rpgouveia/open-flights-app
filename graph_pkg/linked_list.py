class Node:
    def __init__(self, destination: int, weight: int):
        self.destination = destination
        self.weight = weight
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.length = 0

    def insert(self, destination: int, weight: int):
        """Insere um novo nó no início da lista. O(1)"""
        new_node = Node(destination, weight)
        new_node.next = self.head
        self.head = new_node
        self.length += 1

    def remove(self, destination: int) -> bool:
        """
        Remove o nó com o destino especificado. O(k)
        Retorna True se removeu, False se não encontrou.
        """
        current = self.head
        previous = None

        while current is not None:
            if current.destination == destination:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                self.length -= 1
                return True
            previous = current
            current = current.next

        return False

    def destinations(self) -> list[int]:
        """Retorna lista com todos os destinos. O(k)"""
        result = []
        current = self.head
        while current is not None:
            result.append(current.destination)
            current = current.next
        return result

    def is_empty(self) -> bool:
        """Retorna True se a lista está vazia. O(1)"""
        return self.head is None

    def __len__(self) -> int:
        """Retorna o número de nós na lista. O(1)"""
        return self.length

    def __iter__(self):
        """Permite iterar sobre os nós da lista com for. O(k)"""
        current = self.head
        while current is not None:
            yield current
            current = current.next

    def __reversed__(self):
        """Permite iterar sobre os nós em ordem reversa com reversed(). O(k)"""
        nodes = []
        current = self.head
        while current is not None:
            nodes.append(current)
            current = current.next
        for node in reversed(nodes):
            yield node

    def __str__(self) -> str:
        """Representação legível da lista. O(k)"""
        nodes = [f"{node.destination}(w={node.weight})" for node in self]
        return " -> ".join(nodes) if nodes else "None"