#Ascii Tetris in Python by Sucram314

#So I wanted to practice Perfect Clears but I couldn't find a way to start in the middle of a bag in jstris or tetrio so
#I remade Tetris in Python. And it's completely ASCII graphics as well. Might add an AI later.
#Sorry if the code is hard to read lol

#Links:
#javidx9   | inspiration: https://www.youtube.com/watch?v=8OK8_tHeCIA&t=550s
#Hard Drop | info on SRS rotation: https://harddrop.com/wiki/SRS
#jezevec10 | sounds and more inspiration: https://jstris.jezevec10.com/
#osk       | more inspiration: https://tetr.io/

import sys #file path stuff
import os #get paths of sound files, and...

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" #get rid of pygame prompt (sorry! I still support pygame)

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    currentDirectory = os.path.dirname(sys.executable)
elif __file__:
    currentDirectory = os.path.dirname(__file__)

#keybind finder:
KeyBinds = open(currentDirectory+"\\Options.txt","r")

lines = KeyBinds.readlines()
lines = [i for i in lines if i[0] != "#"]
lines = [x.replace("\n","") for x in lines]
lines = [i for i in lines if i != ""]
lines = [x.replace(" ","") for x in lines]
lines = [x.split("=") for x in lines]

for i in range(len(lines)):
    if lines[i][0]=="holdKey": holdKey = lines[i][1]
    elif lines[i][0]=="leftKey": leftKey = lines[i][1]
    elif lines[i][0]=="rightKey": rightKey = lines[i][1]
    elif lines[i][0]=="hardDropKey": hardDropKey = lines[i][1]
    elif lines[i][0]=="softDropKey": softDropKey = lines[i][1]
    elif lines[i][0]=="clockwiseKey": clockwiseKey = lines[i][1]
    elif lines[i][0]=="counterClockwiseKey": counterClockwiseKey = lines[i][1]
    elif lines[i][0]=="oneEightyKey": oneEightyKey = lines[i][1]
    elif lines[i][0]=="showFPS":
        if lines[i][1].lower()=="true": showFPS = True
        elif lines[i][1].lower()=="false": showFPS = False
        else: showFPS = False
    elif lines[i][0]=="seed":
        if lines[i][1].lower()=="none": seed = None
        else:
            try: seed = int(lines[i][1])
            except: seed = None
    elif lines[i][0]=="showGhost":
        if lines[i][1].lower()=="true": ghost = True
        elif lines[i][1].lower()=="false": ghost = False
        else: ghost = True
    elif lines[i][0]=="directionChangeDASCancel":
        if lines[i][1].lower()=="true": directionChangeCancel = True
        elif lines[i][1].lower()=="false": directionChangeCancel = False
    elif lines[i][0]=="softDropFactor(SDF)":
        if lines[i][1].lower()!="inf":
            try: sdf = int(lines[i][1])
            except: sdf = float("inf")
        else: sdf = float("inf")
    elif lines[i][0]=="automaticRepeatRate(ARR)":
        if lines[i][1].lower()!="inf":
            try: arr = int(lines[i][1])
            except: arr = 2
    elif lines[i][0]=="delayedAutoShift(DAS)":
        try: das = int(lines[i][1])
        except: das = 10
    elif lines[i][0]=="dasCutDelay(DCD)":
        try: dcd = int(lines[i][1])
        except: dcd = 1

#-----------------------------------------------------------------------------------

#importing all other modules
from sty import fg as c      #coloured text in console
from sty import Style,RgbFg  #custom colours
import time # TIME
import msvcrt #some stuff with disabling keyboard
import keyboard as k #detecting keyboard and more
import random # RANDOMNESS
import copy #COPYING LISTS AND DICTIONARIES
import ctypes #fullscreen and more
import pygame #sound
import atexit #do stuff before code ends
#-----------------------------------------------------

#put console in fullscreen and disabling input (no typing, quickedit or shift + arrowkeys to select console)
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')

SW_MAXIMIZE = 3

hWnd = kernel32.GetConsoleWindow()
user32.ShowWindow(hWnd, SW_MAXIMIZE)

k.block_key("shift")

