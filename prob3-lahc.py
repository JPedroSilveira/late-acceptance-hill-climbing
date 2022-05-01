from sys import argv
import numpy as np
from regex import W
import networkx as nx


def build_instance(instance_file: str) -> nx.DiGraph:
    data = np.loadtxt(instance_file, dtype=int)
    n = data[0, 0]  # Número de vértices
    m = data[0, 1]  # Número de arestas
    A = np.zeros((n, n))

    for i in data[1:]:
        # Corrigindo índices
        i[0] -= 1
        i[1] -= 1

        # Definindo arestas
        A[i[0], i[1]] = 1
        A[i[1], i[0]] = 1

    G = nx.from_numpy_matrix(A)

    assert nx.number_of_nodes(G) == n
    assert nx.number_of_edges(G) == m

    G = nx.to_directed(G)
    assert type(G) == nx.DiGraph
    return G


class PossibleSolution:
    def __init__(self, boxes: np.ndarray):
        self.boxes = boxes  # Lista booleana que determina quais nodos possuem caixas
        self.value = -1  # Valoração calculada para a solução


    def turn_valid(self, graph: nx.DiGraph):
        # =================================
        # Caso a solução não seja factível,
        #  iremos modificá-la afim de que
        #       se torne factível
        graph_copy = graph.copy()


        # Dada a disposição de caixas atual:
        # remove os arcos que partem de
        # vértices com caixa.
        boxed_nodes = []
        for node in nx.nodes(graph):
            if self.boxes[node]:
                boxed_nodes.append(node)
                out_edges = graph_copy.out_edges(node)
                for edge in list(out_edges):
                    graph_copy.remove_edge(*edge)

        # Dado vértices que receberam caixas
        # e que não são acessíveis a partir da origem:
        # remove a caixa, re-insere os arcos
        for boxed_node in boxed_nodes:
            reachable = nx.has_path(graph_copy, 0, boxed_node)
            if not reachable:
                self.boxes[boxed_node] = False
                out_edges = graph.out_edges(boxed_node)
                for edge in list(out_edges):
                    graph_copy.add_edge(*edge)

        self.value = sum(self.boxes)
        return self

    def generate_random_neighbor(self, graph: nx.DiGraph):  # -> PossibleSolution
        value = -1

        # =========================
        # Random Neighborhood com
        #   aplicação de máscara
        #    na solução atual
        while value == -1:
            random_mask = np.concatenate(([False], np.random.choice([True, False], len(self.boxes) - 1)), axis=0)

            if np.random.choice([True, False]):
                applied = np.logical_or(self.boxes, random_mask)
            else:
                applied = np.logical_xor(self.boxes, random_mask)

            neighbor = PossibleSolution(applied).turn_valid(graph)
            value = neighbor.value

        return neighbor

    def __repr__(self):
        str_return = ""
        # for i in range(len(self.boxes)):
        #     if self.boxes[i] == 1: label = 'Com caixa'
        #     else: label = 'Sem Caixa'
        #
        #     str_return += f'\n\tVértice {i+1} -> {label}'

        str_return += str(self.boxes)

        if self.value == -1:
            str_return += f"\n-> INSTÂNCIA INVÁLIDA"
        else:
            str_return += f"\n-> Quantidade de caixas: {self.value}"

        return str_return


class Problem3:
    def __init__(self, instance_graph: nx.DiGraph, S: np.ndarray or None = None, l: int = 10, m: int = 20):
        #   =============================
        #   Parâmetros da Meta-Heurística
        #   Late Acceptance Hill Climbing
        #   =============================
        self.graph = instance_graph

        if S is not None:  # Caso uma solução inicial tenha sido dada
            assert len(S) == nx.number_of_nodes(self.graph)
            S = PossibleSolution(S).turn_valid(self.graph)
        else:  # Solução atual começa vazia
            S = PossibleSolution([0] * nx.number_of_nodes(instance_graph)).turn_valid(self.graph)
        self.S = S  # Solucão inicial
        self.S_star = S  # Solução ótima
        self.l = l  # Tamanho da lista histórico de soluções geradas
        self.m = m  # Máximo de rejeições consecutivas

        #   ==================================
        #   Variáveis de execução do algoritmo
        #   ==================================
        self.r = 0  # Contador de rejeições consecutivas
        self.F = [self.S] * self.l  # Lista de últimas soluções geradas

    def update_F(self, p: int) -> None:
        self.F[p] = self.S

    def optimize(self) -> PossibleSolution:

        print("=" * 32)
        print(
            f"""Otimizando problema com parâmetros:
    -> l = {self.l}
    -> m = {self.m}
e solução inicial:{self.S}"""
        )
        print("-" * 32)

        # Índice 'p' para acessar F
        p = 0

        while self.r <= self.m:

            s_ = self.S.generate_random_neighbor(self.graph)
            # print("Solução Candidata:", self.S)
            # print("Value", s_.value)

            if s_.value >= self.S.value or s_.value >= self.F[p].value:

                # print("-> Solução aceita.")

                # Aceita nova solução
                if s_.value > self.S.value:
                    self.r = 0  # Reseta contador de rejeições consecutivas

                self.S = s_
                self.update_F(p)

                if self.S.value > self.S_star.value:
                    # print("\t", "*" * 16)
                    # print("-> Melhor solução encontrada!")
                    # print("\t", "*" * 16)
                    self.S_star = self.S

            p = (self.r + 1) % self.l
            self.r += 1

        #            print(
        #                f"""Variáveis ao fim da iteração:
        #    -> F = {[i.value for i in self.F]}
        #    -> r = {self.r}"""
        #            )

        print("\n", "=" * 32)
        print(
            f"""
Algoritmo LAHC encerrado.
Solução ótima encontrada:
    -> {self.S_star}"""
        )
        print("\n", "=" * 32)
        return self.S_star


if __name__ == "__main__":
    instance_file = argv[1]
    instance_graph = build_instance(instance_file)
    # print(instance_graph)

    initial_solution = [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    prob3 = Problem3(instance_graph)
    optimal = prob3.optimize()
    # print(optimal)
