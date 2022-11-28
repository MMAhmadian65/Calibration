from abc import ABCMeta, abstractmethod



 # This abstract class represents an abstract algorithm class, which is extended by a concrete algorithm.

class Algorithm():
    __metaclass__ = ABCMeta

    def __init__():
        self._funcionAptitud = 0;

    # This method sets the initial seed to run the algorithm.
    # @ param seed - The initial seed.

    def setSeed(self, seed):
        self._seed = seed;

    # Sets the fitness landscape algorithm.
    # @ param funcionAptitud The new fitness landscape algorithm.

    def setFuncionAptitud(self, funcionAptitud):
        self._funcionAptitud = funcionAptitud;


    # Gets the fitness landscape algorithm.
    # @ return The current fitness landscape algorithm.

    def getFuncionAptitud(self):
        return self._funcionAptitud;


     # Gets the best individual.
     # @return The current best individual.

    def getBest(self):
        return self._Best;


     # Sets the worst best individual found in the {@link Algoritmo#multiRun(int) multiRun} method.
     # @param Worst The new worst best individual.

    def setWorst(self, Worst):
        self._Worst = Worst;


     # Gets the worst best individual found in the {@link Algoritmo#multiRun(int) multiRun} method.
     # @return The worst best individual.

    def getWorst(self):
        return self._Worst;


     # Sets the best individual found in the {@link Algoritmo#run() run} and {@link Algoritmo#multiRun(int) multiRun} methods.
     # @param Best The new best individual.

    def setBest(self, Best):
        self._Best = Best;


     # Returns the quality of one individual depending the {@link PaisajeAptitud#esMaximizar() esMaximizar} method.
     # @param i The individual whom is to be calculated the quality.
     # @return The quality of the individual.

    def Quality(self, i):
        if (funcionAptitud.esMaximizar()): return i.getAptitud();
        else: return Integer.MAX_VALUE - i.getAptitud();


     # This method orders an array of {@link Individuo} according to the {@link PaisajeAptitud#esMaximizar() esMaximizar} method.
     # @param elements The array of {@link Individuo}.
     # @param opc If this parameter is equals to <code>0</code> the elements are ordered by Volume fitness value, otherwise by the Speed fitness value.
     # @param left Index that represents the left border of the array.
     # @param right Index that represents the right border of the array.
     # @return The array of {@link Individuo} ordered according to the {@link PaisajeAptitud#esMaximizar() esMaximizar} method and the <code>opc</code> parameter.

    def _Quicksort(self, elements, opc, left, right):
        i = left
        j = right
        pivot = elements[(left + right) / 2];
        while (i <= j):
            if (opc == 0):
                if (not self._funcionAptitud.isMaximize()):
                    while (elements[i].getVolume() > pivot.getVolume()): i += 1
                    while (elements[j].getVolume() < pivot.getVolume()): j -= 1
                else:
                    while (elements[i].getVolume() < pivot.getVolume()): i+= 1
                    while (elements[j].getVolume() > pivot.getVolume()): j-= 1
            else:
                if (not self._funcionAptitud.isMaximize()):
                    while (elements[i].getSpeed() > pivot.getSpeed()): i+= 1
                    while (elements[j].getSpeed() < pivot.getSpeed()): j-= 1
                else:
                    while (elements[i].getSpeed() < pivot.getSpeed()): i+= 1
                    while (elements[j].getSpeed() > pivot.getSpeed()): j-= 1
            if (i <= j):
                tmp = elements[i];
                elements[i] = elements[j];
                elements[j] = tmp;
                i+= 1
                j-= 1
        if (left < j): self._Quicksort(elements, opc, left, j);
        if (i < right): self._Quicksort(elements, opc, i, right);
        return elements;

     # Function to know the run time of a algorithm
     # @param milliseconds The miliseconds value.
     # @return The <code>String</code>: "<i>hours</i>:<i>minutes</i>:<i>seconds</i>"

    def runTime(self, milliseconds):
        sec = milliseconds / 1000.0
        hour = sec / 3600;
        minutes = (sec - (3600 * hour)) / 60;
        seconds = sec - ((hour * 3600) + (minutes * 60));
        return hour + ":" + minutes + ":" + seconds;
