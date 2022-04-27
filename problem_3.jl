# import Pkg;
# Pkg.add("JuMP")
# Pkg.add("GLPK")
# Pkg.add("Formatting")
# Pkg.add("DelimitedFiles")
# Pkg.add("LightGraphs")
# Pkg.add("BenchmarkTools")

using JuMP
using GLPK
using Formatting
using LinearAlgebra

module PROBLEM_3
    using DelimitedFiles
    using LightGraphs
    using BenchmarkTools

    #
    #   Definição de estruturas
    #   e funções auxiliares
    #

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

    #
    #   Leitura de dados
    #

    data = readdlm("instances/instance_12_17.dat", ' ', UInt)
#     data = readdlm("instances/instance_100_180.dat", ' ', UInt)
#     data = readdlm("instances/instance_200_1980.dat", ' ', UInt)
#     data = readdlm("instances/instance_500_6225.dat", ' ', UInt)
#     data = readdlm("instances/instance_10000_19800.dat", ' ', UInt)

    problem = @btime(build_instance(data))
    print_instance(problem)

    #
    #   Formulação
    #

    # C: Define se um vértice possui uma caixa
    # @variable(model, C[1:n], Bin)

end # module