def quickedit(enabled=1):
        kernel32 = ctypes.windll.kernel32
        if enabled:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x40|0x100))
        else:
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x00|0x100))

quickedit(0)

#make sure quickedit gets reenabled on exit
def exit_handler():
    quickedit(1)

atexit.register(exit_handler)

class keyboardDisable():
    def start(self):
        self.on = True

    def stop(self):
        self.on = False

    def __call__(self): 
        while self.on:
            msvcrt.getwch()

    def __init__(self):
        self.on = False

disable = keyboardDisable()
#-------------------------------------------------------------------------------------

#Initializing some important variables
class Cell:
    def __init__(self,colour,inMotion):
        self.colour = colour
        self.inMotion = inMotion

    def string(self):
        return ">"+str(self.colour)+"<██"+end

combo = 0
timea = time.time()
cancelS = False
cancelW = False
delay = 0
timeheld = time.time()
dp,ap = (False, False)
dcded = False
canhold = True
right = True
left = True
up = True
wait = None
rCancel = False
frame = 0.0175 #seconds#
dt = 0
#-------------------------------------------------------------------------------------

#Initializing sound using pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.set_num_channels(18)

switch = 0

placeSound = pygame.mixer.Sound(currentDirectory+"\\Sounds\\place.wav")
combo1 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo1.wav")
combo2 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo2.wav")
combo3 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo3.wav")
combo4 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo4.wav")
combo5 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo5.wav")
combo6 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo6.wav")
combo7 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo7.wav")
combo8 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo8.wav")
combo9 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo9.wav")
combo10 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo10.wav")
combo11 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo11.wav")
combo12 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo12.wav")
combo13 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo13.wav")
combo14 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo14.wav")
combo15 = pygame.mixer.Sound(currentDirectory+"\\Sounds\\combo15.wav")
loseSound = pygame.mixer.Sound(currentDirectory+"\\Sounds\\lose.wav")

def place():
    global switch
    pygame.mixer.Channel(switch).play(placeSound)
    switch = 16 if switch==0 else 0

combos = lambda:pygame.mixer.Channel(combo).play(eval("combo"+str(combo)))
lose = lambda:pygame.mixer.Channel(17).play(loseSound)
#------------------------------------------------------------------------------------
graying = False #turns immobile cells to gray if True

gravity = 1 #determines how fast pieces fall
lock_delay = 15 #how long a piece takes to settle in place
#------------------------------------------------------------------------

#colours for coloured text in console

os.system("") #enables ANSII escape codes (coloured text in console)

red = c.li_red
gh_red = c.da_red
c.orange = Style(RgbFg(255, 150, 50))
c.da_orange = Style(RgbFg(163, 95, 31))
orange = c.orange
gh_orange = c.da_orange
c.yellow_ = Style(RgbFg(247, 255, 8))
yellow = c.yellow_
c.da_yellow_ = Style(RgbFg(141, 145, 4))
gh_yellow = c.da_yellow_
green = c.li_green
gh_green = c.da_green
blue = c.blue
gh_blue = c.da_blue
cyan = c.li_cyan
gh_cyan = c.da_cyan
purple = c.li_magenta
gh_purple = c.da_magenta
gray = c.da_grey
end = c.rs #rs means reset to get rid of any colours
#---------------------------------------------------------------------------

#piece data
zRot = [[[Cell(0,True),Cell(0,True),None],
         [None,Cell(0,True),Cell(0,True)],
         [None,None,None]],

        [[None,None,Cell(0,True)],
         [None,Cell(0,True),Cell(0,True)],
         [None,Cell(0,True),None]],

        [[None,None,None],
         [Cell(0,True),Cell(0,True),None],
         [None,Cell(0,True),Cell(0,True)]],

        [[None,Cell(0,True),None],
         [Cell(0,True),Cell(0,True),None],
         [Cell(0,True),None,None]]]

lRot = [[[None,None,Cell(1,True)],
         [Cell(1,True),Cell(1,True),Cell(1,True)],
         [None,None,None]],

        [[None,Cell(1,True),None],
         [None,Cell(1,True),None],
         [None,Cell(1,True),Cell(1,True)]],

        [[None,None,None],
         [Cell(1,True),Cell(1,True),Cell(1,True)],
         [Cell(1,True),None,None]],

        [[Cell(1,True),Cell(1,True),None],
         [None,Cell(1,True),None],
         [None,Cell(1,True),None]]]

