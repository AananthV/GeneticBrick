'''
This is a python clone of https://github.com/xviniette/FlappyLearning/blob/gh-pages/Neuroevolution.js
'''


import numpy as np

#Define a configuration for the network;
class Options:
    #Logistic activation function
    def activation(self, a):
        return 1/(1+exp(-a))

    #Random value between -1 and 1
    def randomClamped(self):
        return np.random.random()*2 - 1

    #Other Params
    network = [4, [2], 1] #Perceptron structure
    population = 50 #Population per generation
    elitism = 0.2 #The best species are left unaltered
    randomBehaviour = 0.2 #Random species in next gen
    mutationRate = 0.1 #Rate of change of weights
    mutationRange = 1 #Limit of mutation change
    crossoverFactor = 0.5 #Factor of genetic crossover
    historic = 0 #Latest saved generation
    lowHistoric = False #False - Save score and network; True - Save only score
    scoreSort = -1 # -1 = desc, 1 = asc
    nbChild = 1 #No of children by breeding

options = Options()

class Neuron:
    def __init__(self):
        self.value = 0
        self.weights = []

    #Function to initialise n weights to random values.
    def populate(self, n):
        global options
        for i in range(n):
            self.weights.append(options.randomClamped())
            #self.weights.append(np.random.random()*2 - 1)

class Layer:
    def __init__(self, index):
        self.id = index or 0
        self.neurons = []

    #Function to initialise nbNeurons neurons with nbWeights weights to a Layer
    def populate(self, nbNeurons, nbWeights):
        for i in range(nbNeurons):
            n = Neuron()
            n.populate(nbWeights)
            self.neurons.append(n)
class Network:
    def __init__(self):
        self.layers = []

    def perceptronGeneration(self, inputs, hiddens, outputs):
        index = 0
        previousNeurons = 0

        #Input Layer
        layer = Layer(index)
        layer.populate(inputs, previousNeurons)
        self.layers.append(layer)
        previousNeurons = inputs
        index = index + 1

        #Hidden Layers
        for i in hiddens:
            layer = Layer(index)
            layer.populate(i, previousNeurons)
            self.layers.append(layer)
            previousNeurons = i
            index = index + 1

        #Output Layer
        layer = Layer(index)
        layer.populate(outputs, previousNeurons)
        self.layers.append(layer)

    def getSave(self):
        class Datas:
            neurons = []
            weights = []

        datas = Datas()

        for i in self.layers:
            datas.neurons.append(len(i.neurons))
            for j in i.neurons:
                for k in j.weights:
                    #Push all weights into a flat array
                    datas.weights.append(k)
        return datas

    def setSave(self, save):
        previousNeurons = 0
        index = 0
        indexWeights = 0
        self.layers = []
        for i in save.neurons:
            layer = Layer(index)
            layer.populate(i, previousNeurons)
            for j in layer.neurons:
                for k in range(len(j.weights)):
                    j.weights[k] = save.weights[indexWeights]
                    indexWeights = indexWeights + 1
            previousNeurons = i
            index = index + 1
            self.layers.append(layer)

    def compute(self, inputs):
        for i in range(len(inputs)):
            if self.layers[0] and self.layers[0].neurons[i]:
                self.layers[0].neurons[i].value = inputs[i]

        prevLayer = self.layers[0]
        for i in range(1, len(self.layers)):
            for j in range(len(self.layers[i].neurons)):
                sum = 0
                for k in range(len(prevLayer.neurons)):
                    sum += self.layers[i].neurons[j].weights[k] * prevLayer.neurons[k].value

                self.layers[i].neurons[j].value = 1/(1+np.exp(-sum))

            prevLayer = self.layers[i]

        out = []
        lastLayer = self.layers[len(self.layers)-1]
        for i in lastLayer.neurons:
            out.append(i.value)

        return out

class Genome:
    def __init__(self, score, network):
        self.score = score or 0
        self.network = network or None

class Generation:
    def __init__(self):
        self.genomes = []
        global options

    def addGenome(self, genome):
        index = 0
        for i in range(len(self.genomes)):
            #Descending Order
            if options.scoreSort < 0:
                if self.genomes[i].score <= genome.score:
                    break
            elif options.scoreSort > 0:
                if self.genomes[i].score >= genome.score:
                    break
            index = i

        self.genomes.insert(index, genome)

    def breed(self, g1, g2, nbChilds):
        datas = []
        for nb in range(nbChilds):
            data = g1
            for i in range(len(g2.network.weights)):
                #Genetic crossover
                if np.random.random() <= options.crossoverFactor:
                    data.network.weights[i] = g2.network.weights[i]

            for i in range(len(data.network.weights)):
                if np.random.random() <= options.mutationRate:
                    data.network.weights[i] = data.network.weights[i] + (np.random.random()*2 - 1) * options.mutationRange

            datas.append(data)

        return datas

    def generateNextGeneration(self):
        nexts = []
        for i in range(int(options.elitism * options.population)):
            if len(nexts) <= options.population:
                nexts.append(self.genomes[i].network)

        for i in range(int(options.randomBehaviour * options.population)):
            if len(nexts) <= options.population:
                n = self.genomes[0].network
                tw = [np.random.random()*2 - 1 for i in range(len(n.weights))]
                n.weights = tw
                nexts.append(n)

        max = 0
        while(True):
            childs = []
            for i in range(max):
                childs = self.breed(self.genomes[i], self.genomes[max], options.nbChild)

                for i in range(options.nbChild):
                    if len(nexts) <= options.population:
                        nexts.append(childs[i].network)
                    else:
                        return nexts

            max = max + 1
            if max >= len(self.genomes) - 1:
                max = 0



class Generations:
    def __init__(self):
        self.generations = []
        self.currentGeneration = Generation()
        global options

    def firstGeneration(self):
        out = []
        for i in range(options.population):
            nn = Network()
            nn.perceptronGeneration(options.network[0], options.network[1], options.network[2])
            out.append(nn.getSave())

        self.generations.append(Generation())
        return out

    def nextGeneration(self):
        if len(self.generations) == 0: #Generate first generation first
            return False
        gen = self.generations[-1].generateNextGeneration()
        self.generations.append(Generation())
        return gen

    def addGenome(self, genome):
        if len(self.generations) == 0:
            return False
        return self.generations[-1].addGenome(genome)

class Neuvol:
    def __init__(self):
        global options
        global screen
        self.generations = Generations()

    def nextGeneration(self):
        networks = []
        if len(self.generations.generations) == 0:
            #If no geneation, create first
            networks = self.generations.firstGeneration()
        else:
            #Create next one
            networks = self.generations.nextGeneration()

        #Create Networks from Generation
        nns = []
        for i in networks:
            nn = Network()
            nn.setSave(i)
            nns.append(nn)

        if options.lowHistoric:
            if len(self.generations.generations) >= 2:
                for i in range(len(self.genertions.generations[-2].genomes)):
                    del self.genertions.generations[-2].genomes[i].network

        if options.historic:
            if len(self.genertions.generations) > options.historic + 1:
                self.genertions.generations.insert(0, len(self.genertions.genertions) - (options.historic + 1))

        return nns

    def networkScore(self, network, score):
        self.generations.addGenome(Genome(score, network.getSave()))

    def returnBest(self):
        if len(self.generations.generations) > 0:
            return self.generations.generations[-1].genomes[0].network
