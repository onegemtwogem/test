#third term project backup
#Goal: 700+ lines of good code, not bunches of text, nonsense, dead code, etc.
from Tkinter import *
import random
import tkMessageBox
import tkSimpleDialog

class MinesweeperCountry(object): 
    """attributes: location, name, neighbors, mine, visibility, adjacent mines
    methods: uncover, place flag"""
    def __init__(self, name, location, neighbors):
        self.name = name
        self.location = location
        self.neighbors = neighbors
        self.isMine = False
        self.isVisible = False
        self.adjMines = 0
        self.isFlagged = False
        self.isQuestion = False

    def uncover(self, canvas):
        if (self.isVisible == False) and (self.isMine == False): 
            self.isVisible = True 
            #this is similar to memoizing, because it keeps track of visited mines
            self.drawCountryBox(canvas)
            canvas.data.uncoveredCountries += [self.name]
            if len(canvas.data.uncoveredCountries) == len(canvas.data.freeCountries):
                youWin(canvas)
            if self.adjMines == 0: self.uncoverAdjZeros(canvas)
            #this  bit is a common minesweeper function, to avoid tedious 
            #uncovering

    def uncoverAdjZeros(self, canvas):
        countries = canvas.data.countries
        for country in self.neighbors:
            #if countries[country].adjMines == 0:
            countries[country].uncover(canvas) #MUTUAL RECURSION!!!!!!!!!!!!!!!!

    def nameCountry(self, canvas): #based off code from course website
        message = "Which country is this?"
        title = ""
        options = self.getOptions(canvas)
        for i in xrange(len(options)):
            message += "\n" + options[i]
        response = tkSimpleDialog.askstring(title, message) 
        if response == None: #get rid of cancel button
            canvas.data.remainingMines += 1
            return None
        else: return response

    def getWeightedOptions(self, canvas, weight): #model RECURSION
        for country in self.neighbors:
            canvas.data.weightedOptions += weight*[country]
            if (country not in canvas.data.weightedOptions) and (weight > 1): 
                #base case(s)
                country.getWeightedOptions(canvas, weight/2)
                #while this will include the country clicked, the wrapper 
                #function takes care of that

    def getOptions(self, canvas): #model
        #reset each time function is called
        canvas.data.weightedOptions = canvas.data.listOfCountries 
        weight = canvas.data.weight
        self.getWeightedOptions(canvas, weight)
        #for country in self.neighbors:
        #    weightedOptions += canvas.data.weight*[country]
            #IS THIS TOO EXPENSIVE???? ie does it take too much time?
        options = [self.name]
        weightedOptions = canvas.data.weightedOptions
        while len(options) < canvas.data.numberOfOptions:
            country = weightedOptions[random.randint(0, len(weightedOptions)-1)]
            if country not in options: options += [country]
        random.shuffle(options)
        return options

    def placeFlag(self, canvas):
        self.isFlagged = True
        self.drawCountryBox(canvas)
        namedCountry = self.nameCountry(canvas)
        if namedCountry == None: 
            self.isFlagged = False
            redrawAll(canvas)
        elif (namedCountry != self.name): 
            gameOver(canvas, self.location[0], self.location[1], "Wrong country.")
        canvas.data.remainingMines -= 1
        redrawAll(canvas)

    def placeQuestion(self, canvas):
        self.isFlagged = False
        self.isQuestion = True
        self.drawCountryBox(canvas)
        canvas.data.remainingMines += 1
        redrawAll(canvas)

    def removeQuestion(self, canvas):
        self.isQuestion = False
        self.drawCountryBox(canvas)

    def printCountryName(self,canvas): #view
        canvas.create_rectangle(self.location[0], self.location[1], 
            self.location[0] + canvas.data.squareSize, 
            self.location[1] + canvas.data.squareSize, fill = "white", 
            width = 0)
        canvas.create_text(self.location[0], 
            self.location[1] + canvas.data.squareSize/2, 
            text = "%s"%(self.name), anchor = W, 
            font=("Helvetica 16 bold")) 

    def drawCountryBox(self, canvas): #view
        if self.isVisible:
            canvas.create_rectangle(self.location[0], self.location[1], 
                self.location[0] + canvas.data.squareSize, 
                self.location[1] + canvas.data.squareSize, fill = "white", 
                width = 2)
            canvas.create_text(self.location[0] + canvas.data.squareSize/2, 
                self.location[1] + canvas.data.squareSize/2, 
                text = "%s"%(self.adjMines), anchor = CENTER, 
                font=("Helvetica 11 bold")) 
        else:
            if self.isFlagged: fill, phrase = "red", ""
            elif self.isQuestion: fill, phrase = "green", "?"
            elif self.name in canvas.data.currentNeighbors:
                fill, phrase = "light blue", ""
            else: fill, phrase = canvas.data.hiddenColor, ""
            canvas.create_rectangle(self.location[0], self.location[1], 
                self.location[0] + canvas.data.squareSize, 
                self.location[1] + canvas.data.squareSize, fill = fill, width = 2)
            canvas.create_text(self.location[0] + canvas.data.squareSize/2, 
                self.location[1] + canvas.data.squareSize/2, 
                text = phrase, anchor = CENTER, font=("Helvetica 11 bold"))