oRot = [[[Cell(2,True),Cell(2,True)],
         [Cell(2,True),Cell(2,True)]],

        [[Cell(2,True),Cell(2,True)],
         [Cell(2,True),Cell(2,True)]],

        [[Cell(2,True),Cell(2,True)],
         [Cell(2,True),Cell(2,True)]],

        [[Cell(2,True),Cell(2,True)],
         [Cell(2,True),Cell(2,True)]]]

sRot = [[[None,Cell(3,True),Cell(3,True)],
         [Cell(3,True),Cell(3,True),None],
         [None,None,None]],

        [[None,Cell(3,True),None],
         [None,Cell(3,True),Cell(3,True)],
         [None,None,Cell(3,True)]],

        [[None,None,None],
         [None,Cell(3,True),Cell(3,True)],
         [Cell(3,True),Cell(3,True),None]],

        [[Cell(3,True),None,None],
         [Cell(3,True),Cell(3,True),None],
         [None,Cell(3,True),None]]]

jRot = [[[Cell(4,True),None,None],
         [Cell(4,True),Cell(4,True),Cell(4,True)],
         [None,None,None]],

        [[None,Cell(4,True),Cell(4,True)],
         [None,Cell(4,True),None],
         [None,Cell(4,True),None]],

        [[None,None,None],
         [Cell(4,True),Cell(4,True),Cell(4,True)],
         [None,None,Cell(4,True)]],

        [[None,Cell(4,True),None],
         [None,Cell(4,True),None],
         [Cell(4,True),Cell(4,True),None]]]

iRot = [[[None,None,None,None],
         [Cell(5,True),Cell(5,True),Cell(5,True),Cell(5,True)],
         [None,None,None,None],
         [None,None,None,None]],

        [[None,None,Cell(5,True),None],
         [None,None,Cell(5,True),None],
         [None,None,Cell(5,True),None],
         [None,None,Cell(5,True),None]],

        [[None,None,None,None],
         [None,None,None,None],
         [Cell(5,True),Cell(5,True),Cell(5,True),Cell(5,True)],
         [None,None,None,None]],

        [[None,Cell(5,True),None,None],
         [None,Cell(5,True),None,None],
         [None,Cell(5,True),None,None],
         [None,Cell(5,True),None,None]]]

tRot = [[[None,Cell(6,True),None],
         [Cell(6,True),Cell(6,True),Cell(6,True)],
         [None,None,None]],

        [[None,Cell(6,True),None],
         [None,Cell(6,True),Cell(6,True)],
         [None,Cell(6,True),None]],

        [[None,None,None],
         [Cell(6,True),Cell(6,True),Cell(6,True)],
         [None,Cell(6,True),None]],

        [[None,Cell(6,True),None],
         [Cell(6,True),Cell(6,True),None],
         [None,Cell(6,True),None]]]

kickjlszt = {"01":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],"10":[(0,0),(1,0),(1,-1),(0,2),(1,2)],"12":[(0,0),(1,0),(1,-1),(0,2),(1,2)],"21":[(0,0),(-1,0),(-1,1),(0,-2),(-1,-2)],"23":[(0,0),(1,0),(1,1),(0,-2),(1,-2)],"32":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],"30":[(0,0),(-1,0),(-1,-1),(0,2),(-1,2)],"03":[(0,0),(1,0),(1,1),(0,-2),(1,-2)]}
kicki = {"01":[(0,0),(-2,0),(1,0),(-2,-1),(1,2)],"10":[(0,0),(2,0),(-1,0),(2,1),(-1,-2)],"12":[(0,0),(-1,0),(2,0),(-1,2),(2,-1)],"21":[(0,0),(1,0),(-2,0),(1,-2),(-2,1)],"23":[(0,0),(2,0),(-1,0),(2,1),(-1,-2)],"32":[(0,0),(-2,0),(1,0),(-2,-1),(1,2)],"30":[(0,0),(1,0),(-2,0),(1,-2),(-2,1)],"03":[(0,0),(-1,0),(2,0),(-1,2),(2,-1)]}
oneEightyKicks = {"02":[(0,0),(0,1),(1,1),(-1,1),(1,0),(-1,0)],"20":[(0,0),(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)],"13":[(0,0),(1,0),(1,2),(1,1),(0,2),(0,1)],"31":[(0,0),(-1,0),(-1,2),(-1,1),(0,2),(0,1)]}
#--------------------------------------------------------------------------------------------------

