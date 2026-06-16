"""
Carregador dos dados do OpenFlights.

Lê os arquivos airports.dat e routes.dat e constrói um grafo direcionado
onde os nós são aeroportos e os arcos são rotas aéreas. O peso de cada
arco é a distância geográfica em quilômetros entre origem e destino,
calculada pela fórmula de Haversine.

Fontes: 
    https://en.wikipedia.org/wiki/Haversine_formula
    https://openflights.org/data.php

Formato de airports.dat (CSV):
    ID, Nome, Cidade, Pais, IATA, ICAO, Latitude, Longitude, ...

Formato de routes.dat (CSV):
    Companhia, ID_Companhia, Origem, ID_Origem, Destino, ID_Destino, ...
"""

import csv
import math
from graph_pkg import DirectedGraph

EARTH_RADIUS_KM = 6371.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância em quilômetros entre dois pontos da superfície
    terrestre a partir de suas coordenadas geográficas. O(1)

    Usa a fórmula de Haversine, que considera a curvatura da Terra
    tratando-a como uma esfera de raio médio.
    """
    # converte graus para radianos
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # fórmula de Haversine
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def load_airports(path: str) -> dict:
    """
    Lê airports.dat e retorna um dicionário que mapeia o ID OpenFlights
    do aeroporto para seus dados. O(n)

    Cada valor é um dicionário com nome, código IATA, país, latitude e
    longitude. Aeroportos sem coordenadas válidas são ignorados, pois
    não permitem calcular distâncias.
    """
    airports = {}
    with open(path, "r", encoding="utf-8") as input_file:
        for row in csv.reader(input_file):
            if len(row) < 8:
                continue

            airport_id = row[0]
            name = row[1]
            country = row[3]
            iata = row[4]

            try:
                latitude = float(row[6])
                longitude = float(row[7])
            except ValueError:
                continue

            airports[airport_id] = {
                "name": name,
                "iata": iata,
                "country": country,
                "latitude": latitude,
                "longitude": longitude,
            }

    return airports


def load_routes(path: str) -> list:
    """
    Lê routes.dat e retorna uma lista de pares (id_origem, id_destino). O(m)
    Linhas com aeroportos de ID nulo são ignoradas.
    """
    routes = []
    with open(path, "r", encoding="utf-8") as input_file:
        for row in csv.reader(input_file):
            if len(row) < 6:
                continue

            source_id = row[3]
            destination_id = row[5]

            # ignora rotas com identificadores nulos
            if source_id == "\\N" or destination_id == "\\N":
                continue

            routes.append((source_id, destination_id))

    return routes


def build_graph(airports_path: str, routes_path: str) -> tuple[DirectedGraph, dict, dict]:
    """
    Constrói o grafo direcionado das rotas aéreas a partir dos arquivos
    do OpenFlights.

    Cada aeroporto com coordenadas válidas vira um nó, rotulado com seu
    código IATA (ou o nome, se não houver IATA). Cada rota única vira um
    arco, com peso igual à distância em quilômetros pela fórmula de Haversine.

    Retorna:
        (grafo, mapa_id_para_indice, dicionario_aeroportos)
        grafo: instância de DirectedGraph já preenchida
        mapa_id_para_indice: dicionário do ID OpenFlights para o índice do nó
        dicionario_aeroportos: dados brutos para uso na interface
    """
    airports = load_airports(airports_path)
    routes = load_routes(routes_path)

    # mapeia cada ID OpenFlights para um índice contíguo (base 0) do grafo
    id_to_index = {}
    for airport_id in airports:
        id_to_index[airport_id] = len(id_to_index)

    graph = DirectedGraph(len(airports))

    # define o rótulo de cada nó: código IATA, ou nome se IATA estiver vazio
    for airport_id, data in airports.items():
        index = id_to_index[airport_id]
        label = data["iata"] if data["iata"] and data["iata"] != "\\N" else data["name"]
        graph.update_information(index, label)

    # cria os arcos, evitando duplicatas (rotas repetidas por companhias diferentes)
    created_arcs = set()
    for source_id, destination_id in routes:
        # ambos os aeroportos precisam existir e ter coordenadas
        if source_id not in id_to_index or destination_id not in id_to_index:
            continue
        if source_id == destination_id:
            continue

        arc = (source_id, destination_id)
        if arc in created_arcs:
            continue
        created_arcs.add(arc)

        source_index = id_to_index[source_id]
        destination_index = id_to_index[destination_id]

        source_data = airports[source_id]
        destination_data = airports[destination_id]

        distance = haversine_distance(
            source_data["latitude"], source_data["longitude"],
            destination_data["latitude"], destination_data["longitude"],
        )

        graph.create_adjacency(source_index, destination_index, distance)

    # Retorna também o dicionário bruto de aeroportos
    return graph, id_to_index, airports