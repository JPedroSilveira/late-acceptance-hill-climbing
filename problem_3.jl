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
        # A
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

        for i = 2:size(data, 1)
            A[data[i, 1], data[i, 2]] = 1
            A[data[i, 2], data[i, 1]] = 1
        end # for

        G = Graph(A)
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
#     print_instance(problem)
    println("==================="); println("")


    #   ==========
    #   Formulação
    #   ==========


    model = Model(() -> Gurobi.Optimizer(grb_env))

    #   ---------
    #   Variáveis
    #   ---------
    n = size(vertices(problem.G), 1)
    @variable(model, C[1:n], Bin) # C: Define se um vértice possui uma caixa

    #   ----------
    #   Restrições
    #   ----------
    @constraint(model, C[1] == 0)

    #   --------
    #   Objetivo
    #   --------
    @objective(model, Max, sum(C))

    println("===================")
    println("-> Modelo formuado:"); println("")
    print(model)
    println("==================="); println("")

    println("===================")
    println("-> Otimizando..."); println("")
    optimize!(model)
    println("==================="); println("")


end # module
