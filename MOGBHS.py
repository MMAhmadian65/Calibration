import random
from AlgorithmMO import AlgorithmMO
from Individual import Individual
from Aimsun import Aimsun
import numpy as np
# This class extends and implements the abstract class {@ link AlgorithmMO} and his abstract methods.This class represents the Multi-objective global best harmony search algorithm if a local search algorithm isn't set, otherwise represents a memetic algorithm based on MOGBHS (as global search algorithm) and the choosen local search algorithm.


class MOGBHS (AlgorithmMO):

    # Constructor that initializes the { @ link AlgorithmMO} parameters and the MOGBHS parameters, also initializes the initial global population pseudo - randomly.
    # @ param funcion The fitness option.
    # @ param numImprovisations The number of improvisations (iterations) to be used in the run method.
    # @ param populationsize The size of the harmony memory (the population size).
    # @ param genes The length of the array of selected parameters to calibrate.
    # @ param HMCR The harmony memory considering rate.
    # @ param PARmin The pitch adjusting rate minimum value.
    # @ param PARmax The pitch adjusting rate maximum value.
    # @ param argv The array containing the ang file address and the replication id.

    def __init__(self, funcion, numImprovisations, populationsize, genes, HMCR, PARmin, PARmax, Range, argv):
        self.__PARmax = PARmax
        self.__PARmin = PARmin
        self.__HMCR = HMCR
        self.__rank = 0
        self.__argv = argv
        self._initializer(None, None, None, funcion, None, numImprovisations, populationsize, genes, Range)

    # This method allows the fast non - dominated sort.
    # @ param population The population to be sorted.

    def __calculateFastNonDominatedOrder(self, population):
        front1 = []
        F = []
        aux = []
        for p in population:
            p.SetOfDominants = []
            p.NumberOfDominated = 0
            p.Rank = -1
            for q in population:
                if p.dominate(q):
                    p.SetOfDominants.append(q);
                elif q.dominate(p): p.NumberOfDominated+= 1
            if p.NumberOfDominated == 0:
                p.Rank = 0
                front1.append(p)
        F.append(front1);
        aux.extend(front1);
        i = 0;
        while F[i]:
            temp = []
            for p in F[i]:
                for q in p.SetOfDominants:
                    q.NumberOfDominated = q.NumberOfDominated - 1
                    if q.NumberOfDominated == 0:
                        q.Rank = i + 1;
                        temp.append(q);
            i+= 1
            F.append(temp)
            aux.extend(temp)
        self._P = aux;
        return F

    # This method determines if exist or not, an harmony in the list parameter with the same NRMS fitness value of the newImprovisation harmony.
    # @ param list the list of harmonies (or individuals).
    # @ param newImprovisation the new harmony.
    # @ return true if anyMatch((list.iterator) -> iterator.NRMS == newImprovisation.NRMS), false otherwise.

    def __exist(self, list, newImprovisation):
        for i in list:
            if i.getAptitud() == newImprovisation.getAptitud():
                return True;
        return False;


    # This method allows calculation of crowding distance for members of a pareto front.
    # @ param population the population (front) for which the crowding distance to be calculated.
    # @ return the new population (front) with crowding distance calcualted for each individual.

    def __calculateCrowdingDistance(self, population):
            aux = [];
            for ind in population:
                ind.CrowdingDistance = 0.0
                aux.append(ind)
            individuals = self._Quicksort(aux, 0, 0, len(population) - 1)
            individuals[0].CrowdingDistance = float('inf');
            individuals[len(individuals) - 1].CrowdingDistance = float('inf');
            for i in range(1, len(individuals) - 1):
                individuals[i].CrowdingDistance += abs(individuals[i + 1].getVolume() - individuals[i - 1].getVolume()) / abs(
                        individuals[0].getVolume() - individuals[len(individuals) - 1].getVolume());
            individuals = self._Quicksort(individuals, 1, 0, len(population) - 1)
            individuals[0].CrowdingDistance = float('inf');
            individuals[len(individuals) - 1].CrowdingDistance = float('inf');
            for i in range(1, len(individuals) - 1):
                individuals[i].CrowdingDistance += abs(individuals[i + 1].getSpeed() - individuals[i - 1].getSpeed()) / abs(
                            individuals[0].getSpeed() - individuals[len(individuals) - 1].getSpeed());
            return individuals;
    
    #This method runs simulation for the given population
    def __runSimulation(self, population, scenario = False, noCalibration = False):
        aimsun = Aimsun(self.__argv, population, scenario, noCalibration)
        population = aimsun.run()
        del aimsun

    # This method runs the MOGBHS
    def run(self):
        
        scenario = False
        noCalibration = False
        if self._funcionAptitud.getwithoutCal() == None: noCalibration = True
        if self._funcionAptitud.getObserved() == None: scenario = True
        
        self.__runSimulation(self._P, scenario, noCalibration)
        if self._funcionAptitud.getwithoutCal() == None:
            self._setwithoutCal()
        if self._funcionAptitud.getObserved() == None:
            self._setObserved()
        F = [[]];
        self._funcionAptitud.evaluatePopulation(self._P)
        F = self.__calculateFastNonDominatedOrder(self._P);
        self.__replacement(F)
        self._plotActualvsSimulated(0)
        self._plotGEH(0)
        print("Here is the initial population sorted based on pareto fronts:")
        for p in self._P:
            print(p.data)
            print(p.getVolume())
            print(p.getSpeed())
            print(p.Rank)
            print(p.CrowdingDistance)
        self.__calculateFirstRankNumber(self._P);
        bestIndex = self._TOPSIS()
        
        for generations in range(self._numIteraciones):

            par = self.__PARmin + (((self.__PARmax - self.__PARmin) / self._numIteraciones) * generations);
            print("Time to generate new harmonies")
            self.__generateNewHarmonies(self._populationsize, par, bestIndex)
            print("Here are harmonies generated:")
            for p in self._Q:
                print(p.data)
            print("Now let's evaluate them:")
            self.__runSimulation(self._Q)
            self._funcionAptitud.evaluatePopulation(self._Q);
            self._R = self._P + self._Q
            self._Q = []

            #Selection of next generation
            F = self.__calculateFastNonDominatedOrder(self._R);
            self.__replacement(F)
            print("Here is the new population sorted based on pareto fronts and crowding distance values:")
            for p in self._P:
                print(p.data)
                print(p.getVolume())
                print(p.getSpeed())
                print(p.Rank)
                print(p.CrowdingDistance)
            self.__calculateFirstRankNumber(self._P)
            bestIndex = self._TOPSIS()
            self._R = []

        print(self._progress)
        self._plotConvergence()
        self._plotActualvsSimulated(bestIndex)
        self._plotGEH(bestIndex)
        self._plotPareto(False, False)


        return self._P;


    # This method generates new harmonies (solutions)
    # @param numThreads number of threads
    # @param par the hyperparameter PAR
    def __generateNewHarmonies(self, numThreads, par, best):
        for i in range(numThreads):
            ind = Individual(self._funcionAptitud, self._genes);
            sol = []
            for dimension in range(self._genes):
                if random.random() < self.__HMCR:
                    initial = 0
                    if self.__rank < self._populationsize - 1: initial = self.__rank
                    value = self._P[random.randint(initial, self._populationsize - 1)].data[dimension];
                    if (random.random() < par): value = self._P[best].data[dimension]
                    sol.append(value);
                else:
                    value = self._P[random.randint(0, self.__rank - 1)].data[dimension];
                    condition = True
                    while condition:
                        a = 0
                        if random.random() < 0.5:
                            a = random.random()
                        else:
                            a = -1 * random.random()
                        value = round(value + a, 2)
                        if value >= self._range[dimension][0] and value <= self._range[dimension][1]:
                            condition = False
                        else:
                            condition = True
                    sol.append(value);
            ind.data = sol
            self._Q.append(ind)

    # This method froms the new population
    # @param F, a list contaning all the pareto fronts
    def __replacement(self, F):
        Pt1 = []
        i = 0;
        while len(Pt1) + len(F[i]) < self._populationsize:
            self.__calculateCrowdingDistance(F[i])
            F[i].sort(key=lambda Individual: Individual.CrowdingDistance, reverse=True)
            Pt1.extend(F[i]);
            i += 1;
        self.__calculateCrowdingDistance(F[i])
        F[i].sort(key=lambda Individual: Individual.CrowdingDistance, reverse=True)
        Pt1.extend(F[i][0:self._populationsize - len(Pt1)])
        self._P = Pt1


    # This method updates the rank attribute used to determine the number of individuals on the first pareto front.
    # @ param list The list of individuals.

    def __calculateFirstRankNumber(self, list):
        self.__rank = 0
        for ind in list:
            if ind.Rank == 0: self.__rank += 1








