import numpy as np

# This concrete class represents a individual or harmony (contains a solution to the problem of calibration)

class Individual:
    
    # Constructor that receives a fitness option and the number of parameters (dimensions or genes) of the model to be calibrated.
    # @ param funcion the fitness option.
    # @ param genes the number of parameters of the model to be calibrated.
    def __init__(self, function, genes):
        self.funcion = function
        self.__Speed = -1.0
        self.__Volume = -1.0
        self.__NRMS = -1.0
        self.output_model = None;
        self.Rank = -1
        self.NumberOfDominated = 0
        self.CrowdingDistance = 0.0
        self.SetOfDominants = []
        self.data = None
        if (genes > 0):
            self.data = np.zeros(shape=(genes));


    # This method checks if the individual domainates another individual.
    # @ param ind the other individual.
    # @ return true if self domainates otro according to fitness option (maximize or minimize), false otherwise.

    def dominate(self, ind):
        if not self.funcion.isMaximize():
            if (self.getVolume() > ind.getVolume() or self.getSpeed() > ind.getSpeed()):
                return False;
            if (self.getSpeed() < ind.getSpeed() or self.getVolume() < ind.getVolume()):
                return True;
        else:
            if (self.getVolume() < ind.getVolume() or self.getSpeed() < ind.getSpeed()):
                return False;
            if (self.getSpeed() > ind.getSpeed() or self.getVolume() > ind.getVolume()):
                return True;

        return False;

    # This method clears the fitness values of the individual.

    def clearFitness(self):
        self.__NRMS = -1;
        self.__Speed = -1;
        self.__Volume = -1;

    # This method sets( if the NRMS value is -1) and returns the NRMS value of the individual.
    # @ return the value of NRMS.

    def getNRMS(self):
        if self.__NRMS == -1:
            self.__NRMS = self.funcion.evaluate(self);
        return self.__NRMS;

    # This method sets (if the Volume value is -1) and returns the Volume value of the individual.
    # @ return the value of Volume.

    def getVolume(self):
        if self.__Volume == -1:
            self.__Volume = self.funcion.evaluateObjetive1(self);
        return self.__Volume;

    # This method returns the Speed value of the individual.
    # @ return the value of Speed.

    def getSpeed(self):
        if self.__Speed == -1:
            self.__Speed = self.funcion.evaluateObjetive2(self);
        return self.__Speed;


    # Gets the rank number of the individual.
    # @ return the rank number (if assigned), otherwise return -1.

    def getRank(self):
        return self.Rank

    # Sets the rank number of the individual.
    # @ param Rank the new rank number to be assigned to the individual.

    def setRank(self, Rank):
        self.Rank = Rank

    # Sets the Speed value of the individual.
    # @ param Speed the new Speed value to be assigned to the individual.

    def setSpeed(self, Speed):
        self.__Speed = Speed

    # Sets the Volume value of the individual.
    # @ param Volume the new Volume value to be assigned to the individual.

    def setVolume(self, Volume):
        self.__Volume = Volume

    # Sets the NRMS value of the individual.
    # @ param NRMS the new NRMS value to be assigned to the individual.

    def setNRMS(self, NRMS):
        this.__NRMS = NRMS;

