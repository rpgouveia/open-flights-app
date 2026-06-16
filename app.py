import os
import streamlit as st
from openflights.loader import build_graph
from random_graph.generator import generate_random_graph
from pajek.pajek_io import write_pajek, read_pajek

st.set_page_config(page_title="OpenFlights - Malha Aérea", layout="wide")

@st.cache_resource
def load_dataset():
    """
    Carrega o dataset, constroi o grafo e demonstra o ciclo Pajek.

    Fluxo:
        1. build_graph lê os .dat e constrói o grafo original, junto com
        o mapa de índices e os dados dos aeroportos com as coordenadas.
        2. O grafo é SEMPRE regravado em formato Pajek e relido de volta.
        3. A aplicação usa o grafo RELIDO do Pajek para os algoritmos.
        Os nomes, siglas e coordenadas vem de airports_data, que e
        uma fonte separada (o Pajek não guarda coordenadas).
    """
    airports_path = os.path.join("dataset", "airports.dat")
    routes_path = os.path.join("dataset", "routes.dat")
    pajek_path = os.path.join("dataset", "openflights.net")

    if not os.path.exists(airports_path) or not os.path.exists(routes_path):
        return None, None, None

    # 1. construir o grafo original a partir dos dados brutos
    original_graph, id_to_index_map, airports_data = build_graph(airports_path, routes_path)

    # 2. demonstrar o ciclo Pajek: sempre regrava e rele
    write_pajek(original_graph, pajek_path)
    flight_graph = read_pajek(pajek_path)

    # 3. retorna o grafo relido do Pajek, mais os metadados com as coordenadas
    return flight_graph, id_to_index_map, airports_data


flight_graph, id_to_index, airports_data = load_dataset()

if flight_graph is None:
    st.error("Arquivos do dataset não encontrados. Certifique-se de que airports.dat e routes.dat estão na pasta 'dataset/'.")
    st.stop()

index_to_display = {}
for airport_id, index in id_to_index.items():
    data = airports_data[airport_id]
    iata = data["iata"]
    name = data["name"]
    clean_name = name.replace("(Duplicate)", "").replace("(duplicate)", "").strip()

    # formatar com a sigla
    if iata and iata != "\\N":
        index_to_display[index] = f"{clean_name} ({iata}) - Nó {index}"
    else:
        index_to_display[index] = f"{clean_name} (SEM SIGLA) - Nó {index}"

valid_indices = list(index_to_display.keys())
valid_indices.sort(key=lambda idx: index_to_display[idx])

st.title("OpenFlights - Análise de Malha Aérea")
st.markdown("Aplicação de grafos para rotas de voos.")

selected_menu = st.sidebar.selectbox(
    "Navegação",
    [
        "1. Visão Geral",
        "2. Buscar Rota (Dijkstra)",
        "3. Análise Estrutural",
        "4. Centralidades",
        "5. Grafo Aleatório (Pajek)"
    ]
)

if selected_menu == "1. Visão Geral":
    st.header("Informações do Dataset")
    total_edges = sum(len(flight_graph.adjacency_list[i]) for i in range(flight_graph.size))

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total de Aeroportos (Nós)", value=flight_graph.size)
    with col2:
        st.metric(label="Total de Rotas (Arestas)", value=total_edges)

    st.info("Utilize o menu lateral para navegar pelas funcionalidades.")

elif selected_menu == "2. Buscar Rota (Dijkstra)":
    st.header("Planejamento de Rota (Caminho Mínimo)")

    col1, col2 = st.columns(2)
    with col1:
        origin_index = st.selectbox(
            "Aeroporto de Origem",
            options=valid_indices,
            format_func=lambda idx: index_to_display[idx]
        )
    with col2:
        destination_index = st.selectbox(
            "Aeroporto de Destino",
            options=valid_indices,
            format_func=lambda idx: index_to_display[idx]
        )

    if st.button("Buscar Melhor Rota"):
        if origin_index == destination_index:
            st.warning("O aeroporto de destino deve ser diferente do aeroporto de origem.")
        else:
            distance_map, previous_map = flight_graph.dijkstra_heap(origin_index)

            if distance_map[destination_index] == float('inf'):
                st.warning("Não há uma rota disponível conectando estes dois aeroportos.")
            else:
                path_str = flight_graph.reconstruct_path(origin_index, destination_index, previous_map)
                st.success("Rota encontrada com sucesso!")
                st.write(f"**Distância Estimada:** {distance_map[destination_index]:.2f} km")
                st.write(f"**Trajeto:** {path_str}")

