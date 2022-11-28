# -*- coding: utf-8 -*-
from __future__ import division
import random
import os
import sys
import math
SITEPACKAGES = "C:\\Python27\\Lib\\site-packages"
sys.path.append(SITEPACKAGES)
import csv
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from topsis import Topsis
import numpy as np

from abc import ABCMeta, abstractmethod
from Algorithm import Algorithm
from Individual import Individual


#  This abstract class represents a Multi-Objective algorithm extending the Algorithm class and overrides the implementation of the run method.

class AlgorithmMO(Algorithm):
    __metaclass__ = ABCMeta


    #  This abstract method overrides the run method in Algorithm class which allows the execution of the multi-objective algorithm according to concrete class that implements it.

    @abstractmethod
    def run(self):
        pass

    #  * This method allows the initialization of all algorithms, linking the crossing, mutation, selection, replacement and fitness algorithms to the concrete class. Also sets the population size, the genes array size and the number of iterations. This method calls the AlgorithmMO::_initializer() method which generates the initial pseudo-random population.
    #  * @param range a matrix containing the range for each parameter.
    #  * @param funcionCruce the crossing algorithm.
    #  * @param funcionMutacion the mutation algorithm.
    #  * @param funcionSeleccion the selection algorithm.
    #  * @param funcionAptitud the fitness landscape algorithm.
    #  * @param funcionReemplazo the replace algorithm.
    #  * @param numIteraciones the iteration number to runs the multi-objective algorithm.
    #  * @param poblacion the population size.
    #  * @param cantidadGenes the genes array size.

    def _initializer(self, funcionCruce, funcionMutacion, funcionSeleccion, funcionAptitud, funcionReemplazo, numIteraciones, poblacion, cantidadGenes, Range):
        self._range = Range;
        self._funcionCruce = funcionCruce;
        self._funcionMutacion = funcionMutacion;
        self._funcionSeleccion = funcionSeleccion;
        self._funcionAptitud = funcionAptitud;
        self._funcionReemplazo = funcionReemplazo;
        self._numIteraciones = numIteraciones;
        self._genes = cantidadGenes;
        self._populationsize = poblacion;
        self._Q = [];
        self._P = [];
        self._R = [];
        self._progress = []
        if self._funcionAptitud.getwithoutCal() == None:
            self._populationsize = self._populationsize + 1
        if self._funcionAptitud.getObserved() == None:
            self._populationsize = self._populationsize + 1
        self._initialPopulation()

    #  This method generates a population of pseudo-randomly generated individuals, the population have size: <code>tamanoPoblacion</code>, and the first element is obtained from the trf file.<br><br><b>See:</b> {@link AlgoritmoMO#inicializarGenes(DOMAIN.ABSTRACT.Individuo, DOMAIN.ABSTRACT.Individuo) inicializarGenes}

    def _initialPopulation(self):
        self.setBest(Individual(self._funcionAptitud, -1));
        indicator = 0
        for i in range(self._populationsize):
            ind = Individual(self._funcionAptitud, self._range.shape[0])
            if self._funcionAptitud.getwithoutCal() == None and i == 0:
                self.__initialGenes(ind, -1)
            elif self._funcionAptitud.getObserved() == None and i == 1:
                self.__initialGenes(ind, 2)
            else:
                self.__initialGenes(ind)
            self._P.append(ind);
        for i in self._P:
            print (i.data)


    #  This method initialize all genes of the individual with a pseudo-random number, according to the given range for each parameter.
    #  @param ind The individual to be initialized.

    def __initialGenes(self, ind, indicator = 0):

        sol = []
        for i in range(ind.data.shape[0]):
            start = self._range[i][0]
            stop = self._range[i][1]

            if indicator == -1:
                stop = 1.05 * start
            if indicator == 1:
                start = 0.95 * stop
            if indicator == 2:
                mean = start + (stop - start) / 2
                start = 0.95 * mean
                stop = 1.05 * mean
            sol.append(round(start + random.random() * (stop - start), 2));
        ind.data = sol

    def __readPopulation(self):
        X_axis = []  # X
        Y_axis = []  # Y
        for ind in self._P:
            X_axis.append(ind.getVolume())
            Y_axis.append(ind.getSpeed())

        return X_axis, Y_axis

    # Sets the simulated values without calibration
    def _setwithoutCal(self):
        self._funcionAptitud.setwithoutCal(self._P[0].output_model)
        del self._P[0]
        self._populationsize = len(self._P)

    # Sets the observed values
    def _setObserved(self):
        self._funcionAptitud.setObserved(self._P[0].output_model)
        del self._P[0]
        self._populationsize = len(self._P)

    # This method selects a single solution from solutions on first pareto front using TOPSIS
    def _TOPSIS(self):
        prog = []
        Pareto = []
        for p in self._P:
            if p.Rank == 0:
                objectives = []
                objectives.append(p.getVolume())
                objectives.append(p.getSpeed())
                Pareto.append(objectives)
            else:
                break

        evaluation_matrix = np.array(Pareto)

        print(evaluation_matrix)
        weights = [5, 5]

        '''
        if higher value is preferred - True
        if lower value is preferred - False
        '''
        criteria = np.array([False, False])

        t = Topsis(evaluation_matrix, weights, criteria)
        t.calc()

        print("best_distance\t", t.best_distance)
        print("worst_distance\t", t.worst_distance)

        # print("weighted_normalized",t.weighted_normalized)

        print("worst_similarity\t", t.worst_similarity)
        print("rank_to_worst_similarity\t", t.rank_to_worst_similarity())

        print("best_similarity\t", t.best_similarity)
        print("rank_to_best_similarity\t", t.rank_to_best_similarity())

        rank_to_best_similarity = t.rank_to_best_similarity()

        print(rank_to_best_similarity[0])
        prog.append(self._P[rank_to_best_similarity[0] - 1].getVolume())
        prog.append(self._P[rank_to_best_similarity[0] - 1].getSpeed())
        if len(self._progress) == 0:
            self._progress.append(prog)
        else:
            if prog[0] < self._progress[-1][0] and prog[1] < self._progress[-1][1]:
                self._progress.append(prog)
            else:
                prog = []
                prog.append(self._progress[-1][0])
                prog.append(self._progress[-1][1])
                self._progress.append(prog)
        return rank_to_best_similarity[0] - 1

    def _plotConvergence(self):

        iter = []
        iter.extend(range(0, len(self._progress)))
        data = np.array(self._progress)

        for k in range(0, 2):

            if k == 0:
                plt.plot(iter, data[:, 0], 'o-')
                #plt.xticks(range(len(iter)), iter)
                ylabel = "NRMS(volume)"

            else:
                plt.plot(iter, data[:, 1], 'o-')
                #plt.xticks(range(len(iter)), iter)
                ylabel = "NRMS(speed)"

            xlabel = "Iteration"
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            dir = "C:\\Users\\ahmadiam\\Desktop\\"
            address = None
            if k == 0:
                address = dir + "VolumeCon.png"
            else:
                address = dir + "SpeedCon.png"

            plt.savefig(address, dpi=600)
            plt.clf()

        

    # This method plots actual and simulated speed and volume for calibrated and not calibrated parameters
    def _plotActualvsSimulated(self, bestIndex):
        print("The best index is:")
        print(bestIndex)
        actual = self._funcionAptitud.getObserved()
        withoutCal = self._funcionAptitud.getwithoutCal()
        best = self._P[bestIndex].output_model
        
        for k in range(0, 2):
            x = []
            y = []
            z = []
            sum = 0
            initial = 0
            final = 0
            for j in range(len(best.keys())):
                for i in range(len(best.values()[j][k])):
                    if (actual.values()[j][k][i] > 0):
                        sum += 1
                        ac30 = actual.values()[j][k][i] * math.sqrt(3) / 3
                        ac60 = actual.values()[j][k][i] * math.sqrt(3)
                        if withoutCal.values()[j][k][i] > ac30 and withoutCal.values()[j][k][i] < ac60: initial += 1
                        if best.values()[j][k][i] > ac30 and best.values()[j][k][i] < ac60: final += 1
                        x.append(best.values()[j][k][i])
                        y.append(actual.values()[j][k][i])
                        z.append(withoutCal.values()[j][k][i])


            percent1 = round((initial / sum) * 100, 2)
            percent2 = round((final / sum) * 100, 2)
            degree_sign = u"\N{DEGREE SIGN}"
            string1 = "After calibration- (within $\pm$15" + degree_sign + ": " + str(percent2) + "%)"
            string2 = "Before calibration- (within $\pm$15" + degree_sign + ": " + str(percent1) + "%)"
            fig, ax = plt.subplots()
            ax.scatter(y, x, color=['blue'], label=string1)
            ax.scatter(y, z, color=['red'], label=string2)
            
            lims = [
                np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
                np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
            ]

            ylims30 = np.zeros(len(lims))
            ylims60 = np.zeros(len(lims))
            for i in range(len(lims)):
                ylims30[i] = np.sqrt(3) / 3 * lims[i]
                ylims60[i] = np.sqrt(3) * lims[i]

            # now plot both limits against eachother
            ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
            ax.plot(lims, ylims60, 'k-', alpha=0.75, zorder=0, linestyle='dashed')
            ax.plot(lims, ylims30, 'k-', alpha=0.75, zorder=0, linestyle='dashed')
            ax.set_aspect('equal')
            ax.set_xlim(lims)
            ax.set_ylim(lims)
            xlabel = None
            ylabel = None
            if k == 0:
                xlabel = "Actual speed"
                ylabel = "Simulated speed"
            else:
                xlabel = "Actual volume"
                ylabel = "Simulated volume"
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            dir = "C:\\Users\\ahmadiam\\Desktop\\"
            address = None
            if k == 0:
                address = dir + "Speed.png"
            else:
                address = dir + "Volume.png"

            # Shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.65, box.height ])

            # Put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                      fancybox=True, shadow=True, ncol=1, prop={'size': 4})
            #plt.legend(loc='upper left');

            fig.savefig(address, dpi=300)
            plt.clf()

    def _plotGEH(self, bestIndex):
        print("The best index is:")
        print(bestIndex)
        actual = self._funcionAptitud.getObserved()
        withoutCal = self._funcionAptitud.getwithoutCal()
        best = self._P[bestIndex].output_model

        for k in range(0, 2):
            x = []
            y = []
            z = []
            for j in range(len(best.keys())):
                for i in range(len(best.values()[j][k])):
                    if (actual.values()[j][k][i] > 0):
                        x.append(best.values()[j][k][i])
                        y.append(actual.values()[j][k][i])
                        z.append(withoutCal.values()[j][k][i])
                    
            before = []
            after = []
            iter = []
            iter.extend(range(1, len(y) + 1))
            for j in range(0, len(y)):
                before.append(math.sqrt((2 * (y[j] - z[j]) ** 2) / (y[j] + z[j])))
                after.append(math.sqrt((2 * (y[j] - x[j]) ** 2) / (y[j] + x[j])))

            fig, ax = plt.subplots()
            ax.plot(iter, before, 'k-', alpha=0.75, zorder=0, color="red", linestyle='dashed', label="Before calibration")
            ax.plot(iter, after, 'k-', alpha=0.75, zorder=0, label="After calibration", color="blue")


            xlabel = "Section number"
            ylabel = None
            if k == 0:
                ylabel = "GEH(speed)"
            else:
                ylabel = "GEH(volume)"
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            dir = "C:\\Users\\ahmadiam\\Desktop\\"
            address = None
            if k == 0:
                address = dir + "GEHSpeed.png"
            else:
                address = dir + "GEHVolume.png"

            # Shrink current axis by 20%
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + 0.3, box.width, box.height  * 0.5])

            # Put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25),
                      fancybox=True, shadow=True, ncol=1, prop={'size': 4})
            # plt.legend(loc='upper left');

            fig.savefig(address, dpi=300)
            plt.clf()
                
    
    # Method to take two equally-sized lists and return just the elements which lie
    # on the Pareto frontier, sorted into order.
    # Default behaviour is to find the maximum for both X and Y, but the option is
    # available to specify maxX = False or maxY = False to find the minimum for either
    # or both of the parameters.

    def _plotPareto(self, maxX = True, maxY = True):
        Xs, Ys= self.__readPopulation()

        # Sort the list in either ascending or descending order of X
        myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
        # Start the Pareto frontier with the first value in the sorted list
        p_front = [myList[0]]
        # Loop through the sorted list
        for pair in myList[1:]:
            if maxY:
                if pair[1] >= p_front[-1][1]:  # Look for higher values of Y…
                    p_front.append(pair)  # … and add them to the Pareto frontier
            else:
                if pair[1] <= p_front[-1][1]:  # Look for lower values of Y…
                    p_front.append(pair)  # … and add them to the Pareto frontier
        # Turn resulting pairs back into a list of Xs and Ys
        p_frontX = [pair[0] for pair in p_front]
        p_frontY = [pair[1] for pair in p_front]
        # Plot a scatter graph of all results
        plt.scatter(Xs, Ys)
        # Then plot the Pareto frontier on top
        plt.plot(p_frontX, p_frontY)

        plt.xlabel("Volume")
        plt.ylabel("Speed")
        Figname = "C:\\Users\\ahmadiam\\Desktop\\Pareto.png"
        plt.savefig(Figname, dpi=600)