def drawMinesweeperBoard(canvas): #view
    canvas.create_image(canvas.data.width/2, canvas.data.height/2, image = canvas.data.bg)
    if canvas.data.newGameButton != False:
        canvas.create_window(40, 590, window = canvas.data.newGameButton)
    #else: canvas.create_window(40, 590, window = canvas.data.beginButton)
    canvas.create_window(112, 590, window = canvas.data.instructionsButton)
    canvas.create_window(186, 590, window = canvas.data.mainButton)
    canvas.create_window(274, 590, window = canvas.data.reviewButton)
    #the magic numbers here position the buttons so that they are next to 
    #eachother
    countries = canvas.data.countries
    for country in countries: 
        countries[country].drawCountryBox(canvas)
    #remainingMines = numberOfMinesUnmarked(canvas)
    remainingMines = canvas.data.remainingMines
    canvas.create_text(0.05*canvas.data.width, 0.05*canvas.data.height, 
        text="%s remaining mines"%(remainingMines), anchor = NW, 
        font=("Helvetica 11 bold"))

def gameOver(canvas, x, y, reason): #model
    canvas.data.isGameOver = True
    canvas.data.inPlay = False
    index = random.randint(0, len(canvas.data.jamesBond)-1)
    canvas.data.bond = canvas.data.jamesBond[index]
    canvas.data.reason = reason
    canvas.data.gameOverx, canvas.data.gameOvery = x, y
    redrawAll(canvas)

def youWin(canvas):
    canvas.data.isGameOver = True
    canvas.data.youWon = True
    name = getName(canvas)
    saveText(name + "," + str(canvas.data.numberOfClicks) + ",", "scores.txt")
    #add winners' scores to the scoreboard
    redrawAll(canvas)
    while canvas.data.isGameOver == True:
        drawFact(canvas)

def getName(canvas): #based off code from course website
        message = "You won! What is your name?"
        title = ""
        response = tkSimpleDialog.askstring(title, message) 
        if response == None: #get rid of cancel button
            return None
        else: return response

def loadScores():
    """returns and ordered list of the best three scores in the form: score,
    name, score, name, score, name where scores are type int"""
    scoresList = []
    scores = loadTextString("scores.txt") + ","
    while "," in scores:
        indx = scores.index(",")
        scoresList.append(scores[0:indx]) #add each score to the list
        scores = scores[indx + 1:]
    for element in scoresList:
        try: 
            indxx = scoresList.index(element)
            newElement = int(element)
            scoresList.pop(indxx)
            scoresList.insert(indxx, newElement)
        except: pass
    scoreBoard = []
    while len(scoreBoard) < 6:
        winnerIndex = scoresList.index(min(scoresList))
        scoreBoard.append(scoresList[winnerIndex]) #winning score
        scoreBoard.append(scoresList[winnerIndex - 1]) #winner's name
        scoresList = scoresList[:winnerIndex-1] + scoresList[winnerIndex + 1:]
    return scoreBoard

