# open-flights-app

PUCPR - Grafos - Projeto Colaborativo 2

Aplicação de análise de grafos sobre a malha aérea mundial, usando os dados
abertos do [OpenFlights](https://openflights.org/data.php). Os aeroportos são
os nós e as rotas aéreas são os arcos de um grafo direcionado, ponderado e
rotulado. O peso de cada arco é a distância geográfica em quilômetros entre
origem e destino, calculada pela fórmula de Haversine.

Todo o pacote de grafos e os algoritmos foram construídos manualmente, sem o
uso de bibliotecas prontas de grafos.

## Modelagem

- **Nós:** aeroportos (rotulados pelo código IATA ou pelo nome).
- **Arcos:** rotas aéreas direcionadas entre aeroportos.
- **Pesos:** distância em quilômetros (fórmula de Haversine sobre latitude e longitude).
- **Escala:** 7.698 aeroportos e 36.906 rotas, atendendo aos mínimos de 5.000 nós e 20.000 arestas.

O grafo real não é fracamente conexo: há um componente principal com a maior
parte das rotas comerciais e milhares de aeroportos isolados (sem rotas no dataset).

## Funcionalidades

- Gravação e carregamento de grafos em formato Pajek (`.net`).
- Verificação de conexidade fraca e extração de componentes.
- Verificação de caminho euleriano.
- Detecção de ciclos.
- Caminho mínimo entre aeroportos (Dijkstra).
- Medidas de centralidade: proximidade (closeness) e intermediação (betweenness).
- Gerador de grafo direcionado aleatório (conexo ou desconexo).
- Geração de log das centralidades em arquivo de texto.

## Estrutura do projeto

```
open-flights-app/
├── app.py                 Aplicação Streamlit (interface principal)
├── test1.py               Testes simples com formato PAJEK e grafos pequenos
├── test2.py               Testes com os dados reais do OpenFlights
├── test3.py               Testes do gerador aleatório
├── dataset/               Arquivos de dados (airports.dat, routes.dat)
├── graph_pkg/             Pacote de grafos construído manualmente
├── pajek/                 Gravação e carregamento em formato Pajek
├── openflights/           Carregador dos dados e cálculo de distâncias
├── random_graph/          Gerador de grafo aleatório
├── results/               Resultados (Grafos gerados, centralidades, arquivos Gephi)
└── centrality_log/        Gravação do log das centralidades
```

## Como executar

### Pré-requisitos

- Python 3.10 ou superior.
- Streamlit (`pip install streamlit`).

### Ambiente Virtual

É recomendado usar um ambiente virtual para isolar as dependências do projeto:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

### Dataset

Baixe os arquivos `airports.dat` e `routes.dat` da
[página de dados do OpenFlights](https://openflights.org/data.php) e coloque-os
na pasta `dataset/`.

### Aplicação

Na raiz do projeto, execute:

```
streamlit run app.py
```

A aplicação abre no navegador, com um menu lateral que dá acesso às análises da
malha aérea: visão geral, busca de rotas, análise estrutural, centralidades e
gerador de grafo aleatório.

## Autores

- Ângelo Piovezan
- Renato Gouveia

## Créditos dos dados

Dados de aeroportos e rotas fornecidos pelo
[OpenFlights](https://openflights.org/data.php), sob a licença
Open Database License (ODbL). Os dados de rotas refletem a situação de junho
de 2014.