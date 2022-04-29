from sys import argv
import numpy as np
import networkx as nx


def build_instance(instance_file: str) -> nx.Graph:
    data = np.loadtxt(instance_file, dtype=int)
    n = data[0, 0] # Número de vértices
    m = data[0, 1] # Número de arestas
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
    return G

class PossibleSolution:
    def __init__(self, boxes: np.ndarray):
        self.boxes = boxes  # Lista binária que determina quais nodos possuem caixas
        self.value = self.evaluate()    # Valoração calculada para a solução

    def evaluate(self) -> int:
        # if solucao_valida -> sum
        # else              -> -1
        return sum(self.boxes)

    def generate_random_neighbor(self):
        raise NotImplementedError

    def __repr__(self):
        str_return = ''
        for i in range(len(self.boxes)):
            if self.boxes[i] == 1: label = 'Com caixa'
            else: label = 'Sem Caixa'

            str_return += f'\n\tVértice {i+1} -> {label}'

        if self.value == -1:
            str_return += f'\n-> INSTÂNCIA INVÁLIDA'
        else:
            str_return += f'\n-> Quantidade de caixas: {self.value}'

        return str_return


class Problem3:
    def __init__(self, instance_graph:nx.DiGraph,
                 S:np.ndarray or None=None,
                 l:int=10, m:int=20):
        #   =============================
        #   Parâmetros da Meta-Heurística
        #   Late Acceptance Hill Climbing
        #   =============================
        self.graph = instance_graph

        if S is not None:
            assert len(S) == nx.number_of_nodes(self.graph)
            S = PossibleSolution(S)
        else: # Solução atual começa vazia
            S = PossibleSolution([0] * nx.number_of_nodes(instance_graph))

        self.S = S
        self.S_star = S # Solução ótima
        self.l = l      # Tamanho da lista histórico de soluções geradas
        self.m = m      # Máximo de rejeições consecutivas

        #   ==================================
        #   Variáveis de execução do algoritmo
        #   ==================================
        self.r = 0  # Contador de rejeições consecutivas
        self.F = [self.S] * self.l  # Lista de últimas soluções geradas

    def update_F(self, p:int) -> None:
        self.F[p] = self.S

    def optimize(self) -> PossibleSolution:

        print('=' * 32)
        print(f'''Otimizando problema com parâmetros:
    -> l = {self.l}
    -> m = {self.m}
e solução inicial:{self.S}''')
        print('-' * 32)

        # Índice 'p' para acessar F
        p = 0

        while self.r <= self.m:

            s_ = self.S.generate_random_neighbor()
            print('Solução Candidata:', self.S)

            if s_.value >= self.S.value or s_.value >= self.F[p]:

                print('-> Solução aceita.')

                # Aceita nova solução
                if s_.value > self.S.value:
                    self.r = 0  # Reseta contador de rejeições consecutivas

                self.S = s_
                self.update_F(p)

                if self.S > self.S_star:
                    print('\t', '*'*16)
                    print('-> Melhor solução encontrada!')
                    print('\t', '*' * 16)
                    self.S_star = self.S

            p = (self.r + 1) % self.l
            self.r += 1

            print(
                f'''Variáveis ao fim da iteração:
    -> F = {self.F}
    -> r = {self.r}'''
            )

        print('\n', '='*32)
        print(
            f'''
Algoritmo LAHC encerrado.
Solução ótima encontrada:
    -> {self.S_star}'''
        )
        print('\n', '=' * 32)
        return self.S_star


if __name__ == '__main__':
    instance_file = argv[1]
    instance_graph = build_instance(instance_file)
    print(instance_graph)

    initial_solution = [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    prob3 = Problem3(instance_graph)
    optimal = prob3.optimize()
    #
    print(optimal)