def drawFact(canvas):
    #print a fun fact if you win!
    width, height = canvas.data.width, canvas.data.height
    fact = canvas.data.facts[random.randint(0,len(canvas.data.facts)-1)]
    if len(fact) < 90: size = 24
    else: size = 20
    canvas.create_rectangle(0.15*canvas.data.width, 0.05*canvas.data.height, 
            0.8*canvas.data.width, 0.3*canvas.data.height, fill = "white", 
            width = 0)
    canvas.create_text(width/2, 0.2*height, text=fact, 
        anchor = CENTER, font=("Helvetica %s bold")%(size), width = 0.7*canvas.data.width)

def redrawAll(canvas): #view
    canvas.delete(ALL)
    width, height = canvas.data.width, canvas.data.height
    drawMinesweeperBoard(canvas)
    if (canvas.data.isGameOver == True) and (canvas.data.youWon == True):
        canvas.create_rectangle(0.25*width, 0.35*height, 0.75*width, 
            0.85*height, fill = "white", width = 0)
        
        canvas.create_text(width/2, height/2, text="You WON!", anchor=CENTER, 
            font=("Helvetica", 48, "bold"))
                
        
    elif canvas.data.isGameOver == True:
        canvas.create_image(canvas.data.gameOverx, canvas.data.gameOvery, image = canvas.data.bond)
        canvas.create_rectangle(0.25*width, 0.35*height, 0.75*width, 
            0.85*height, fill = "white", width = 0)
        canvas.create_text(width/2, height/2, text="Game Over!", anchor=CENTER, 
            font=("Helvetica", 48, "bold"))
        canvas.create_text(width/2, height/2 - 0.1*height, 
            text=canvas.data.reason, anchor=CENTER, font=("Helvetica 36 bold"))
    if canvas.data.isGameOver == True:
        scoreBoard = loadScores()
        canvas.create_text(width/2, 0.6*height, text="Leaderboard:", anchor=CENTER,
            font = ("Helvetica 20 bold"))
        canvas.create_text(width/2, 0.65*height, text=scoreBoard[:2], anchor=CENTER,
            font = ("Helvetica 20 bold"))
        canvas.create_text(width/2, 0.7*height, text=scoreBoard[2:4], anchor=CENTER,
            font = ("Helvetica 20 bold"))
        canvas.create_text(width/2, 0.75*height, text=scoreBoard[4:], anchor=CENTER,
            font = ("Helvetica 20 bold"))

def findQuad(canvas, event): #model
    quadTree = canvas.data.quadTree
    if event.x <= canvas.data.width/2:
        if event.y <= canvas.data.height/2:
            return "topLeft"
        else:
            return "bottomLeft"
    else:
        if event.y <= canvas.data.height/2:
            return "topRight"
        else:
            return "bottomRight"

def mousePressedHelper(canvas, event): #model
    """Returns country name if the mouse was pressed in a box, otherwise 
    returns False """
    if (canvas.data.mainMenu == False): 
        # we want countries, main menu doesn't use countries
         #for the score, lower is better
        countries = canvas.data.countries
        quadTree = canvas.data.quadTree
        quad = findQuad(canvas, event)
        for country in quadTree[quad]:
            if ((countries[country].location[0] <= event.x <= 
                countries[country].location[0] + canvas.data.squareSize) 
                and (countries[country].location[1] <= event.y <= 
                countries[country].location[1] + canvas.data.squareSize)):
                    return country
        return False

def saveYourself(canvas):
    if canvas.data.continent == "Europe":
        trivia = loadTextList("eurotrivia.txt")
    elif canvas.data.continent == "Africa":
        trivia = loadTextList("afrotrivia.txt")
    index = 2*(random.randint(0, (len(trivia)-1)/2))
    question = trivia[index]
    answer = trivia[index+1]
    message = "Bond found you. He'll let you go if you answer his question: '%s'"%(question)
    title = ""
    #options = ["Antarctica", "Europe"]
    #for i in xrange(len(options)):
    #    message += "\n" + options[i]
    response = tkSimpleDialog.askstring(title, message) 
    #type(response) = string
    #print trivia
    response = removeExcessWhitespace(response)
    answer = removeExcessWhitespace(answer)
    #print response, type(answer)
    #print answer, type(answer)
    return (response == answer)#model