#Initializing board, randomization of the bag, loss detection, etc.
board = [[None for i in range(10)] for j in range(24)]

bag = ["z","l","o","s","j","i","t"]

orient = 0

def getName():
    global bag
    if bag == []:
        bag = ["z","l","o","s","j","i","t"]
    name = bag.pop(random.randint(0,len(bag)-1))
    return name

nex = []
for i in range(7): nex.append(getName())

held = ""
current = ""

def getPiece(name):
    if name=="":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [None,None,None,None],
                 [None,None,None,None]]
        
    elif name=="z":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [Cell(0,True),Cell(0,True),None,None],
                 [None,Cell(0,True),Cell(0,True),None]]
    elif name=="l":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [None,None,Cell(1,True),None],
                 [Cell(1,True),Cell(1,True),Cell(1,True),None]]

    elif name=="o":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [None,Cell(2,True),Cell(2,True),None],
                 [None,Cell(2,True),Cell(2,True),None]]

    elif name=="s":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [None,Cell(3,True),Cell(3,True),None],
                 [Cell(3,True),Cell(3,True),None,None]]

    elif name=="j":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [Cell(4,True),None,None,None],
                 [Cell(4,True),Cell(4,True),Cell(4,True),None]]

    elif name=="i":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [None,None,None,None],
                 [Cell(5,True),Cell(5,True),Cell(5,True),Cell(5,True)]]

    elif name=="t":
        piece = [[None,None,None,None],
                 [None,None,None,None],
                 [None,Cell(6,True),None,None],
                 [Cell(6,True),Cell(6,True),Cell(6,True),None]]

    return piece

def hasLost():
    for i in range(4):
        for j in range(3,7):
            if board[i][j]!=None:
                if not board[i][j].inMotion:
                    return True

    return False
                

def spawnPiece():
    global r,board,nex,current,orient
    orient = 0
    name = nex.pop(0)
    current = name
    piece = getPiece(name)
    nex.append(getName())
    for i in range(4):
        board[i] = board[i][:3]+piece[i]+board[i][7:]
    r = True

def holdPiece():
    global board,nex,held,current,orient
    orient = 0
    if held=="":
        held = current
        current = nex.pop(0)
        nex.append(getName())
    else:
        held,current = (current,held)

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j]!=None:
                if board[i][j].inMotion:
                    board[i][j] = None

    piece = getPiece(current)
    for i in range(4):
        board[i] = board[i][:3]+piece[i]+board[i][7:]

