# import Pkg;
# Pkg.add("JuMP")
# Pkg.add("Gurobi")
# Pkg.add("Formatting")
# Pkg.add("DelimitedFiles")
# Pkg.add("LightGraphs")
# Pkg.add("BenchmarkTools")

using Formatting
using LinearAlgebra

module PROBLEM_3
    using JuMP
    using Gurobi
    using DelimitedFiles
    using LightGraphs
    using BenchmarkTools

    grb_env = Gurobi.Env()


    #   =======================
    #   Definição de estruturas
    #   e funções auxiliares
    #   =======================


    struct Problem_3
        G # Grafo
        z # Num caixas
    end

    function print_instance(problem)
        println.("", edges(problem.G))
#         println.()
    end

    function build_instance(data)
        n = data[1,1]
        m = data[1,2]

        A = zeros(UInt8, (n, n))

        for line = 2:size(data, 1)
            A[data[line, 1], data[line, 2]] = 1
            A[data[line, 2], data[line, 1]] = 1
        end # for

        G = DiGraph(A)
        instance = Problem_3(G, 0)

        return instance
    end # build_instance


    #   ================
    #   Leitura de dados
    #   ================


    instance_file = "instances/instance_12_17.dat"
#     instance_file = "instances/instance_200_1980.dat"
#     instance_file = "instances/instance_500_6225.dat"
#     instance_file = "instances/instance_10000_19800.dat"
    data = readdlm(instance_file, ' ', UInt)

    println("===================")
    println("-> Construindo Instância para {", instance_file, "}..."); println("")
    problem = @btime(build_instance(data))
    print_instance(problem)
    println("==================="); println("")


    #   ==========
    #   Formulação
    #   ==========


    model = Model(() -> Gurobi.Optimizer(grb_env))

    #   ---------
    #   Constantes
    #   ---------
    n = size(vertices(problem.G), 1)
    println("n = ", n)

    M = n^2
    println("M = ", M)

    v_i = vertices(problem.G)[1]
    println("Vértice Inicial = ", v_i)

    #   ---------
    #   Variáveis
    #   ---------

    # C: Define se um vértice possui uma caixa
    @variable(model, C[1:n], Bin)

    # A: Matriz que contém todos os possíveis
    # grafos considerando cada vértice não-inicial
    # como destino.
    # A(d1, d2, d3)
    #   -> d1: Dimensão que representa cada possível
    #          vértice com caixa.
    #   -> d2 e d3: Representam as arestas do grafo.
    # TODO: lembrar que na 1a dimensão o indice inicial está deslocado em 1 unidade para cima
    @variable(model, A[1:n-1, 1:n, 1:n], Bin)

    @variable(model, Mozao, Int)

    #   ----------
    #   Restrições
    #   ----------
    @constraint(model, C[1] == 0)

    for i in 1:n-1          # d1
#         Mozao == M * (1 - C[i + 1])
#         @constraint(model, Mozao == M * (1 - C[i + 1]))

        for j in 1:n         # d2
            for k in 1:n     # d3
                @constraint(model, A[i, j, k] <= has_edge(problem.G, j, k))
            end

            # ====================
            # Conservação de Fluxo
            # ====================

            # Par que restringe:
            #
            #   -> Ao valor de um: a quantidade de arestas que saem
            #      de um vértice qualquer 'j'.
            #   -> Ao valor de um: a quantidade de arestas que entram
            #      em um vértice qualquer 'j'.
            @constraint(model, sum(A[i, 2:n, 2:n]) - sum(A[i, 2:n, 2:n]) >= 0 - M * (1 - C[i + 1]))
            @constraint(model, sum(A[i, 2:n, 2:n]) - sum(A[i, 2:n, 2:n]) <= 0 + M * (1 - C[i + 1]))


            # Par que restringe:
            #
            #   -> Ao valor de um: a quantidade de arestas do
            #      vértice original à qualquer outro vértice.
            #   -> Ao valor de zero: a quantidade de arestas de
            #      qualquer outro vértice ao vértice original.
            @constraint(model, sum(A[i, 1, :]) - sum(A[i, j, :]) >= 1 - M * (1 - C[i + 1]))
            @constraint(model, sum(A[i, 1, :]) - sum(A[i, j, :]) <= 1 + M * (1 - C[i + 1]))

        end

        # Par que restringe:
        #
        #   -> Ao valor de um: a quantidade de arestas de
        #      qualquer outro vértice ao vértice destino.
        #   -> Ao valor de zero: a quantidade de arestas do
        #      vértice destino à qualquer outro vértice.
        @constraint(model, sum(A[i, i + 1, :]) - sum(A[i, :, i + 1]) >= -1 - M * (1 - C[i + 1]))
        @constraint(model, sum(A[i, i + 1, :]) - sum(A[i, :, i + 1]) <= -1 + M * (1 - C[i + 1]))
    end

    set_time_limit_sec(model, 60.0 * 5) # limite 5 minutos

    #   --------
    #   Objetivo
    #   --------
    @objective(model, Max, sum(C))

    println("===================")
    println("-> Modelo formulado:"); println("")
    print(model)
    println("==================="); println("")

    println("===================")
    println("-> Otimizando..."); println("")
    optimize!(model)
    println("==================="); println("")


end # module