def removeExcessWhitespace(rawString): #model, with help from Alex
    return " ".join(rawString.split())

def leftMousePressed(canvas, event): #controller, wrapper
    """If square is a bomb, game over. If it's a hidden country, uncover it. 
    If it's a menu option, follow that option. Otherwise, do nothing."""
    print event.x, event.y
    if canvas.data.inPlay == True: 
            canvas.data.numberOfClicks += 1
    if canvas.data.mainMenu: 
        if (333 <= event.x <= 565) and (179 <= event.y <= 237): 
            #these magic numbers are the coordinates of the word "Europe"
            canvas.data.continent = "Europe"
            initStart(canvas)
        elif (333 <= event.x <= 545) and (277 <= event.y <= 334):
            #these magic numbers are the coordinates of the word "Africa"
            canvas.data.continent = "Africa"
            initStart(canvas)
    elif canvas.data.inPlay == False:
        return (event.x, event.y)
    elif mousePressedHelper(canvas, event) == False: #no country pressed
        return (event.x, event.y)
    elif ((canvas.data.countries[mousePressedHelper(canvas, event)].isMine == True) 
        and (canvas.data.countries[mousePressedHelper(canvas, event)].isFlagged== False)
        and (canvas.data.countries[mousePressedHelper(canvas, event)].isQuestion==False)):
        countries = canvas.data.countries
        if saveYourself(canvas): pass
        else:
            x, y = event.x, event.y
            gameOver(canvas, x, y, "Bond got you.")
    elif ((canvas.data.countries[mousePressedHelper(canvas, event)].isFlagged==True)
        or (canvas.data.countries[mousePressedHelper(canvas, event)].isQuestion==True)):
        pass
    else: 
        countries = canvas.data.countries
        countries[mousePressedHelper(canvas, event)].uncover(canvas)

def rightMousePressed(canvas, event): #controller
    if canvas.data.inPlay == True: 
            canvas.data.numberOfClicks += 1
    if canvas.data.inPlay == False: return
    countries = canvas.data.countries
    if mousePressedHelper(canvas, event) == False: 
        pass
    #elif (countries[mousePressedHelper(canvas, event)].isVisible == True): 
    #    pass #if it is visible, do nothing
    elif (countries[mousePressedHelper(canvas, event)].isFlagged == True):
        #if it is flagged, make it a question mark
        countries[mousePressedHelper(canvas, event)].placeQuestion(canvas)
        redrawAll(canvas)
    elif (countries[mousePressedHelper(canvas, event)].isQuestion == True):
        #if it is questioned, make if blank
        countries[mousePressedHelper(canvas, event)].removeQuestion(canvas)
        redrawAll(canvas)
    else: #if it is blank, make it questioned
        countries[mousePressedHelper(canvas, event)].placeFlag(canvas)

def reviewCountries(canvas, event): #model 
    init(canvas)
    canvas.data.inPlay = False
    countries = canvas.data.countries
    quadTree = canvas.data.quadTree
    country = mousePressedHelper(canvas, event) #get country name
    if country != False: #mousePressedHelper may return false
        countries[country].printCountryName(canvas)

def mouseMotion(canvas, event): #controller
    canvas.data.currentNeighbors = []
    #if (canvas.data.mainMenu == False):
    if (canvas.data.inPlay == True) or (canvas.data.reviewCountries == True):
        canvas.data.mousePosition = (event.x, event.y) 
        if canvas.data.reviewCountries == True:
            reviewCountries(canvas, event)
        elif (canvas.data.inPlay == True):
            redrawAll(canvas) 
            if (mousePressedHelper(canvas, event) != False):
                countries = canvas.data.countries
                for country in canvas.data.listOfCountries:
                    if country in countries[mousePressedHelper(canvas, event)].neighbors:
                        canvas.data.currentNeighbors.append(country)
                if canvas.data.isGameOver == False: redrawAll(canvas)

