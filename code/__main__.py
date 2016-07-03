#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@data 17/10/2013
@author: Douglas Ferreira de Borba
@comment: para a execução do programa é necessário a
          instalação da biblioteca matplotlib
'''

from math import sqrt
from matplotlib.pyplot import plot, title, show, annotate
from random import random, randrange


def euclidean_distance(source, target):
    '''Calcula a distância euclidiana'''
    return sqrt((source[0] - target[0]) ** 2 + (source[1] - target[1]) ** 2)


def path_distance(permutation, cities):
    '''Calcula a distância total do caminho'''
    distance = 0
    for source in permutation:
        if permutation.index(source) == (len(permutation) - 1):
            target = permutation[0]
        else:
            target = permutation[permutation.index(source) + 1]
        distance += euclidean_distance(cities[source], cities[target])
    return distance


def random_permutation(cities):
    '''Gera randomicamente a primeira solução'''
    permutation = range(len(cities))
    for index in range(len(permutation)):
        position = randrange(len(permutation) - index) + index
        permutation[position], permutation[index] = permutation[
            index], permutation[position]
    return permutation


def initialise_pheromone_matrix(num_ants, num_cities, path_cost):
    '''Inicializa a matriz de ferômonios'''
    pheromone_matrix = [[(num_ants / path_cost) for i in range(num_cities)]
                        for j in range(num_cities)]
    for index_i in range(len(pheromone_matrix)):
        pheromone_matrix[index_i][index_i] = 0
    return pheromone_matrix


def calculate_choices(cities, last_city, exclude, pheromone_matrix,
                      beta, alfa):
    '''Calcula a probabilidade de cada cidade ser selecionada'''
    choices = []
    for city in cities:
        index = cities.index(city)
        if index in exclude:
            continue
        probability = {'city': index}
        probability.update({'history': (pheromone_matrix[last_city][index]) **
                            alfa})
        probability.update(
            {'distance': euclidean_distance(cities[last_city], city)})
        probability.update(
            {'heuristic': (1.0 / probability['distance']) ** beta})
        probability.update(
            {'probability': probability['history'] * probability['heuristic']})
        choices.append(probability)
    return choices


def select_next_city(possible_cities):
    '''Seleciona da próxima cidade conforme sua probabilidade'''
    probability_sum = 0.0
    for city in possible_cities:
        probability_sum += city['probability']
    if probability_sum == 0.0:
        return possible_cities[randrange(len(possible_cities))]['city']
    v = random()
    for city in possible_cities:
        v -= (city['probability'] / probability_sum)
        if v <= 0.0:
            return city['city']
    return possible_cities[-1]['city']


def stepwise_const(cities, pheromone_matrix, beta, alfa):
    '''Seleciona aleatóriamente uma cidade de partida'''
    permutation = []
    permutation.append(randrange(len(cities)))
    while True:
        choices = calculate_choices(
            cities, permutation[-1], permutation, pheromone_matrix, beta, alfa)
        permutation.append(select_next_city(choices))
        if len(permutation) == len(cities):
            break
    return permutation


def evaporation_pheromone(pheromone_matrix, evaporation_rate):
    '''Executa a evaporação dos feromônios depositados'''
    for line in pheromone_matrix:
        for value in line:
            value = (1.0 - evaporation_rate) * value


def update_pheromone(pheromone_matrix, solutions):
    '''Atualiza os feromônios depositados'''
    for solution in solutions:
        for x in solution['path']:
            if solution['path'].index(x) == len(solution['path']) - 1:
                y = solution['path'][0]
            else:
                y = solution['path'][solution['path'].index(x) + 1]
            pheromone_matrix[x][y] += (1.0 / solution['cost'])
            pheromone_matrix[y][x] += (1.0 / solution['cost'])


def extract_cities(file):
    '''Extrai as cidade do arquivo de entrada'''
    cities = []
    for line in open(file, 'r'):
        if line[0].isdigit():
            cities.append([float(value)
                          for value in line.split()[1:]])
    return cities


def search(cities, max_it, num_ants, evaporation_rate, beta, alfa):
    '''Busca a melhor solução para o problema'''
    '''Comente a linha 150 e descomente a linha 154 para Ant System'''

    best = {'path': random_permutation(cities)}
    best.update({'cost': path_distance(best['path'], cities)})
    pheromone_matrix = initialise_pheromone_matrix(
        num_ants, len(cities), best['cost'])
    index_i = 0
    while index_i < max_it:
        print "Colony [" + str(index_i + 1) + "]: "
        solutions = []
        index_j = 0
        while index_j < num_ants:
            candidate = {}
            candidate.update(
                {'path': stepwise_const(cities, pheromone_matrix, beta, alfa)})
            candidate.update(
                {'cost': path_distance(candidate['path'], cities)})
            print "Ant [" + str(index_j + 1) + "]: " + str(candidate)
            solutions.append(candidate)
            if candidate['cost'] < best['cost']:
                best = candidate
            index_j += 1
        # solutions.append(best)
        evaporation_pheromone(pheromone_matrix, evaporation_rate)
        update_pheromone(pheromone_matrix, solutions)
        index_i += 1
        print "Best Ant [" + str(index_j + 1) + "]: " + str(best) + "\n"
    return best


def plot_solution(cities, best):
    '''Plota o gráfico da solução'''
    p = [cities[index]
         for index in best['path']] + [[cities[best['path'][0]][0],
                                       cities[best['path'][0]][1]]]
    title("Custo Total do Caminho: " + str(best['cost']) + "\n")
    plot(*zip(*p), color='green', marker='s', linestyle='-')
    for index in range(len(p) - 1):
        annotate(index + 1, (cities[best['path'][index]][0],
                             cities[best['path'][index]][1]))
    show()


if __name__ == "__main__":
    '''Configurações do algoritmo'''
    num_colonies, num_ants = 500, 200
    evaporation_rate, beta, alfa = 0.6, 5.0, 5.0
    cities = extract_cities("instances\\oliver30.tsp")
    best = search(cities, num_colonies, num_ants, evaporation_rate, beta, alfa)
    print "Solution: " + str(best)
    # plot_solution(cities, best)