#empty board string configuration
string = "\n"*10
string +="                                                \n"
string +="                                                \n"
string +="                                                \n"
string +="                                                \n"
string +="                                                \n"
string +="                                        NEXT    \n"
string +="                                      N100      N101      N102      N103        \n"
string +="                                      N110      N111      N112      N113        \n"
string +="            ████████████████████████  N120      N121      N122      N123        \n"
string +="    HOLD    ██040       041       042       043       044       045       046       047       048       049       ██  N130      N131      N132      N133        \n"
string +="  H00       H01       H02       H03         ██050       051       052       053       054       055       056       057       058       059       ██            \n"
string +="  H10       H11       H12       H13         ██060       061       062       063       064       065       066       067       068       069       ██  N200      N201      N202      N203        \n"
string +="  H20       H21       H22       H23         ██070       071       072       073       074       075       076       077       078       079       ██  N210      N211      N212      N213        \n"
string +="  H30       H31       H32       H33         ██080       081       082       083       084       085       086       087       088       089       ██  N220      N221      N222      N223        \n"
string +="            ██090       091       092       093       094       095       096       097       098       099       ██  N230      N231      N232      N233        \n"
string +="            ██100       101       102       103       104       105       106       107       108       109       ██            \n"
string +="            ██110       111       112       113       114       115       116       117       118       119       ██  N300      N301      N302      N303        \n"
string +="            ██120       121       122       123       124       125       126       127       128       129       ██  N310      N311      N312      N313        \n"
string +="            ██130       131       132       133       134       135       136       137       138       139       ██  N320      N321      N322      N323        \n"
string +="            ██140       141       142       143       144       145       146       147       148       149       ██  N330      N331      N332      N333        \n"
string +="            ██150       151       152       153       154       155       156       157       158       159       ██            \n"
string +="            ██160       161       162       163       164       165       166       167       168       169       ██  N400      N401      N402      N403        \n"
string +="            ██170       171       172       173       174       175       176       177       178       179       ██  N410      N411      N412      N413        \n"
string +="            ██180       181       182       183       184       185       186       187       188       189       ██  N420      N421      N422      N423        \n"
string +="            ██190       191       192       193       194       195       196       197       198       199       ██  N430      N431      N432      N433        \n"
string +="            ██200       201       202       203       204       205       206       207       208       209       ██            \n"
string +="            ██210       211       212       213       214       215       216       217       218       219       ██  N500      N501      N502      N503        \n"
string +="            ██220       221       222       223       224       225       226       227       228       229       ██  N510      N511      N512      N513        \n"
string +="            ██230       231       232       233       234       235       236       237       238       239       ██  N520      N521      N522      N523        \n"
string +="            ████████████████████████  N530      N531      N532      N533        \n"
string +="                                                \n"
string +="                                      N600      N601      N602      N603        \n"
string +="                                      N610      N611      N612      N613        \n"
string +="                                      N620      N621      N622      N623        \n"
string +="                                      N630      N631      N632      N633        \n"
string +="                                                \n"

def getGhost(board):
    escape = True
    for row in board:
        for cell in row:
            if cell!=None:
                if cell.inMotion:
                    escape = False
                    break
        else:
            continue
        break

    if escape:
        return board
    
    copy_ = copy.deepcopy(board)
    copy__ = copy.deepcopy(board)
    while True:
        copy_,lock = move(copy_,"down",False)
        if not lock:
            break

    indexes = []
    
    for i in range(len(copy_)):
        for j in range(len(copy_[i])):
            if copy_[i][j]!=None:
                if copy_[i][j].inMotion:
                    copy_[i][j].colour = chr(int(copy_[i][j].colour)+65)
                    copy_[i][j].inMotion = False
                    indexes.append((i,j))

    for index in indexes:
        if copy__[index[0]][index[1]]==None:
            copy__[index[0]][index[1]] = copy_[index[0]][index[1]]

    return copy__

def replaceString(string,subString,idx):
    return string[:idx]+subString+string[idx+10:]