def randomlyPlaceMines(canvas): #model
    countries = canvas.data.countries
    mines = []
    while len(mines) < canvas.data.numberMines: #random indices, no repeats
        index = random.randint(0, len(countries)-1)
        if index not in mines: mines.append(index)
    for mine in mines:
        countries[canvas.data.listOfCountries[mine]].isMine = True
    #countries[mine].isMine = True for mine in mines

def findAdjMines(canvas): #model
    countries = canvas.data.countries
    for country in countries:
        adjMines = 0
        for neighbor in countries[country].neighbors:
            if countries[neighbor].isMine == True:
                adjMines += 1
        countries[country].adjMines = adjMines#model

def loadTextList(fileName): #From course website, fall 2010
    fileHandler = open(fileName, "rt") # rt stands for read text
    text = fileHandler.readlines() # read the entire file into a list
    fileHandler.close() # close the file
    return text

def loadTextString(fileName): #from course website, fall 2010
    fileHandler = open(fileName, "rt") # rt stands for read text
    text = fileHandler.read() # read the entire file into a single string
    fileHandler.close() # close the file
    return text

def saveText(text, fileName): #modified from fall 2010
    #first load the old scores so as to fake not override them,then add the
    #new score
    scores = ""
    for score in loadTextList(fileName):
        scores += score + ","
    scores += text 
    #print scores
    fileHandler = open(fileName, "wt") # wt stands for write text
    fileHandler.write(scores) # write the text
    fileHandler.close() # close the file

def getCountriesInfo(canvas): #model
    #name, location, neighbors, isMine, isVisible, adjmines
    width, height = canvas.data.width, canvas.data.height
    countries = canvas.data.countries
    if canvas.data.continent == "Europe":
        countriesList = loadTextList("euroCountries.txt")
    elif canvas.data.continent == "Africa":
        countriesList = loadTextList("Africa.txt")
    #the following code pulls from the adjacency list stored in Countries.txt to
    #create a graph where countries are nodes and edges connect each country
    #to its neighbors
    for country in xrange(len(countriesList)):
        #key name
        indx = countriesList[country].index(",")
        key = countriesList[country][0:indx]
        countriesList[country] = countriesList[country][indx+1:]
        #country name, same as key name
        indx = countriesList[country].index(",")
        name = countriesList[country][0:indx]
        countriesList[country] = countriesList[country][indx+1:]
        #width
        indx = countriesList[country].index(",")
        xlocation = countriesList[country][0:indx]
        countriesList[country] = countriesList[country][indx+1:]
        #height
        indx = countriesList[country].index(",")
        ylocation = countriesList[country][0:indx]
        countriesList[country] = countriesList[country][indx+1:]
        #neighbors
        neighbors = []
        while "," in countriesList[country]:
            indx = countriesList[country].index(",")
            neighbors.append(countriesList[country][0:indx])
            countriesList[country] = countriesList[country][indx+1:]
        countries[key] = MinesweeperCountry(name, 
            (int(xlocation)-canvas.data.squareSize/2, 
                int(ylocation)-canvas.data.squareSize/2), neighbors)

def loadMinesweeperBoard(canvas): #model
    width, height = canvas.data.width, canvas.data.height
    countries = {}
    canvas.data.countries = countries
    #this is to be a dictionary of all the countries where each country is an
    #instance of the class MinesweeperCountry where all its info is stored :)
    getCountriesInfo(canvas)
    listOfCountries = []
    for country in countries: 
        listOfCountries.append(countries[country].name)
    canvas.data.listOfCountries = listOfCountries
    if canvas.data.reviewCountries == False:
        # if we are playing the game/not reviewing, we need to place mines!
        randomlyPlaceMines(canvas)
        findAdjMines(canvas)
        freeCountries = []
        mineCountries = []
        for country in listOfCountries:
            if countries[country].isMine == False: freeCountries += [country]
            else: mineCountries += [country]
        canvas.data.countries = countries
        canvas.data.freeCountries = freeCountries #countries w/o mine
        canvas.data.mineCountries = mineCountries #countries w/ mine
        canvas.data.uncoveredCountries = [] #to add countries that get uncovered 
        #model
    #elif canvas.data.reviewCountries == True:
        #otherwise, we want to create a QUADTREE to get rid of the slight delay
        #in reviewing countries
    createQuadTree(canvas)
        
