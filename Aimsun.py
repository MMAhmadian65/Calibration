import sys
import os
import time
import csv
import random
import math
import random

from PyANGBasic import *
from PyANGKernel import *
from PyANGConsole import *
from Individual import Individual


SITEPACKAGES = "C:\\Python27\\Lib\\site-packages"
sys.path.append(SITEPACKAGES)
import pandas as pd
import numpy as np

from collections import OrderedDict

import sqlite3
from sqlite3 import Error

def QString():
    pass

class Aimsun:

    #This method initializes the class with the ang file address, replication id and matrix (pop) containing the clibration vector
    # @ param argv: argv[1]: the ang file address, argv[2]: replication id
    # @ param the population (each vector in the population contains the calibration parameters to be set)
    def __init__(self, argv, P, scenario = False, noCalibration = False):

        if len(argv) != 2:
            print ("Usage: aconsole -script %s ANG_FILE_NAME" % argv[0])
            return -1

        self.__angFileName = argv[1]
        self.__pop = P
        self.__calibScenario = "calibScenario"
        self.__calibExperiment = "calibExperiment"
        self.__calibAverage = "calibAverage"
        self.__noCalibration = noCalibration
        if scenario:
            self.__createCalibrationScenario()
        else:
            self.__angFileName = "C:\\Users\\ahmadiam\\Desktop\\Sample\\tmp.ang"

    #This method destructs an instance of Aimsun
    def __del__(self):
        print('Destructor called, Aimsun deleted.')

    # This function returns the demand folder
    # @param model: GK model
    # @return: Folder object
    def __getDemandFolder(self, model):
        folderName = "GKModel::trafficDemand"
        folder = model.getCreateRootFolder().findFolder(folderName)
        if folder is None:
            folder = GKSystem.getSystem().createFolder(
                model.getCreateRootFolder(), folderName)
        return folder

    # This method returns the folder object for the scenarios
    # @param model: GK Model
    # @return: return the folder
    def __getScenariosFolder(self, model):

        folderName = "GKModel::top::scenarios"
        folder = model.getCreateRootFolder().findFolder(folderName)
        if folder is None:
            folder = GKSystem.getSystem().createFolder(
                model.getCreateRootFolder(), folderName)
        return folder

    def __setupScenario(self, model):

        scenario = GKSystem.getSystem().newObject("GKScenario", model)
        scenario.setName(self.__calibScenario)

        demand = model.getType("GKTrafficDemand")
        demandId = None
        for types in model.getCatalog().getUsedSubTypesFromType(demand):
            for s in types.itervalues():
                demandId = s.getId()

        print(demandId)

        demand = model.getCatalog().find(demandId)

        demand.setDataValueByID(GKTrafficDemand.fromAtt, 2)
        demand.setDataValueByID(GKTrafficDemand.durationAtt, 2)

        folder = self.__getDemandFolder(model)
        folder.append(demand)

        scenario.setDemand(demand)

        plan = model.getType("GKPublicLinePlan")
        planId = None
        for types in model.getCatalog().getUsedSubTypesFromType(plan):
            for s in types.itervalues():
                planId = s.getId()

        print(planId)

        plan = model.getCatalog().find(planId)

        scenario.setPublicLinePlan(plan)

        masterPlan = model.getType("GKMasterControlPlan")
        masterPlanId = None
        for types in model.getCatalog().getUsedSubTypesFromType(masterPlan):
            for s in types.itervalues():
                masterPlanId = s.getId()

        print(masterPlanId)

        masterPlan = model.getCatalog().find(masterPlanId)

        scenario.setMasterControlPlan(masterPlan)
        date = pd.datetime(2022,1,1)
        scenario.setDate(date)

        paras = scenario.getInputData()
        paras.setDetectionInterval(GKTimeDuration.fromString("00:10:00"))
        paras.setStatisticalInterval(GKTimeDuration.fromString("00:10:00"))
        paras.enableStoreStatistics(True)
        paras.enableStoreDetection(True)
        paras.setKeepPathsInMemory(False)
        paras.setSectionLanesStatistics(True)
        paras.setTurnsStatistics(True)

    def __setupExperiment(self, model):

        print('\nSetting up experiment...\n')

        scenario = model.getCatalog().findByName(self.__calibScenario)
        experiment = GKSystem.getSystem().newObject("GKExperiment", model)
        experiment.setName(self.__calibExperiment)

        experiment.setScenario(scenario)

    def __setupReplication(self, model, num_rep):

        experiment = model.getCatalog().findByName(self.__calibExperiment)
        rep = []

        for i in range(0, num_rep):
            replication = GKSystem.getSystem().newObject("GKReplication", model)
            repName = "calibReplication" + str(i)
            replication.setName(repName)
            replication.setExperiment(experiment)
            experiment.addReplication(replication)
            rep.append(replication)

        replication_list = rep

        for replication in replication_list:
            experiment.addReplication(replication)

        # create the average experiment result
        avg_result = GKSystem.getSystem().newObject("GKExperimentResult", model)
        avg_result.setName(self.__calibAverage)

        # add replcations to the average
        for replication in experiment.getReplications():
            avg_result.addReplication(replication)
        experiment.addReplication(avg_result)

    def __createCalibrationScenario(self):
        self.__createLogfile()
        # Start a Console
        console = ANGConsole()

        # Load a network
        if console.open(self.__angFileName):
            model = GKSystem.getSystem().getActiveModel()
            print("A scenario, an experiment and one replications are created!")
            self.__setupScenario(model)
            self.__setupExperiment(model)
            self.__setupReplication(model, 1)
            scenario = model.getCatalog().findByName(self.__calibScenario)
            experiment = model.getCatalog().findByName(self.__calibExperiment)
            scenario.addExperiment(experiment)

            # attach the new scenario to folder
            folder = self.__getScenariosFolder(model)
            folder.append(scenario)
            console.save("C:\\Users\\ahmadiam\\Desktop\\Sample\\tmp.ang")
            self.__angFileName = "C:\\Users\\ahmadiam\\Desktop\\Sample\\tmp.ang"
            console.close()
            fileLog.close()
        else:
            fileLog.write("Cannot load the network\n")
            fileLog.flush()
            console.getLog().addError("Cannot load the network")
            return -1



    # This method reads the speed and flow for each from data_origin (a average_result type)
    # @param model: GK Model
    # @param data_origin: a list of replications:
    #         [a replication or the average_result (which is a subtype of GKReplication)]
    # @return: a dict, avg_data[sector_name] = [[speed],[flow]]
    def __read_sector_data(self, model, replication_list):

        rep_data = OrderedDict()

        sec_type = model.getType("GKDetector")
        # read data for each replication and then the average
        for replication in replication_list:

            print('\nReading Replication data: {0}'.format(replication.getId()))

            # get the column id
            speedColumn = sec_type.getColumn(GK.BuildContents(GKColumnIds.eSpeed, replication, None))
            flowColumn = sec_type.getColumn(GK.BuildContents(GKColumnIds.eFlow, replication, None))

            # read each detector
            for sec in model.getCatalog().getObjectsByType(sec_type).itervalues():

                sec_Id = str(sec.getId())
                # print('----Reading Sector {0}...'.format(sec_name))

                # add to dict
                # speed (mph), flow
                rep_data[sec_Id] = [[], []]

                speedData = sec.getDataValueTS(speedColumn)
                flowData = sec.getDataValueTS(flowColumn)

                if flowData.size() == 0 or speedData.size() == 0 or flowData.size() != speedData.size():
                    print('ERROR: Detector {0} has no data available'.format(det_name))
                else:
                    rep_data[sec_Id][0].append(speedData.getAggregatedValue())  # This returns the aggregated value (ent = 0)
                    rep_data[sec_Id][1].append(flowData.getAggregatedValue())  # This returns the aggregated value (ent = 0)
                    # for interval in range(flowData.size()):
                    #     rep_data[sec_Id][0].append(speedData.getValue(GKTimeSerieIndex(interval))[0])
                    #     rep_data[sec_Id][1].append(flowData.getValue(GKTimeSerieIndex(interval))[0])

            # print(rep_data)

        return rep_data

    def __findAverageobject(self, model):

        resultType = model.getType("GKExperimentResult")
        result = None

        for types in model.getCatalog().getUsedSubTypesFromType(resultType):
            for s in types.itervalues():
                if s.getExperiment().getId() == model.getCatalog().findByName(self.__calibExperiment).getId():
                    result = s

        return result

    #This method runs the simulation and extract the data from detectors
    # @ param model the aimsun active model
    # @ param id, the index of calibration vector in the population

    def __runSim(self, model, avg_result, id):

        avg_result.resetReplications()

        replication_list = avg_result.getReplications()

        print("There are %d replications" %len(replication_list))
                
        rep = replication_list[0]
        
        if rep is not None and rep.isA('GKReplication'):
            print("Starting simulation...")
            rep.setRandomSeed(random.randint(1, 2.2 * 10 ** 9))
            GKSystem.getSystem().executeAction('execute', rep, replication_list, "")

            print("Simulation finished! Time to run average")

            if len(replication_list) > 1:
                # compute the average
                if avg_result != None and avg_result.isA("GKExperimentResult"):
                    GKSystem.getSystem().executeAction("execute", avg_result, [], "")

                print("Now let's get the average resluts")

                avrage = [avg_result]
                self.__pop[id].output_model = self.__read_sector_data(model, avrage)
            else:
                self.__pop[id].output_model = self.__read_sector_data(model, replication_list)

            fileLog.write("Simulation Finished at %s\n" % time.asctime(time.localtime(time.time())))
            fileLog.flush()
        else:
            fileLog.write("Cannot find the replication % d\n" % self.__idRep)
            fileLog.flush()
            console.close()

    # This method creates a log file
    def __createLogfile(self):

        global fileLog

        angAbsName = os.path.basename(self.__angFileName)
        angName = os.path.splitext(angAbsName)[0]
        fileLogPath = os.path.dirname(self.__angFileName) + os.sep + angName + ".log"

        if not os.path.exists(fileLogPath):
            fileLog = open(fileLogPath, "w")
        else:
            fileLog = open(fileLogPath, "a")

        # system = GKSystem()  # Access the unique instance of GKSystem (GKSystem is a singleton class (only one instance of this class exists))
        # fileLog.write("\noooooooooooooooooooooooooooooooooooooooooooooooooo\n")
        # fileLog.write("Date: %s - " % time.asctime(time.localtime(time.time())))
        # fileLog.write("%s - CONSOLE - " % str(system.getAppVersion()))
        # fileLog.write("ANG FILE: %s\n" % str(self.__angFileName))
        # fileLog.write("Id Replication/Result: %d\n" % self.__idRep)
        # fileLog.write("\noooooooooooooooooooooooooooooooooooooooooooooooooo\n")


    #This method load the network and calls other methods to modify the parameters and run the simulation
    def run(self):

        self.__createLogfile()
        # Start a Console
        console = ANGConsole()

        # Load a network
        if console.open(self.__angFileName):

            # Create a backup
            print("Creating backup")
            # console.save(self.__angFileName + ".old")
            # console.save(self.__angFileName)
            # print("Backup file was created!")
            #model = console.getModel()
            
            # set up AIMSUN
            model = GKSystem.getSystem().getActiveModel()
            fileLog.write("--------------------------------------------\n")
            fileLog.write("Network: %s \n" % str(model.getDocumentFileName()))
            fileLog.write("--------------------------------------------\n")
            fileLog.flush()

            avg_result = self.__findAverageobject(model)
            for iter in range(len(self.__pop)):
                self.__noCalibration = False
                if not self.__noCalibration: self.__modifytheModel(model, iter)
                self.__noCalibration = False
                self.__runSim(model, avg_result, iter)

            # for iter in range(len(self.__pop)):
            #     print(self.__pop[iter].output_model)

            console.close()
            fileLog.close()
            return self.__pop
        else:
            fileLog.write("Cannot load the network\n")
            fileLog.flush()
            console.getLog().addError("Cannot load the network")
            return -1

    # This method finds the "Car" object
    # @param model, aimsun active model
    def __getcarVeh(self, model):
            vehicleType = model.getType("GKVehicle")
            vehicleId = None
            for types in model.getCatalog().getUsedSubTypesFromType(vehicleType):
                for s in types.itervalues():
                    if s.getName() == "Car":
                        vehicleId = s.getId()

            return model.getCatalog().find(vehicleId)

    # This method modifies the model according to the parameters in vector i
    # @param model, aimsun active model
    # @param i, the index of calibration vector for which the model to be modified
    # @return an aimsun experiment contaning the changed parameters

    def __modifytheModel(self, model, i):

        carVeh = self.__getcarVeh(model)

        attr = carVeh.getType().getColumn("GKVehicle::minDistDev", GKType.eSearchThisAndParentTypes)
        speed = carVeh.getDataValueDouble(attr)
        print("Hello")
        print (speed)

        # experID = model.getActiveExperimentId()
        # experiment = model.getCatalog().find(experID)
        experiment = model.getCatalog().findByName(self.__calibExperiment)

        # [reaction_time, reaction_stop, reaction_light, reaction_prob]
        car_react = GKVehicleReactionTimes(self.__pop[i].data[0], self.__pop[i].data[1], self.__pop[i].data[2], 1)

        carVeh.setDataValueByID(GKVehicle.maxAccelMean, self.__pop[i].data[3])
        
        carVeh.setDataValueByID(GKVehicle.speedAcceptanceMean, self.__pop[i].data[4])

        carVeh.setDataValueByID(GKVehicle.maxSpeedMean, self.__pop[i].data[5])

        carVeh.setDataValueByID(GKVehicle.maxDecelMean, self.__pop[i].data[6])

        carVeh.setDataValueByID(GKVehicle.minDistMean, self.__pop[i].data[7])

        print(self.__pop[i].data)

        carVeh.setVariableReactionTimes([car_react])
        experiment.setVariableReactionTimesMicro(carVeh, [car_react])