def drawboard(board_,extraVars={}):
    board = copy.deepcopy(board_)
    if ghost:
        board = getGhost(board)
        
    empty = string
    for key in extraVars:
        empty += key+"="+str(extraVars[key])+", "
    empty = empty[:-2]
    empty += "\n"
    if showFPS:
        try:
            empty += "FPS: "+str(round(1/(time.time()-dt),None))
        except:
            empty += "FPS: inf"
    for i in range(4,len(board)):
        for j,cell in enumerate(board[i]):
            sub = "█" if j==0 else " "
            sub += "0" if len(str(i))==1 else ""
            sub += (str(i)+str(j)+"       ")
            idx = string.find(sub)+1
            if cell!=None:
                empty = replaceString(empty,cell.string(),idx)
            else:
                empty = replaceString(empty,"  ########",idx)

    heldPiece = getPiece(held)
    for i in range(len(heldPiece)):
        for j,cell in enumerate(heldPiece[i]):
            sub = "H"+str(i)+str(j)+"       "
            idx = string.find(sub)
            if cell!=None:
                empty = replaceString(empty,cell.string(),idx)
            else:
                empty = replaceString(empty,"  ########",idx)

    for x,name in enumerate(nex[:-1]):
        nextPiece = getPiece(name)
        for i in range(len(nextPiece)):
            for j,cell in enumerate(nextPiece[i]):
                sub = "N"+str(x+1)+str(i)+str(j)+"      "
                idx = string.find(sub)
                if cell!=None:
                    empty = replaceString(empty,cell.string(),idx)
                else:
                    empty = replaceString(empty,"  ########",idx)

    empty = empty.replace("#","")
    empty = empty.replace(">A<",gh_red)
    empty = empty.replace(">B<",gh_orange)
    empty = empty.replace(">C<",gh_yellow)
    empty = empty.replace(">D<",gh_green)
    empty = empty.replace(">E<",gh_blue)
    empty = empty.replace(">F<",gh_cyan)
    empty = empty.replace(">G<",gh_purple)
    empty = empty.replace(">0<",red)
    empty = empty.replace(">1<",orange)
    empty = empty.replace(">2<",yellow)
    empty = empty.replace(">3<",green)
    empty = empty.replace(">4<",blue)
    empty = empty.replace(">5<",cyan)
    empty = empty.replace(">6<",purple)
    empty = empty.replace(">7<",gray)
    empty = empty.replace("","")
    empty = empty.replace("","")
    empty = empty.replace("","")

    print(empty,end="\r")

def move(board,direction,lock=True):
    if direction == "down":
        move = True
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]!=None:
                    if board[i][j].inMotion == True:
                        if i+1 == len(board):
                            move = False
                            break
                        if board[i+1][j]!=None:
                            if board[i+1][j].inMotion == False:
                                move = False
                                break
                    
            else:
                continue
            break

        if move:
            for i in range(len(board)-1,-1,-1):
                for j in range(len(board[i])):
                    if board[i][j]!=None:
                        if board[i][j].inMotion == True:
                            board[i][j],board[i+1][j] = (None,board[i][j])
            return board,True

        else:
            if lock:
                for i in range(len(board)-1,-1,-1):
                    for j in range(len(board[i])):
                        if board[i][j]!=None:
                            if board[i][j].inMotion == True:
                                board[i][j].inMotion = False
                                if graying:
                                    board[i][j].colour = 7
            return board,False

    if direction == "right":
        move = True
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]!=None:
                    if board[i][j].inMotion == True:
                        if j+1 == len(board[i]):
                            move = False
                            break
                        if board[i][j+1]!=None:
                            if board[i][j+1].inMotion == False:
                                move = False
                                break
                    
            else:
                continue
            break

        if move:
            for i in range(len(board)):
                for j in range(len(board[i])-1,-1,-1):
                    if board[i][j]!=None:
                        if board[i][j].inMotion == True:
                            board[i][j],board[i][j+1] = (None,board[i][j])
            return board,True

        else:
            return board,False

    if direction == "left":
        move = True
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]!=None:
                    if board[i][j].inMotion == True:
                        if j-1 == -1:
                            move = False
                            break
                        if board[i][j-1]!=None:
                            if board[i][j-1].inMotion == False:
                                move = False
                                break
                    
            else:
                continue
            break

        if move:
            for i in range(len(board)):
                for j in range(len(board[i])):
                    if board[i][j]!=None:
                        if board[i][j].inMotion == True:
                            board[i][j],board[i][j-1] = (None,board[i][j])
            return board,True

        else:
            return board,False

def getMinimal(array_):
    array = copy.deepcopy(array_)
    for i in range(len(array)):
        for j in range(len(array[i])):
            if array[i][j]!=None:
                if array[i][j].inMotion:
                    array[i][j] = array[i][j].colour
                else:
                    array[i][j] = None
    return array

def getSubArray(board_,sub):
    board = [[None,None,None,None,None,None]+x+[None,None,None,None,None,None] for x in board_]
    board = [[None for i in range(len(board[0]))] for j in range(6)]+board+[[None for i in range(len(board[0]))] for j in range(6)]
    for i in range(len(board)-len(sub)+1):
        for j in range(len(board[i])-len(sub[0])+1):
            isHere = True
            for y in range(len(sub)):
                if board[i+y][j:j+len(sub[0])]!=sub[y]:
                    isHere = False
                    break
            if isHere:
                return (i-6,j-6)

    return (-1,-1)