def createQuadTree(canvas): #model
    quadTree = {"topLeft":[], "bottomLeft":[], "topRight":[], "bottomRight":[]}
    #these names are less confusing for me than the mathematical names, 
    #especially since the canvas isn't a regular mathematical coordinate system
    width, height = canvas.data.width, canvas.data.height
    countries = canvas.data.countries
    for country in canvas.data.listOfCountries:
        if countries[country].location[0] <= width/2:
            if countries[country].location[1] <= height/2:
                #topLeft quartile
                quadTree["topLeft"].append(countries[country].name)
            else:
                #bottomLeft quartile
                quadTree["bottomLeft"].append(countries[country].name)
        else:
            if countries[country].location[1] <= height/2:
                #topRight quartile
                quadTree["topRight"].append(countries[country].name)
            else:
                #bottomRight quartile
                quadTree["bottomRight"].append(countries[country].name)
    canvas.data.quadTree = quadTree

def init(canvas): #model
    canvas.data.numberMines = 1
    canvas.data.remainingMines = canvas.data.numberMines
    canvas.data.squareSize = 15
    canvas.data.hiddenColor = "blue"
    canvas.data.numberOfClicks = 0
    canvas.data.isGameOver = False
    canvas.data.youWon = False
    canvas.data.inPlay = True
    canvas.data.reviewCountries = False
    canvas.data.margin = 5
    canvas.data.cellSize = 15
    canvas.data.weight = 8
    canvas.data.numberOfOptions = 5
    canvas.data.currentNeighbors = []
    if canvas.data.continent == "Europe":
        canvas.data.bg = PhotoImage(file = "blank_europe_map_resized.gif") 
        canvas.data.facts = loadTextList("eurofacts.txt")
    elif canvas.data.continent == "Africa":
        canvas.data.bg = PhotoImage(file = "blank_Africa.gif")
        canvas.data.facts = loadTextList("afrofacts.txt")###### add facts
    bond1 = PhotoImage(file = "bond_1.gif")
    bond2 = PhotoImage(file = "bond_2.gif")
    bond3 = PhotoImage(file = "bond_3.gif")
    bond4 = PhotoImage(file = "bond_4.gif")
    canvas.data.jamesBond = [bond1, bond2, bond3, bond4]
    loadMinesweeperBoard(canvas)
    redrawAll(canvas)#model

def run(): #model
    root = Tk()
    global root
    width, height = 875, 600
    canvas = Canvas(root, width = width, height = height)
    canvas.pack()
    root.resizable(width=0, height=0)
    root.title("Creating World Peace (and geographical literacy)")
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call init
    class Struct: pass
    canvas.data = Struct()
    canvas.data.width, canvas.data.height = width, height
    mainMenu(canvas)
    # set up events
    root.bind("<Button-1>", lambda event: leftMousePressed(canvas, event))
    root.bind("<Button-3>", lambda event: rightMousePressed(canvas, event))
    root.bind("<Motion>", lambda event: mouseMotion(canvas, event))
    #timerFired(canvas)
    # and launch the app
    root.mainloop()  
    # This call BLOCKS (so your program waits until you close the window!)#model

# START SCREEN