elif selected_menu == "3. Análise Estrutural":
    st.header("Validações do Grafo")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Analisar Conectividade e Componentes"):
            is_connected = flight_graph.is_connected()
            if is_connected:
                st.success("O grafo é fracamente conexo.")
            else:
                st.warning("O grafo NÃO é fracamente conexo. Extraindo componentes...")
                components = flight_graph.connected_components()
                components.sort(key=len, reverse=True)

                st.write(f"**Total de Componentes Encontrados:** {len(components)}")
                st.write("Top 5 maiores componentes:")
                for i, comp in enumerate(components[:5]):
                    st.write(f"- Componente {i+1}: {len(comp)} vértices")

    with col2:
        if st.button("Verificar Ciclos"):
            if flight_graph.is_cyclic():
                st.success("O grafo possui ciclos (Cíclico).")
            else:
                st.info("O grafo não possui ciclos (Acíclico).")

        if st.button("Verificar Caminho Euleriano"):
            if flight_graph.has_eulerian_path():
                st.success("O grafo possui um Caminho Euleriano.")
            else:
                st.warning("O grafo NÃO possui um Caminho Euleriano.")

elif selected_menu == "4. Centralidades":
    st.header("Análise de Importância dos Aeroportos")
    st.info("O cálculo utiliza a fórmula com fator de correção para grafos desconexos.")

    if st.button("Processar Top 10 Aeroportos (Maior Componente)"):
        with st.spinner("Computando centralidades... Isso pode levar alguns segundos."):
            components = flight_graph.connected_components()
            main_component = max(components, key=len)

            closeness_metrics = flight_graph.closeness_centrality(main_component)
            betweenness_metrics = flight_graph.betweenness_centrality(main_component)

            top_closeness = sorted(closeness_metrics.items(), key=lambda x: x[1], reverse=True)[:10]
            top_betweenness = sorted(betweenness_metrics.items(), key=lambda x: x[1], reverse=True)[:10]

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Proximidade (Closeness)")
                for rank, (vertex, value) in enumerate(top_closeness, start=1):
                    st.write(f"**{rank}.** {flight_graph.vertices[vertex]} - `{value:.6f}`")

            with col2:
                st.subheader("Intermediação (Betweenness)")
                for rank, (vertex, value) in enumerate(top_betweenness, start=1):
                    st.write(f"**{rank}.** {flight_graph.vertices[vertex]} - `{value:.0f}`")

elif selected_menu == "5. Grafo Aleatório (Pajek)":
    st.header("Gerador Aleatório e Exportação Pajek")

    col1, col2 = st.columns(2)
    with col1:
        requested_vertices = st.number_input("Número de Vértices", min_value=2, value=100)
    with col2:
        requested_arcs = st.number_input("Número de Arestas", min_value=0, value=500)

    force_connectivity = st.checkbox("Garantir conexidade", value=True)

    if st.button("Gerar Grafo e Exportar"):
        try:
            generated_graph = generate_random_graph(
                requested_vertices,
                requested_arcs,
                connected=force_connectivity
            )

            real_arcs = sum(
                len(generated_graph.adjacency_list[i])
                for i in range(generated_graph.size)
            )
            st.success(f"Grafo gerado: {generated_graph.size} vértices e {real_arcs} arestas.")

            os.makedirs("results", exist_ok=True)
            export_path = os.path.join("results", "grafo-aleatorio.net")
            write_pajek(generated_graph, export_path)

            st.info(f"Arquivo exportado com sucesso para: `{export_path}`")

        except ValueError as error_msg:
            st.error(f"Erro de validação: {error_msg}")