def pureRotate(piece,c,direction):
    newRot = (c+direction)%4
    return eval("copy.deepcopy("+piece+"Rot["+str(newRot)+"])")

def attemptPlace(board,piece,pos):
    newboard = copy.deepcopy(board)
    for i in range(len(piece)):
        for j in range(len(piece[i])):
            if piece[i][j]!=None:
                if i+pos[1]>=len(newboard) or i+pos[1]<0 or j+pos[0]>=len(newboard[0]) or j+pos[0]<0:
                    return False,None
                if newboard[i+pos[1]][j+pos[0]]!=None:
                    return False,None
                newboard[i+pos[1]][j+pos[0]] = piece[i][j]
            
    return True,newboard

def rotate(board_,piece,direction):
    board = copy.deepcopy(board_)
    global orient
    ogboard = copy.deepcopy(board)
    pure = pureRotate(piece,orient,direction)
    unrotated = pureRotate(piece,orient,0)
    minimalPiece = getMinimal(unrotated)
    minimalBoard = getMinimal(board)
    y,x = getSubArray(minimalBoard,minimalPiece)
    if (x,y)!=(-1,-1):
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]!=None:
                    if board[i][j].inMotion:
                        board[i][j] = None

        if direction!=2:
            if piece=="i":
                kicklist = kicki[str(orient)+str((orient+direction)%4)]
            else:
                kicklist = kickjlszt[str(orient)+str((orient+direction)%4)]
        else:
            kicklist = oneEightyKicks[str(orient)+str((orient+direction)%4)]

        for kick in kicklist:
            success,newboard = attemptPlace(board,pure,(x+kick[0],y-kick[1]))
            if success:
                orient = (orient+direction)%4
                return newboard

    return ogboard
    

def clearLines(board):
    global combo
    cleared = False
    for i in range(len(board)):
        filled = True
        for cell in board[i]:
            if cell == None:
                filled = False
                break
            else:
                if cell.inMotion:
                    filled = False
                    break
        if filled:
            cleared = True
            board[i] = ["#" for x in range(10)]

    if cleared:
        combo += 1
        if combo>15:
            combo = 15
    else:
        combo = 0

    i = len(board)-2

    while i>-1:
        if board[i+1]==["#" for x in range(10)]:
            for j in range(i,0,-1):
                board[j+1],board[j] = (board[j],board[j-1])
            board[0] = [None for x in range(10)]
            i+=1
        i-=1

    return board

def boardState(board):
    array = [[None for i in range(len(board[0]))] for j in range(len(board))]
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j]!=None:
                array[i][j] = board[i][j].colour
    return array

onGround = False
lockBool = False
timeOnGround = 0

r = True
updateNext = False

lost = False

#main update function