def drawStart(canvas): #view
    canvas.delete(ALL)
    if canvas.data.continent == "Europe":
        canvas.data.bg = PhotoImage(file = "blank_europe_map_resized.gif")
    elif canvas.data.continent == "Africa":
        canvas.data.bg = PhotoImage(file = "blank_Africa.gif")
    canvas.create_image(canvas.data.width/2, canvas.data.height/2, 
        image = canvas.data.bg)
    #if canvas.data.showInstructions == True:
    #    displayInstructions(canvas)
    if canvas.data.reviewCountries == True:
        init(canvas)
        canvas.data.inPlay = False
        #reviewCountries(canvas)
    else:
        #text with a background
        canvas.create_rectangle(15, 
            canvas.data.height/2-15, canvas.data.width-15, 
            canvas.data.height/2+15, fill = "white", width = 0)
        canvas.create_text(canvas.data.width/2, canvas.data.height/2, 
            anchor = CENTER, text="Select 'Begin' or 'Instructions' or 'Review Countries'", 
            font="Helvetica 26 bold",)#view#view
    if canvas.data.newGameButton != False:
        canvas.create_window(40, 590, window = canvas.data.newGameButton)
    #else: canvas.create_window(40, 590, window = canvas.data.beginButton)
    canvas.create_window(112, 590, window = canvas.data.instructionsButton)
    canvas.create_window(186, 590, window = canvas.data.mainButton)
    canvas.create_window(274, 590, window = canvas.data.reviewButton)

def createButtons(canvas):
    #create begin button
    canvas.data.newGameButton = False
    def newGame():
        canvas.data.inPlay = True
        canvas.data.reviewCountries = False
        init(canvas)
    def begin(): 
        canvas.data.inPlay = True
        canvas.data.reviewCountries = False
        canvas.data.beginButton.destroy()
        newGameButton = Button(root, text="New Game", command=newGame)
        newGameButton.pack()
        canvas.data.newGameButton = newGameButton
        init(canvas)
    beginButton = Button(root, text="Begin", command=begin)
    beginButton.pack()
    #instructions button
    canvas.data.showInstructions = False
    def instructions(): 
        canvas.data.showInstructions = True
        canvas.data.reviewCountries = False
        displayInstructions(canvas)
        #drawStart(canvas)
    instructionsButton = Button(root, text="Instructions", command=instructions)
    instructionsButton.pack()
    #review countries button
    canvas.data.reviewCountries = False
    def review():
        canvas.data.newGameButton = False
        canvas.data.reviewCountries = True
        drawStart(canvas)
    reviewButton = Button(root, text="Review Countries", command=review)
    reviewButton.pack()
    def main():
        mainMenu(canvas)
    mainButton = Button(root, text="Main Menu", command=main)
    mainButton.pack()
    canvas.data.reviewButton = reviewButton
    canvas.data.mainButton = mainButton
    canvas.data.beginButton = beginButton
    canvas.data.instructionsButton = instructionsButton#model

def initStart(canvas): #model
    canvas.data.inPlay = False
    canvas.data.mainMenu = False
    createButtons(canvas)
    drawStart(canvas)#model

def displayInstructions(canvas):
    canvas.delete(ALL)
    width, height = canvas.data.width, canvas.data.height
    if canvas.data.continent == "Europe":
        canvas.data.bg = PhotoImage(file = "blank_europe_map_resized.gif")
    elif canvas.data.continent == "Africa":
        canvas.data.bg = PhotoImage(file = "blank_Africa.gif")
    canvas.create_image(canvas.data.width/2, canvas.data.height/2, 
        image = canvas.data.bg)
    instructions = loadTextList("instructions.txt")[0]
    canvas.create_rectangle(0.2*width, 0.1*height, 0.8*width, 0.85*height, fill = "white", width = 0)
    canvas.create_text(width/2, height/2, text="%s"%(instructions), font="Helvetica 14", width = 0.6*width)#view
    if canvas.data.newGameButton != False:
        canvas.create_window(40, 590, window = canvas.data.newGameButton)
    else: canvas.create_window(40, 590, window = canvas.data.beginButton)
    canvas.create_window(186, 590, window = canvas.data.mainButton)
    canvas.create_window(274, 590, window = canvas.data.reviewButton)
    #the magic numbers here position the buttons so that they are next to 
    #eachother

# MAIN MENU

def drawMainMenu(canvas):
    canvas.delete(ALL)
    canvas.data.bg = PhotoImage(file = "main menu.gif")
    canvas.create_image(canvas.data.width/2, canvas.data.height/2, 
        image = canvas.data.bg)

def mainMenu(canvas):
    canvas.data.mainMenu = True
    canvas.data.inPlay = False
    canvas.data.reviewCountries = False
    drawMainMenu(canvas)

run()