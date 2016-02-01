import pygame, random, sys, Queue, os
from pygame.locals import *

#Generating the tiled map, along with the start/finish & walls
#The map is 32 by 24.
class Maze:
 def __init__(self, mazeLayer):
  self.mLayer = mazeLayer
  self.mLayer.fill((0, 0, 0, 0)) 	#fill it with black translucent
  self.spawn = [0,23]			#Where the player will spawn
  self.goal  = [31,0]			#Where the player needs to go to win
  
  #Drawing the walls
  self.wallArray = []
  for x in range(0, 182):		#1/4 of the map will be walls
   self.randX = random.randint(0,31) 	#Random x coord
   self.randY = random.randint(0,23) 	#Random y coord
   pos = [self.randX, self.randY]	#place hold variable
   if(pos != self.spawn and pos != self.goal):	#Walls cant spawn on the goal or end zone
    self.wallArray.append(pos)		#push it into the array
    pygame.draw.rect(self.mLayer, (119, 67, 11, 255), (self.randX*20, self.randY*20, 20, 20))
   else:
    x = x - 1	

  #Drawing the goal zone
  pygame.draw.circle(self.mLayer, (0,0,255,255), (self.goal[0]*20+10, self.goal[1]*20+10), 10)
	
  #drawing the grid over everything
  for y in xrange(24):
   pygame.draw.line(self.mLayer, (0,0,0,255), (0, y*20), (640, y*20))
   for x in xrange(32):
    if ( y == 0 ):
     pygame.draw.line(self.mLayer, (0, 0, 0, 255), (x*20, 0), (x*20, 480))
 
 def draw(self, screen):
  screen.blit(self.mLayer, (0, 0))
  
class Player:
 def __init__(self, playerLayer):
  self.smellArray = []			#An array to hold the players smell zones
  self.soundArray = []			#An array to hold the players sound zones
  self.pLayer = playerLayer
  self.pLayer.fill((0, 0, 0, 0))	#reset the player
  self.playX = 0			#The players x coordinate
  self.playY = 23			#The players y coordinate
  self.goal  = [31,0]			#The playets goal zone
  pygame.draw.circle(self.pLayer, (255,0,0,255), (self.playX*20 + 10, self.playY*20 + 10), 10)
  
 #to allow the player to sit still for a turn
 def idle(self):
  self.idleBool = True			#the player is not idle
  #reduce the size of the smells and remove smells at 0
  self.trim = 0	
  #loop through all of the smelly positions
  while(self.trim < len(self.smellArray)):
   #reduce their values by 1
   self.smellArray[self.trim][2] = self.smellArray[self.trim][2] -1
   #if the smell is now 0 remove it!
   if(self.smellArray[self.trim][2] == 0):
    self.smellArray.pop(self.trim)
   #otherwise check the next smelly position
   else:
    self.trim = self.trim + 1

  #you didn't move so remove the sound!
  self.soundArray = []

  #update!
  self.update()

 #moving function to move the player around the grid
 def move(self, xPos, yPos):
  #moving!!
  self.idleBool = False
  #add the smells
  self.smellArray.append([self.playX, self.playY, 10])
  #reduce the size of the smells and remove smells at 0
  self.trim = 0	
  #loop through all of the smelly positions
  while(self.trim < len(self.smellArray)):
   #reduce their values by 1
   self.smellArray[self.trim][2] = self.smellArray[self.trim][2] -1
   #if the smell is now 0 remove it!
   if(self.smellArray[self.trim][2] == 0):
    self.smellArray.pop(self.trim)
   #otherwise check the next smelly position
   else:
    self.trim = self.trim + 1

  #move the player
  self.playX = self.playX + xPos	#update the player's coordinates
  self.playY = self.playY + yPos

  #add the sound ring
  self.soundArray = []			#reset the array after everymovement
  for x in range (-4, 5):		#create a cube of sound around the player
   for y in range (-4, 5):
    self.soundArray.append([self.playX+x, self.playY+y])
  #pop some positions to make the array a circle of positions instead of a cube
  self.soundArray.pop(0)
  self.soundArray.pop(0)
  self.soundArray.pop(5)
  self.soundArray.pop(5)
  self.soundArray.pop(5)
  self.soundArray.pop(12)
  self.soundArray.pop(57)
  self.soundArray.pop(64)
  self.soundArray.pop(64)
  self.soundArray.pop(64)
  self.soundArray.pop(69)
  self.soundArray.pop(69)
 
  #update the player
  self.update()
 
 #collision detection function between the player and walls
 def collide(self, xPos, yPos, maze):
  for x in range (0, len(maze.wallArray)):	#for all of the walls
   if([xPos, yPos] == maze.wallArray[x]):	#if the new position of the player is the same as a wall
    return False				#return false!
   if((xPos < 0) or (xPos > 31) or (yPos < 0) or (yPos > 23)):	#if the player was to walk off the map
    return False				#return false!
  return True					#otherwise return true!
  
 #update function to update everything
 def update(self):
  #reset the player screen
  self.pLayer.fill((0, 0, 0, 0)) 

  #update draw the noise ring
  if(not self.idleBool):
   pygame.draw.circle(self.pLayer, (255,0,0,50), (self.playX*20 + 10, self.playY*20 + 10), 90, 0)

  #update draw all of the smells
  for x in range (0, len(self.smellArray)):
   pygame.draw.circle(self.pLayer, (0,255,0,255), (self.smellArray[x][0]*20 + 10, self.smellArray[x][1]*20 + 10), self.smellArray[x][2], 0)
  
  #Player gets drawn over everyone
  pygame.draw.circle(self.pLayer, (0,0,0,255), (self.playX*20 + 10, self.playY*20 + 10), 10, 0)

  #GG state
  if([self.playX, self.playY] == self.goal):
   GG("The player")

 #draw the player
 def draw(self, screen):
  screen.blit(self.pLayer, (0, 0))