def update():
    global board,wait,timea,cancelS,cancelW,delay,timeheld,dp,ap,dcded,canhold,right,left,up,timeOnGround,onGround,lockBool,dt,combo,updateNext,lost
    dt = time.time()
    og = boardState(board)
    if not lost:
        moving = False
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]!=None:
                    if board[i][j].inMotion:
                        moving = True
                        break
            else:
                continue
            break

        wait_deny = False

        if not moving:
            board = clearLines(board)
            lost = hasLost()
            if not lost:
                if r:
                    place()
                if combo!=0:
                    combos()
            else:
                lose()
            spawnPiece()
            cancelS = True
            timeheld = time.time()
            delay = 0
            dcded = False
            lockBool = False
            onGround = False
            wait_deny = True
            canhold = True

        if k.is_pressed(holdKey):
            if canhold:
                holdPiece()
                lockBool = False
                onGround = False
                wait_deny = True
                canhold = False

        if directionChangeCancel:
            if not(k.is_pressed(rightKey) or k.is_pressed(leftKey)):
                delay = 0
        else:
            if dp:
                if not k.is_pressed(rightKey):
                    dp = False
                    delay = 0
            if ap:
                if not k.is_pressed(leftKey):
                    ap = False
                    delay = 0
        
        if (not(k.is_pressed(rightKey) and k.is_pressed(leftKey)))and(k.is_pressed(rightKey) or k.is_pressed(leftKey)):
            if time.time()-timeheld >= delay:
                delay = das*frame if delay == 0 else arr*frame
                if dcded:
                    delay = arr*frame
                    dcded = False
                timeheld = time.time()
                if arr!=0:
                    if k.is_pressed(rightKey):
                        dp = True
                        board,moved = move(board,"right")
                    if k.is_pressed(leftKey):
                        ap = True
                        board,moved = move(board,"left")

                else:
                    if k.is_pressed(rightKey):
                        dp = True
                        while True:
                            board,moved = move(board,"right")
                            if not moved:
                                break
                    if k.is_pressed(leftKey):
                        ap = True
                        while True:
                            board,moved = move(board,"left")
                            if not moved:
                                break

        if directionChangeCancel:
            if not(k.is_pressed(rightKey) or k.is_pressed(leftKey)):
                delay = 0
        else:
            if dp:
                if not k.is_pressed(rightKey):
                    dp = False
                    delay = 0
            if ap:
                if not k.is_pressed(leftKey):
                    ap = False
                    delay = 0

        if k.is_pressed(counterClockwiseKey):
            if left:
                left = False
                timeOnGround = time.time()
                board = rotate(board,current,-1)
        else:
            left = True

        if k.is_pressed(clockwiseKey):
            if right:
                right = False
                timeOnGround = time.time()
                board = rotate(board,current,1)
        else:
            right = True

        if k.is_pressed(oneEightyKey):
            if up:
                up = False
                timeOnGround = time.time()
                board = rotate(board,current,2)
        else:
            up = True

        if gravity!=0:
            wait = 1/gravity
        else:
            wait = float("+inf")
        if k.is_pressed(softDropKey) and not cancelS:
            wait /= sdf
            if sdf==float("+inf"):
                wait = 0
            if wait == 0:
                while True:
                    board,lock = move(board,"down",False)
                    if not lock:
                        break
                delay = dcd*frame
                dcded = True

        if not k.is_pressed(softDropKey):
            cancelS = False

        if k.is_pressed(hardDropKey) and not cancelW:
            wait = 0
            while True:
                board,lock = move(board,"down")
                if not lock:
                    break
            cancelW = True

        if not k.is_pressed(hardDropKey):
            cancelW = False

        if (wait!=0)and(time.time()-timea>=wait):
            timea = time.time()
            board,moved_ = move(board,"down",lockBool)
            if not moved_:
                if not onGround:
                    onGround = True
                    timeOnGround = time.time()

        if updateNext:
            updateNext = False
            timeOnGround = time.time()

        if onGround:
            if time.time()-timeOnGround>=(lock_delay*frame):
                lockBool = True
                
        if wait_deny or lockBool:
            timea = time.time()
            move(board,"down")
            wait_deny = False

    else:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]!=None:
                    board[i][j].colour = 7

    if showFPS:
        drawboard(board)
    else:
        if boardState(board)!=og:
            updateNext = True
            drawboard(board)

    return

#main loop

disable.start()

spawnPiece()

pcNum = 7
pc = 1

while True:
    test = pcNum
    #pc practice keys
    if k.is_pressed("f1"): pcNum = 7
    elif k.is_pressed("f2"): pcNum = 4
    elif k.is_pressed("f3"): pcNum = 1
    elif k.is_pressed("f4"): pcNum = 5
    elif k.is_pressed("f5"): pcNum = 2
    elif k.is_pressed("f6"): pcNum = 6
    elif k.is_pressed("f7"): pcNum = 3

    #retry deteciton
    if k.is_pressed("r") or test!=pcNum:
        if not rCancel:
            lost = False
            r = False
            rCancel = True
            board = [[None for i in range(10)] for j in range(24)]
            bag = ["z","l","o","s","j","i","t"]
            toDel = sorted(random.sample(range(0,7),7-pcNum),reverse=True)
            for idx in toDel: bag.pop(idx)
            orient = 0
            held = ""
            current = ""
            nex = []
            for i in range(7): nex.append(getName())
    else:
        rCancel = False
    
    update() #the holy function
    