#AI agent NOSE!
class Nose:
 def __init__(self, agentLayer, xPos, yPos):
  self.state = 'p'  #p = patrol, c = chase, a = alerted, 
  self.display = False #if the colour of the agent is going to be displayed
  self.aLayer = agentLayer #using the agent layer
  self.aLayer.fill((0, 0, 0, 0)) #reset the agent layer
  self.agentX = xPos
  self.agentY = yPos
  self.compass = ([1,0], [-1,0], [0,-1], [0,1], [0,0]) #a compass to randomly generate movements
  self.stink = 0 #set stink the agent can smell to 0
  pygame.draw.circle(self.aLayer, (0,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 10, 0)

 #random movement function
 def randMove(self):
  #random movement
  return self.compass[random.randint(0,4)]

 #determind if the next move [xPos, yPos] from pos will collide with a maze wall
 def collideWall(self, pos, xPos, yPos, maze):
  self.temp = [pos[0] + xPos, pos[1] + yPos]
  for x in range (0, len(maze.wallArray)):
   if([self.temp[0], self.temp[1]] == maze.wallArray[x]):
    return False
   if((self.temp[0] < 0) or (self.temp[0] > 31) or (self.temp[1] < 0) or (self.temp[1] > 23)):
    return False
  return True

 #def alert(self, agent):
  #self.state = 'a'
  #self.goal = [agent.agentX, agent.agentY]

 def update(self, maze, player):
  #check to see if the player has moved onto the agent
  if [self.agentX, self.agentY] == [player.playX, player.playY]:
   GG("Nose")

  #the chase state, to hunt down the player
  if(self.state == 'c'):
   #for the different movements (north, south, east and west)
   for x in range (0,4):
    self.nextMove = [self.agentX + self.compass[x][0], self.agentY + self.compass[x][1]]
    #if that move puts him on the player, move there and break
    if(self.nextMove == [player.playX, player.playY]):
     self.agentX = self.nextMove[0]
     self.agentY = self.nextMove[1]
     return
    #for the contents of the smell array
    for y in range (0, len(player.smellArray)):
     #if the next move is equal to a position in the smell array
     if(self.nextMove == [player.smellArray[y][0], player.smellArray[y][1]]):
      #and the stink of that tile is higher than the current tile's
      if(player.smellArray[y][2] > self.stink):
       #update the stink and the move.
       self.stink = player.smellArray[y][2]-1
       self.temp = self.nextMove
   #move the agent
   self.agentX = self.temp[0]
   self.agentY = self.temp[1]
  
  #The patrol state, randomly moves the agent around 
  if(self.state == 'p'):
   #move the agent - looking for avaible positions on the map to move to.
   self.moved = False
   while(self.moved == False): 
    self.nextMove = self.randMove()
    self.canMove = self.collideWall([self.agentX, self.agentY], self.nextMove[0], self.nextMove[1], maze)
    if(self.canMove):
     self.agentX = self.agentX + self.nextMove[0]
     self.agentY = self.agentY + self.nextMove[1]
     self.moved = True
     #if the agent moves onto a smelly tile, enter the chase sate.
     for x in range (0, len(player.smellArray)):
      if([self.agentX, self.agentY] == [player.smellArray[x][0], player.smellArray[x][1]]):
       self.stink = player.smellArray[x][2] - 2
       self.state = 'c'

  #the alerted state, move to the agent that alerted you
  if(self.state == 'a'):
   pass

  #repostion the agent
  pygame.draw.circle(self.aLayer, (0,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 10, 0)

  #if display is on add a coloured circle to show which agent is which
  if self.display == True:
   pygame.draw.circle(self.aLayer, (0,255,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 8, 0)

  #GG nose if the agent catches nose
  if([self.agentX, self.agentY] == [player.playX, player.playY]):
   GG("Nose")

 def draw(self, screen):
  screen.blit(self.aLayer, (0, 0))

#AI agent EAR!
class Ear:
 def __init__(self, agentLayer, xPos, yPos):
  self.state = 'p'  #p = patrol, c = chase, a = alerted
  self.display = False
  self.aLayer = agentLayer
  self.agentX = xPos
  self.agentY = yPos
  self.goal = [0,0]
  self.compass = ([1,0], [-1,0], [0,-1], [0,1], [0,0])
  pygame.draw.circle(self.aLayer, (0,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 10, 0)

 def randMove(self):
  #random movement
  self.randy = random.randint(0,4)
  return self.compass[self.randy]

 def collideWall(self, pos, xPos, yPos, maze):
  self.temp = [pos[0] + xPos, pos[1] + yPos]
  for x in range (0, len(maze.wallArray)):
   if([self.temp[0], self.temp[1]] == maze.wallArray[x]):
    return False
   if((self.temp[0] < 0) or (self.temp[0] > 31) or (self.temp[1] < 0) or (self.temp[1] > 23)):
    return False
  return True

 #heuristic function to return the value of each move
 def heuristic(self, a, b):
   return abs(a[0] - b[0] ) + abs(a[1] - b[1])

 #def alert(self, agent):
  #self.state = 'a'
  #self.goal = [agent.agentX, agent.agentY]

 def update(self, maze, player):
  #check to see if the player has moved onto the agent
  if [self.agentX, self.agentY] == [player.playX, player.playY]:
   GG("Ear")

  #check to see if ear is in the player's sound ring
  for x in range (0, len(player.soundArray)):
   if([self.agentX, self.agentY] == player.soundArray[x]):
    self.goal = [player.playX, player.playY]
    self.state = 'c'
  
  #The patrol state, randomly moves the agent around 
  if(self.state == 'p'):
   #move the agent
   self.moved = False
   while(self.moved == False): 
    self.nextMove = self.randMove()
    self.canMove = self.collideWall([self.agentX, self.agentY], self.nextMove[0], self.nextMove[1], maze)
    if(self.canMove):
     self.agentX = self.agentX + self.nextMove[0]
     self.agentY = self.agentY + self.nextMove[1]
     self.moved = True

  #the chase state, to hunt down the player
  if(self.state == 'c'): 
   self.next = {}
   self.next[self.agentX, self.agentY] = self.heuristic([self.agentX, self.agentY], self.goal)
   for x in range(0,4):
    self.nextMove = [self.agentX + self.compass[x][0], self.agentY + self.compass[x][1]]
    if(self.collideWall([self.nextMove[0], self.nextMove[1]], 0, 0, maze)):
     self.score = self.heuristic(self.nextMove, self.goal)
     self.next[self.nextMove[0], self.nextMove[1]] = self.score	
   
   self.bestMove = [0,0,50]
   for x, y in self.next:
    if self.next[x, y] < self.bestMove[2]:
     self.bestMove = [x, y, self.next[x, y]]

   self.agentX = self.bestMove[0]
   self.agentY = self.bestMove[1]

   self.state = 'p'

  #the alerted state, move to the agent that alerted you
  if(self.state == 'a'):
   pass

  #reposition the agent
  pygame.draw.circle(self.aLayer, (0,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 10, 0)

  #if display is on add a coloured circle to show which agent is which
  if self.display == True:
   pygame.draw.circle(self.aLayer, (255,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 8, 0)

  if([self.agentX, self.agentY] == [player.playX, player.playY]):
   GG("Ear")

 def draw(self, screen):
  screen.blit(self.aLayer, (0, 0))

#AI agent Eyeball!
class Eyeball:
 def __init__(self, agentLayer, xPos, yPos):
  self.state = 'p'  #p = patrol, c = chase, a = alerted, d = disabled
  self.display = False
  self.aLayer = agentLayer
  self.agentX = xPos
  self.agentY = yPos
  self.goal = [0,0]
  self.looking = [0,-1]
  self.sightArray = []
  self.compass = ([1,0], [-1,0], [0,-1], [0,1], [0,0])
  pygame.draw.circle(self.aLayer, (0,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 10, 0)

 def randMove(self):
  #random movement
  self.randy = random.randint(0,4)
  return self.compass[self.randy]

 def collideWall(self, pos, xPos, yPos, maze):
  self.temp = [pos[0] + xPos, pos[1] + yPos]
  for x in range (0, len(maze.wallArray)):
   if([self.temp[0], self.temp[1]] == maze.wallArray[x]):
    return False
   if((self.temp[0] < 0) or (self.temp[0] > 31) or (self.temp[1] < 0) or (self.temp[1] > 23)):
    return False
  return True

 #def alert(self, agent):
  #self.state = 'a'
  #self.goal = [agent.agentX, agent.agentY]

 #line of sight function to create an artifical sight field of the agent
 def lineOfSight(self, direction, maze):
  #reset thhe sight array after everymovement
  self.sightArray = []
  #add his position and reset some other variables
  self.sightArray.append([self.agentX, self.agentY, 1])
  self.loop = 0
  self.canSee = True
  if(direction[0] != 0):
   self.hor = 0
   self.ver = 1
  else:
   self.hor = 1
   self.ver = 0
              
  #create the triangular array of view positions
  while((self.loop < 8) and self.canSee == True):
   self.temp = [self.agentX + (direction[0]*self.loop), self.agentY + (direction[1]*self.loop), 1]
   self.sightArray.append(self.temp)
   if(self.loop > 2):
    self.sightArray.append([self.temp[0] + self.hor, self.temp[1] + self.ver, 1])
    self.sightArray.append([self.temp[0] - self.hor, self.temp[1] - self.ver, 1])
   if(self.loop > 4):
    self.sightArray.append([self.temp[0] + self.hor*2, self.temp[1] + self.ver*2, 1])
    self.sightArray.append([self.temp[0] - self.hor*2, self.temp[1] - self.ver*2, 1])
   if(self.loop > 6):
    self.sightArray.append([self.temp[0] + self.hor*3, self.temp[1] + self.ver*3, 1])
    self.sightArray.append([self.temp[0] - self.hor*3, self.temp[1] - self.ver*3, 1])
   self.loop = self.loop + 1

  #For all of the the walls on the map
  for x in range(0, len(maze.wallArray)):
   self.loop = 0
   #checked against the sight of eyeball
   for y in range(0, len(self.sightArray)):
    #if a wall is directly infront of eyeball make him blind
    if(maze.wallArray[x] == [self.agentX + direction[0], self.agentY + direction[1]]):
     for z in range(0, len(self.sightArray)):
      self.sightArray[z][2] = 0

    #if a wall is in his line of sight
    if(maze.wallArray[x] == [self.sightArray[y][0], self.sightArray[y][1]]):
     #loop through all of his sight again
     for z in range(0, len(self.sightArray)):

      #check the direction hes facing (east)
      if(direction[0] == 1):
       #if the wall is directily infront of him
       if(self.sightArray[z][1] == maze.wallArray[x][1] and self.sightArray[z][0] > maze.wallArray[x][0]):  
        #delete all of the approprate sight fields behind the wall
        self.sightArray[z][2] = 0

       #Do more checking!! It's long but produces an accurate line of sight!! its pretty cool
       for p in range(1,4):
        if(maze.wallArray[x][1] == self.agentY):
         if((self.sightArray[z][1] == maze.wallArray[x][1] + p or self.sightArray[z][1] == maze.wallArray[x][1] - p) and self.sightArray[z][0] > maze.wallArray[x][0] + p - 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][1] >  self.agentY):
         if(self.sightArray[z][1] == maze.wallArray[x][1] + p and self.sightArray[z][0] > maze.wallArray[x][0] + p - 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][1] <  self.agentY):
         if(self.sightArray[z][1] == maze.wallArray[x][1] - p and self.sightArray[z][0] > maze.wallArray[x][0] + p - 1):
          self.sightArray[z][2] = 0

      #check the direction hes facing (west)
      if(direction[0] == -1):
       if(self.sightArray[z][1] == maze.wallArray[x][1] and self.sightArray[z][0] < maze.wallArray[x][0]):  
        self.sightArray[z][2] = 0

       for p in range(1,4):
        if(maze.wallArray[x][1] == self.agentY):
         if((self.sightArray[z][1] == maze.wallArray[x][1] + p or self.sightArray[z][1] == maze.wallArray[x][1] - p) and self.sightArray[z][0] < maze.wallArray[x][0] - p + 1):
          self.sightArray[z][2] = 0       
        if(maze.wallArray[x][1] > self.agentY):
         if(self.sightArray[z][1] == maze.wallArray[x][1] + p and self.sightArray[z][0] < maze.wallArray[x][0] - p + 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][1] < self.agentY):
         if(self.sightArray[z][1] == maze.wallArray[x][1] - p and self.sightArray[z][0] < maze.wallArray[x][0] - p + 1):
          self.sightArray[z][2] = 0

      #check the direction hes facing (south)
      if(direction[1] == 1):
       if(self.sightArray[z][0] == maze.wallArray[x][0] and self.sightArray[z][1] > maze.wallArray[x][1]):  
        self.sightArray[z][2] = 0

       for p in range(1,4):
        if(maze.wallArray[x][0] == self.agentX):
         if((self.sightArray[z][0] == maze.wallArray[x][0] + p or self.sightArray[z][0] == maze.wallArray[x][0] - p) and self.sightArray[z][1] > maze.wallArray[x][1] + p - 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][0] > self.agentX):
         if(self.sightArray[z][0] == maze.wallArray[x][0] + p and self.sightArray[z][1] > maze.wallArray[x][1] + p - 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][0] < self.agentX):
         if(self.sightArray[z][0] == maze.wallArray[x][0] - p and self.sightArray[z][1] > maze.wallArray[x][1] + p - 1):
          self.sightArray[z][2] = 0

      #check the direction hes facing (north)
      if(direction[1] == -1):
       if(self.sightArray[z][0] == maze.wallArray[x][0] and self.sightArray[z][1] < maze.wallArray[x][1]):  
        self.sightArray[z][2] = 0

       for p in range(1,4):
        if(maze.wallArray[x][0] == self.agentX):
         if((self.sightArray[z][0] == maze.wallArray[x][0] + p or self.sightArray[z][0] == maze.wallArray[x][0] - p) and self.sightArray[z][1] < maze.wallArray[x][1] - p + 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][0] > self.agentX):
         if(self.sightArray[z][0] == maze.wallArray[x][0] + p and self.sightArray[z][1] < maze.wallArray[x][1] - p + 1):
          self.sightArray[z][2] = 0
        if(maze.wallArray[x][0] < self.agentX):
         if(self.sightArray[z][0] == maze.wallArray[x][0] - p and self.sightArray[z][1] < maze.wallArray[x][1] - p + 1):
          self.sightArray[z][2] = 0

 #heuristic function to return the value of each move
 def heuristic(self, a, b):
   return abs(a[0] - b[0] ) + abs(a[1] - b[1])

 def update(self, maze, player): 
  #check to see if the player has moved onto the agent
  if [self.agentX, self.agentY] == [player.playX, player.playY]:
   GG("Eyeball")
 
  #check to see if the player is in the agent's line of sight
  for x in range(0, len(self.sightArray)):
   if(self.sightArray[x][2] == 1 and ([self.sightArray[x][0], self.sightArray[x][1]] == [player.playX, player.playY])):
    #if he is change the state to chase
    self.state = 'c'

  #The patrol state, randomly moves the agent around 
  if(self.state == 'p'):
   #move the agent
   self.moved = False
   #same randome movement ...
   while(self.moved == False): 
    self.nextMove = self.randMove()
    self.canMove = self.collideWall([self.agentX, self.agentY], self.nextMove[0], self.nextMove[1], maze)
    if(self.canMove):
     self.agentX = self.agentX + self.nextMove[0]
     self.agentY = self.agentY + self.nextMove[1]
     if(self.nextMove != [0,0]):
      self.looking = self.nextMove
     self.lineOfSight(self.looking, maze)
     self.moved = True
  
  #A* search algorithm
  self.frontier = Queue.PriorityQueue()
  self.frontier.put([self.agentX, self.agentY], 0)
  self.came_from = {}
  self.cost_so_far = {}
  self.came_from[self.agentX, self.agentY]= [0, 0]
  self.cost_so_far[self.agentX, self.agentY] = 0
  #the chase state, to hunt down the player
  if(self.state == 'c'):
   #the goal position is the player's position
   self.goal = [player.playX, player.playY]
   
   #if eyeball isnt already standing on the player
   if(not [self.agentX, self.agentY] == self.goal):
    #determind the best possible route to the player
    while not self.frontier.empty():
     self.current = self.frontier.get()

     #break out of the while loop when we find the player
     if self.current == self.goal:
      break

     #check the four compass directions
     for x in range (0,4):
      #create a new cost of movement
      self.new_cost = self.cost_so_far[self.current[0], self.current[1]] + 1
      #create the next possible movement
      self.next = (self.current[0] + self.compass[x][0], self.current[1] + self.compass[x][1])
      #if the next possible movement hasn't already occured, and the move is cheaper than the previous
      if self.next not in self.cost_so_far or self.new_cost < self.cost_so_far[self.next[0], self.next[1]]:
       #if the next movement doesn't move eyeball into a wall or off the screen
       if(self.collideWall([self.next[0], self.next[1]], 0, 0, maze)):
        #update the costs
        self.cost_so_far[self.next[0], self.next[1]] = self.new_cost
        #create a heuristic 
        self.priority = self.new_cost + self.heuristic(self.goal, self.next)
        #add the new position to the queue
        self.frontier.put([self.next[0], self.next[1]], self.priority) 
        #update the came from list to enable backtracking
        self.came_from[self.next[0], self.next[1]] = self.current
 
    #reverse engineer the path to create the route to the player
    self.path = [0, 0]
    self.current = self.goal
    self.path.append(self.current)
    while self.current != [self.agentX, self.agentY]:
     self.current = self.came_from[self.current[0], self.current[1]]
     self.path.append(self.current)
    self.path.reverse() 

    #update the line of sight and position of the agent
    self.looking = [self.path[1][0] - self.agentX, self.path[1][1] - self.agentY]
    self.agentX = self.path[1][0]
    self.agentY = self.path[1][1]
    self.lineOfSight(self.looking, maze)

  #the alerted state, move to the agent that alerted you
  #if(self.state == 'a'):
  # pass

  #draw sight field
  if self.display == True:
   for x in range (0, len(self.sightArray)):
    if(self.sightArray[x][2] == 1):
     pygame.draw.rect(self.aLayer, (0, 0, 0, 50), (self.sightArray[x][0]*20, self.sightArray[x][1]*20, 20, 20))

  #repostion the agent
  pygame.draw.circle(self.aLayer, (0,0,0,255), (self.agentX*20 + 10, self.agentY*20 + 10), 10, 0)

  #if display is on add a coloured circle to show which agent is which
  if self.display == True:
   pygame.draw.circle(self.aLayer, (211,211,211,255), (self.agentX*20 + 10, self.agentY*20 + 10), 8, 0)

  if([self.agentX, self.agentY] == [player.playX, player.playY]):
   GG("Eyeball")

 def draw(self, screen):
  screen.blit(self.aLayer, (0, 0))

#GG function, closes the program and prints who won.
def GG(winner):
 print(winner + ' wins!')
 
 #Holding some stats
 filePath = os.path.realpath('AIStats')
 statsFile = open(filePath, 'r+')
 totalGames = int(statsFile.readline())
 playerWins = int(statsFile.readline())
 earWins = int(statsFile.readline())
 noseWins = int(statsFile.readline())
 eyeballWins = int(statsFile.readline())

 #update the game stats
 totalGames = totalGames + 1
 if winner == 'The player':
  playerWins = playerWins + 1
 elif winner == 'Ear':
  earWins = earWins + 1
 elif winner == 'Nose':
  noseWins = noseWins + 1
 elif winner == 'Eyeball':
  eyeballWins = eyeballWins + 1

 #deleting the contents of the file
 statsFile.seek(0)
 statsFile.truncate()

 #updating the stats
 statsFile.writelines([str(totalGames)+'\n', str(playerWins)+'\n', str(earWins)+'\n', str(noseWins)+'\n', str(eyeballWins)]) 

 #closing the file
 statsFile.close()

 #exiting the game
 sys.exit()
 
#function to update all 3 agents at the same time.
def updateAgents(agentLayer, newNose, newEar, newEyeball, newMaze, newPlayer):
 agentLayer.fill((0, 0, 0, 0)) #reset the agent layer
 if(newNose.state != 'd'):
  newNose.update(newMaze, newPlayer)
 if(newEar.state != 'd'):
  newEar.update(newMaze, newPlayer)
 if(newEyeball.state != 'd'):
  newEyeball.update(newMaze, newPlayer)

#function to call all 3 agent draws at the same time, also if the agent state is 'd' it is disabled and will not update
#see the key presses bellow for more info
def drawAgents(newNose, newEar, newEyeball, screen):
 if(newNose.state != 'd'): 
  newNose.draw(screen)
 if(newEar.state != 'd'):
  newEar.draw(screen)
 if(newEyeball.state != 'd'):
  newEyeball.draw(screen)

#main function
def main():

 pygame.init() #initialize pygame
 screen = pygame.display.set_mode((640,480)) #set the screen width and size
 pygame.display.set_caption('My Simple AI Game!') #name the game
 pygame.mouse.set_visible(0) #hide tha mouse

 background = pygame.Surface(screen.get_size())
 background = background.convert()
 background.fill((255, 255, 255))

 mazeLayer = pygame.Surface(screen.get_size())
 mazeLayer = mazeLayer.convert_alpha()
 mazeLayer.fill((0, 0, 0, 0))
 
 playerLayer = pygame.Surface(screen.get_size())
 playerLayer = playerLayer.convert_alpha()
 playerLayer.fill((0, 0, 0, 0))

 agentLayer = pygame.Surface(screen.get_size())
 agentLayer = agentLayer.convert_alpha()
 agentLayer.fill((0, 0, 0, 0))

 newMaze = Maze(mazeLayer) #create an instance of the maze
 newPlayer = Player(playerLayer) #create an instance of the player
 
 #generating a spawn for the enemies
 randX = random.randint(0,31) #Random x coord
 randY = random.randint(0,23) #Random y coord
 newNose = Nose(agentLayer, randX, randY)

 randX = random.randint(0,31) #Random x coord
 randY = random.randint(0,23) #Random y coord
 newEar = Ear(agentLayer, randX, randY)

 randX = random.randint(0,31) #Random x coord
 randY = random.randint(0,23) #Random y coord
 newEyeball = Eyeball(agentLayer, randX, randY)

 screen.blit(background, (0,0))#blit the bakground
 pygame.display.flip()
 clock = pygame.time.Clock()

 while 1:
  clock.tick(60)
  for event in pygame.event.get():
   if event.type == QUIT:
    return
   elif event.type == KEYDOWN:
    if event.key == K_UP:	#Up key press - calls the collide function to see if the player can make this move
     move = newPlayer.collide(newPlayer.playX, newPlayer.playY-1, newMaze)
     if(move):
      newPlayer.move(0,-1)	#If the move is availible (not moving into a wall or off the map) then move the player
      updateAgents(agentLayer, newNose, newEar, newEyeball, newMaze, newPlayer) #and update all of the agents
    elif event.key == K_DOWN:
     move = newPlayer.collide(newPlayer.playX, newPlayer.playY+1, newMaze)
     if(move):
      newPlayer.move(0,1)
      updateAgents(agentLayer, newNose, newEar, newEyeball, newMaze, newPlayer)
    elif event.key == K_LEFT:
     move = newPlayer.collide(newPlayer.playX-1, newPlayer.playY, newMaze)
     if(move):
      newPlayer.move(-1,0)
      updateAgents(agentLayer, newNose, newEar, newEyeball, newMaze, newPlayer)
    elif event.key == K_RIGHT:
     move = newPlayer.collide(newPlayer.playX+1, newPlayer.playY, newMaze)
     if(move):
      newPlayer.move(1,0)
      updateAgents(agentLayer, newNose, newEar, newEyeball, newMaze, newPlayer)
    elif event.key == K_SPACE:
     newPlayer.idle()
     updateAgents(agentLayer, newNose, newEar, newEyeball, newMaze, newPlayer)
    elif event.key == K_z: #the 'z' 'x' and 'c' keys will disable the different agents (for debugging)
     if(newNose.state == 'd'):
      newNose.state = 'p'
     else:
      newNose.state = 'd'
    elif event.key == K_x:
     if(newEar.state == 'd'):
      newEar.state = 'p'
     else:
      newEar.state = 'd'
    elif event.key == K_c:
     if(newEyeball.state == 'd'):
      newEyeball.state = 'p'
     else:
      newEyeball.state = 'd'
    elif event.key == K_v: #the 'v' key will colour the agents and show eyeball's line of sight
     if(newNose.display == False):
      newNose.display = True
      newEar.display = True
      newEyeball.display = True
     else:
      newNose.display = False
      newEar.display = False
      newEyeball.display = False
    elif event.key == K_ESCAPE:
     return
  
  screen.blit(background, (0,0))
  newMaze.draw(screen)
  newPlayer.draw(screen)
  drawAgents(newNose, newEar, newEyeball, screen)
  pygame.display.flip()

if __name__ == '__main__': main()
