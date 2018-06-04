#!/usr/bin/env python
# Boid implementation in Python using PyGame
# Ben Dowling - www.coderholic.com

import sys, pygame, random, math
import QLearnBoid
import search_util
from collections import defaultdict
from QLearnBoid import QLearnBoid
from QLearnBoid import followLeaderBoidFeatureExtractorV2, distance, threeBirdFlock, distanceObj, distanceBirdCoord
import copy

pygame.init()

size = width, height = 1000, 600

def defineMaze():
    obstacles = defaultdict(bool)
    for r in range(width):
        for c in range(height):
            obstacles[(r,c)] = False

    for r in range(95, 105):
        for c in range(0, 400):
            obstacles[(r,c)] = True

    for r in range(195, 205):
        for c in range(0, 100):
            obstacles[(r,c)] = True
        for c in range(200, 400):
            obstacles[(r,c)] = True

    for r in range(295, 305):
        for c in range(200, 300):
            obstacles[(r,c)] = True

    for r in range(395, 405):
        for c in range(100, 300):
            obstacles[(r,c)] = True

    for r in range(495, 505):
        for c in range(100, 500):
            obstacles[(r,c)] = True

    for r in range(595, 605):
        for c in range(100, 600):
            obstacles[(r,c)] = True

    for r in range(695, 705):
        for c in range(100, 300):
            obstacles[(r,c)] = True

    for r in range(795, 805):
        for c in range(300, 500):
            obstacles[(r,c)] = True

    for r in range(795, 805):
        for c in range(0, 200):
            obstacles[(r,c)] = True

    for r in range(895, 905):
        for c in range(100, 1000):
            obstacles[(r,c)] = True

    for r in range(195, 405):
        for c in range(95, 105):
            obstacles[(r,c)] = True

    for r in range(495, 605):
        for c in range(95, 105):
            obstacles[(r,c)] = True

    for r in range(195, 505):
        for c in range(395, 405):
            obstacles[(r,c)] = True

    for r in range(95, 505):
        for c in range(495, 505):
            obstacles[(r,c)] = True

    for r in range(695, 805):
        for c in range(295, 305):
            obstacles[(r,c)] = True

    for r in range(695, 905):
        for c in range(495, 505):
            obstacles[(r,c)] = True
    return obstacles

obstacles = defineMaze()
black = 0, 0, 0
white = 255, 255, 255
minvel, maxvel = 0, 3
RED = [255, 0, 0]

maxVelocity = 3
numBoids = 15
boids = []

crashdistance = 30


leader_exists = True

if leader_exists:
    numBoids += 1

class Boid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocityX = random.randint(1, 10) / 10.0
        self.velocityY = random.randint(1, 10) / 10.0

    "Return the distance from another boid"
    def distance(self, boid):
        distX = self.x - boid.x
        distY = self.y - boid.y        
        return math.sqrt(distX * distX + distY * distY)

    def getXVelocity(self):
        return self.velocityX

    def getYVelocity(self):
        return self.velocityY

    "Move closer to a set of boids"
    def moveCloser(self, boids):
        if len(boids) < 1: return
            
        # calculate the average distances from the other boids
        avgX = 0
        avgY = 0
        for boid in boids:
            if boid.x == self.x and boid.y == self.y:
                continue
                
            avgX += (self.x - boid.x)
            avgY += (self.y - boid.y)

        avgX /= len(boids)
        avgY /= len(boids)

        # set our velocity towards the others
        distance = math.sqrt((avgX * avgX) + (avgY * avgY)) * -1.0
       
        self.velocityX -= (avgX / 100.0)
        self.velocityY -= (avgY / 100.0)
        
    "Move with a set of boids"
    def moveWith(self, boids):
        if len(boids) == 0: return
        # calculate the average velocities of the other boids
        avgX = 0
        avgY = 0
                
        for boid in boids:
            #avgX += boid.velocityX
            #avgY += boid.velocityY
            avgX += boid.getXVelocity()
            avgY += boid.getYVelocity()

        avgX /= len(boids)
        avgY /= len(boids)

        # set our velocity towards the others
        self.velocityX += (avgX / 8)
        self.velocityY += (avgY / 8)

    
    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        if len(boids) < 1: return
        
        distanceX = 0
        distanceY = 0
        numClose = 0

        for boid in boids:
            distance = self.distance(boid)
            if  distance < minDistance:
                numClose += 1
                xdiff = (self.x - boid.x) 
                ydiff = (self.y - boid.y) 
                
                if xdiff >= 0: xdiff = math.sqrt(minDistance) - xdiff
                elif xdiff < 0: xdiff = -math.sqrt(minDistance) - xdiff
                
                if ydiff >= 0: ydiff = math.sqrt(minDistance) - ydiff
                elif ydiff < 0: ydiff = -math.sqrt(minDistance) - ydiff

                distanceX += xdiff 
                distanceY += ydiff 
        
        if numClose == 0:
            return
            
        self.velocityX -= distanceX / 5
        self.velocityY -= distanceY / 5
        
    "Perform actual movement based on our velocity"
    def move(self):
        if abs(self.velocityX) > maxVelocity or abs(self.velocityY) > maxVelocity:
            scaleFactor = maxVelocity / max(abs(self.velocityX), abs(self.velocityY))
            self.velocityX *= scaleFactor
            self.velocityY *= scaleFactor
        
        self.x += self.velocityX
        self.y += self.velocityY

        # Try wrap around - may need variable width and hieght
        #self.x = (self.x + width) % width
        #self.y = (self.y + height) % height


class LeadBoid(Boid):
    def __init__(self, x, y, isTraining=False):
        self.x = x
        self.y = y

        self.speed = 2
        self.angle = 0.0
        self.direction = [0, 0]
        self.stepCounts = 0
        self.multiple = 1
        self.velocityX = random.uniform(-1,1)
        self.velocityY = random.uniform(-1,1)
        self.isTraining = isTraining

    "Move closer to a set of boids"
    def moveCloser(self, boids):
        return
        
    "Move with a set of boids"
    def moveWith(self, boids):
        return
    
    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        return

    def getXVelocity(self):
        return math.sin(-math.radians(self.angle)) * self.speed

    def getYVelocity(self):
        return -math.cos(math.radians(self.angle)) * self.speed
        
    "Perform actual movement based on our velocity"
    def move(self):

        if self.stepCounts == 20:
            self.multiple = random.uniform(.8,1.2)
            self.stepCounts = 0
            if self.angle == 0: 
                self.angle += 20
        else:
            self.multiple = 1
            self.stepCounts += 1


        self.angle *= self.multiple
        # self.angle += 1
        self.angle = self.angle % 360
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # calculate the position from the direction and speed
        self.x += self.direction[0]*self.speed
        self.y += self.direction[1]*self.speed

        if not self.isTraining:
            if self.x <= 10 or self.x >= width - 10:
                self.angle += 90
            if self.y <= 10 or self.y >= height - 10:
                self.angle += 90


        # self.velocityX += random.uniform(-1,1)
        # self.velocityY += random.uniform(-1,1)
        # if self.velocityX**2 + self.velocityY**2 > maxVelocity**2:
        #     scaleFactor = maxVelocity / max(abs(self.velocityX), abs(self.velocityY))
        #     self.velocityX *= scaleFactor
        #     self.velocityY *= scaleFactor
        
        # self.x += self.velocityX
        # self.y += self.velocityY

        
       
        # Try wrap around - may need variable width and hieght
        #self.x = (self.x + width) % width
        #self.y = (self.y + height) % height

class StraightLineBoid(Boid):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # move across the screen
        self.speed = 3
        self.angle = 90
        self.direction = [1, 0]

    "Move closer to a set of boids"
    def moveCloser(self, boids):
        return
        
    "Move with a set of boids"
    def moveWith(self, boids):
        return
    
    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        return
        
    "Perform actual movement based on our velocity"
    def move(self):
        #self.velocityX += random.uniform(-1,1)
        #self.velocityY += random.uniform(-1,1)
        #if self.velocityX**2 + self.velocityY**2 > maxVelocity**2:
            #scaleFactor = maxVelocity / max(abs(self.velocityX), abs(self.velocityY))
            #self.velocityX *= scaleFactor
            #self.velocityY *= scaleFactor
        self.direction[0] = math.sin(math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        self.x += self.direction[0]*self.speed
        self.y += self.direction[1]*self.speed

        # Try wrap around - may need variable width and hieght
        #self.x = (self.x + width) % width
        #self.y = (self.y + height) % height

class LearningBoid(Boid):
    def __init__(self, x, y, angle = 0.0, speed = 2): 
        self.x = x
        self.y = y
        # move across the screen

        self.speed = speed
        self.angle = angle
        self.direction = [0, 0]

    def getXVelocity(self):
        return math.sin(-math.radians(self.angle)) * self.speed

    def getYVelocity(self):
        return -math.cos(math.radians(self.angle)) * self.speed

    def move(self, action):
        # Assume for now that an action is just an angle movement
        if action[0] != None:
            self.angle += action[0]
            self.speed += action[1]
            if self.speed > maxvel:
                self.speed = maxvel
            elif self.speed < minvel:
                self.speed = minvel
            self.angle = self.angle % 360
            self.direction[0] = math.sin(math.radians(self.angle))
            self.direction[1] = -math.cos(math.radians(self.angle))

            # calculate the position from the direction and speed
            self.x += self.direction[0]*self.speed
            self.y += self.direction[1]*self.speed

class CircleBoid(Boid):
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.speed = 3
        self.angle = 0.0
        self.direction = [0, 0]


    "Move closer to a set of boids"
    def moveCloser(self, boids):
        return
        
    "Move with a set of boids"
    def moveWith(self, boids):
        return
    
    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        return
        
    "Perform actual movement based on our velocity"
    def move(self):
        # We want to just move at a constant 5 degree angle

        self.angle += 1
        self.angle = self.angle % 360
        self.direction[0] = math.sin(-math.radians(self.angle))
        self.direction[1] = -math.cos(math.radians(self.angle))

        # calculate the position from the direction and speed
        self.x += self.direction[0]*self.speed
        self.y += self.direction[1]*self.speed

class SearchBoid(Boid):
    def __init__(self):
        self.x = 50
        self.y = 50
        self.step = 0
        self.speed = 3

        search = search_util.UniformCostSearch(verbose=1)
        search.solve(search_util.MazeProblem((50,50), ((950, 550)), obstacles))
        self.actions = search.actions

    "Move closer to a set of boids"
    def moveCloser(self, boids):
        return
        
    "Move with a set of boids"
    def moveWith(self, boids):
        return
    
    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        return
        
    "Perform actual movement based on our velocity"
    def move(self):
        # We want to just move at a constant 5 degree angle
        # calculate the position from the direction and speed
        if self.step < len(self.actions):
            self.x = self.actions[self.step][0]
            self.y = self.actions[self.step][1]
            self.step += self.speed


'''
screen = pygame.display.set_mode(size)

bird = pygame.image.load("bird.png")
birdrect = bird.get_rect()
lead = pygame.image.load("bird1.png")
leadrect = lead.get_rect()

# create boids at random positions
for i in range(numBoids - 1):
    boids.append(Boid(random.randint(0, width), random.randint(0, height)))

#if leader_exists:
    #boids.append(LeadBoid(random.randint(0, width), random.randint(0, height))) 
   # boids.append(straightLineBoid(30, height / 2.0)) 
    #boids.append(circleBoid(500, 300))


while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    for boid in boids:
        closeBoids = []
        for otherBoid in boids:
            if otherBoid == boid: continue
            distance = boid.distance(otherBoid)
            if distance < 100:
                closeBoids.append(otherBoid)

        
        boid.moveCloser(closeBoids)
        boid.moveWith(closeBoids)  
        boid.moveAway(closeBoids, 30)

        # ensure they stay within the screen space
        # if we roubound we can lose some of our velocity
        
        border = 25
        if boid.x < border and boid.velocityX < 0:
            boid.velocityX = -boid.velocityX * random.random()
        if boid.x > width - border and boid.velocityX > 0:
            boid.velocityX = -boid.velocityX * random.random()
        if boid.y < border and boid.velocityY < 0:
            boid.velocityY = -boid.velocityY * random.random()
        if boid.y > height - border and boid.velocityY > 0:
            boid.velocityY = -boid.velocityY * random.random()
        
            
        boid.move()
        
    screen.fill(white)
    for i in range(len(boids)):
        boid = boids[i]
        if leader_exists and i == len(boids) - 1:
            boidRect = pygame.Rect(leadrect)
            boidRect.x = boid.x
            boidRect.y = boid.y
            screen.blit(lead, boidRect)
        else:
            boidRect = pygame.Rect(birdrect)
            boidRect.x = boid.x
            boidRect.y = boid.y
            screen.blit(bird, boidRect)
    pygame.display.flip()
    pygame.time.delay(1)
'''

def test_rl(rl):
    # Have to redefine this for flocking
    def isfollowing(state, newState):
        # Define following as being within 20-30 units
        # See if it took a step toward the leader correctly
        oldDist = distance(state[0], state[1])
        newDist = distance(newState[0], newState[1])
        follow = 0
        if oldDist >= newDist:
            follow = 1

        # Check we hit the leader
        crash = 0
        if distance(newState[0], newState[1]) < crashdistance - 2:
            crash = 1

        # Check if maintained a good follow distance (i.e. stayed within 7 units of leader)
        stay_follow = 0
        if distance(newState[0], newState[1]) > crashdistance - 2 and distance(newState[0], newState[1]) <= crashdistance + 10:
            stay_follow = 1

    # Super simple test right now with one leader and one 
    # follower controlled by the rl algorithm
    screen = pygame.display.set_mode(size)

    bird = pygame.image.load("bird.png")
    birdrect = bird.get_rect()
    lead = pygame.image.load("bird1.png")
    leadrect = lead.get_rect()

    #leaderBoid = StraightLineBoid(55, height / 2.0)
    #leaderBoid = LeadBoid(500, 300, False)
    #leaderBoid = LeadBoid(55, height / 2.0)
    # Define the start state for our rl algorithm
    #learnerBoid = LearningBoid(25, height / 2.0, 90)
    leaderBoid = CircleBoid(500, 400)
    learnedBoids = []
    #learnedBoids.append(LearningBoid(450, 300, 90))
    #learnedBoids.append(LearningBoid(350, 310, 90))
    #learnedBoids.append(LearningBoid(575, 350, 90))
    learnedBoids.append(LearningBoid(550, 400, 90))
    # Set weights
    #rl.weights = {"distance-delta": -1, "too-close": -5}
    #learnerBoid = LearningBoid(450, 300, 90)
    #learnerBoid2 = LearningBoid(350, 310, 90)

    # Define the start states that will be passed to our learning algorithm
    states = []
    for boid in learnedBoids:
        states.append(((boid.x, boid.y, boid.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height)))
    
    #state = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))
    #state2 = ((learnerBoid2.x, learnerBoid2.y, learnerBoid2.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

    

        # Move both boids
        leaderBoid.move()

        # Move the followers
        for i in range(len(learnedBoids)):
            action = rl.getAction(states[i])
            learnedBoids[i].move(action)
        
        #action = rl.getAction(state)
        #action2 = rl.getAction(state2)
        #learnerBoid.move(action)
        #learnerBoid2.move(action2)

        # Calculate the new states
        for i in range(len(states)):
            states[i] = ((learnedBoids[i].x, learnedBoids[i].y, learnedBoids[i].angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))
        
        #newState = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))
        #newState2 = ((learnerBoid2.x, learnerBoid2.y, learnerBoid2.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))
    
        screen.fill(white)

        #state = newState
        #state2 = newState2

        # Draw the boids
        # Draw the leader
        boidRect = pygame.Rect(leadrect)
        boidRect.x = leaderBoid.x
        boidRect.y = leaderBoid.y
        screen.blit(lead, boidRect)
        pygame.draw.circle(screen, RED, [int(leaderBoid.x), int(leaderBoid.y)], 20, 1)

        # Draw the learners
        for boid in learnedBoids:
            boidRect = pygame.Rect(birdrect)
            boidRect.x = boid.x
            boidRect.y = boid.y
            screen.blit(bird, boidRect)

        #boidRect = pygame.Rect(birdrect)
        #boidRect.x = learnerBoid2.x
        #boidRect.y = learnerBoid2.y
        #screen.blit(bird, boidRect)
        
        pygame.display.flip()
        pygame.time.delay(1)



def test_flock(flock, follow, flock_size):
    # Super simple test right now with one leader and one 
    # follower controlled by the rl algorithm
    screen = pygame.display.set_mode(size)

    bird = pygame.image.load("bird.png")
    birdrect = bird.get_rect()
    lead = pygame.image.load("bird1.png")
    leadrect = lead.get_rect()
    flock_pic = pygame.image.load("flock-bird.png")
    flockrect = flock_pic.get_rect()
    rule_pic = pygame.image.load("rule-bird.png")
    rule_rect = rule_pic.get_rect()

    #leaderBoid = StraightLineBoid(55, height / 2.0)
    leaderBoid = LeadBoid(500, 300, False)

    rule_based = Boid(450, 300)
    # Define the start state for our rl algorithm
    follow_leader = LearningBoid(450, 300, 90)

    follow_state = ((follow_leader.x, follow_leader.y, follow_leader.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))

    flock_birds = []
    for i in range(flock_size):
        flock_birds.append(LearningBoid(random.randint(0, width), random.randint(0, height)))

    flock_states = []
    for i in range(flock_size):
        neighbors = [follow_leader]
        for j in range(flock_size):
            if j != i:
                neighbors.append(flock_birds[j])
        flock_states.append((flock_birds[i], leaderBoid, neighbors, 3))
    
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Draw initial circles 
        screen.fill(white)
        #pygame.draw.circle(screen, RED, [int(leaderBoid.x), int(leaderBoid.y)], 30, 1)

        # Move both boids
        leaderBoid.move()
        
        action_follow = follow.getAction(follow_state)
        follow_leader.move(action_follow)

        for i in range(flock_size):
            action = flock.getAction(flock_states[i])
            flock_birds[i].move(action)


        follow_state = ((follow_leader.x, follow_leader.y, follow_leader.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))
        for i in range(flock_size):
            neighbors = [follow_leader]
            for j in range(flock_size):
                if j != i:
                    neighbors.append(flock_birds[j])
            flock_states[i] = (flock_birds[i], leaderBoid, neighbors, 3)
        
        # Move the followers
        closeBoids = [leaderBoid, follow_leader]
        for otherBoid in flock_birds:
            distance = distanceObj(rule_based, otherBoid)
            if distance < 100:
                closeBoids.append(otherBoid)
        
        # Move rule based boids
        rule_based.moveCloser(closeBoids)
        rule_based.moveWith(closeBoids)  
        rule_based.moveAway(closeBoids, 30)
        rule_based.move()
        
        
        #screen.fill(white)

        # Draw the boids
        # Draw the leader
        lead_rotated = pygame.transform.rotate(lead, leaderBoid.angle)
        boidRect = lead_rotated.get_rect()
        #boidRect = pygame.Rect(lead_rotated)
        boidRect.x = leaderBoid.x
        boidRect.y = leaderBoid.y
        #screen.blit(lead, boidRect)
        screen.blit(lead_rotated, boidRect)
        #pygame.draw.circle(screen, RED, [int(leaderBoid.x), int(leaderBoid.y)], 60, 1)

        # Draw the follower
        boidRect = pygame.Rect(birdrect)
        boidRect.x = follow_leader.x
        boidRect.y = follow_leader.y
        screen.blit(bird, boidRect)
        #pygame.draw.circle(screen, RED, [int(follow_leader.x), int(follow_leader.y)], 30, 1)

        # Draw flockers
        for i in range(flock_size):
            boidRect = pygame.Rect(flockrect)
            boidRect.x = flock_birds[i].x
            boidRect.y = flock_birds[i].y
            screen.blit(flock_pic, boidRect)
        
        # Rule based follower
        boidRect = pygame.Rect(rule_rect)
        boidRect.x = rule_based.x
        boidRect.y = rule_based.y
        #screen.blit(rule_pic, boidRect)
        

        # Draw a circle in the avg location
        avg_x = (leaderBoid.x + follow_leader.x) / 2.0
        avg_y = (leaderBoid.y + follow_leader.y) / 2.0
        #pygame.draw.circle(screen, RED, [int(avg_x), int(avg_y)], 5)

        
        pygame.display.flip()
        #pygame.time.delay(1)

# Perform |numTrials| of the following:
# On each trial, take the MDP |mdp| and an RLAlgorithm |rl| and simulates the
# RL algorithm according to the dynamics of the MDP.
# Each trial will run for at most |maxIterations|.
# Return the list of rewards that we get for each trial.
def simulate_flock(flock_rl, follow_leader, numTrials=20, maxIterations=1000, verbose=False):

    # Have to redefine this for flocking
    def isfollowing(state):
        # Define following as being within 20-30 units
        #if not(distance(state[0], state[1]) > 20 and distance(state[0], state[1]) <= 35):
            #print distance(state[0], state[1])
        return distance(state[0], state[1]) > crashdistance - 5 and distance(state[0], state[1]) <= crashdistance + 15

    def reward(prev_state, new_state):
        # Unpac the states
        boid, leader, birds, velocity = prev_state
        update_boid, update_leader, update_birds, velocity = new_state

        # Calculate the distance to the leader before step
        dist_leader = distanceObj(boid, leader)

        # Get distance to the centroid of flock
        dist = dist_leader
        avg_x = leader.x
        avg_y = leader.y
        for bird in birds:
            avg_x += bird.x
            avg_y += bird.y
        centroid = (avg_x / float(len(birds) + 1), avg_y / float(len(birds) + 1))
        # Distance to centroid before action
        dist_center = distance((boid.x, boid.y), centroid)

        # Updated distance to leader
        updated_distance = distanceObj(update_boid, update_leader)

        # Calculate birds that are too close
        # And re-calc centroid
        number_too_close = 0
        close_birds =  []
        avg_x = update_leader.x
        avg_y = update_leader.y
        if updated_distance < 30:
            close_birds.append(updated_distance)
        bird_distances = []
        for bird in update_birds:
            new_dist = distanceObj(update_boid, bird)
            # See if we are too close
            if new_dist < 30:
                number_too_close += 1
                close_birds.append(new_dist)

            avg_x += bird.x
            avg_y += bird.y

        updated_centroid = (avg_x / float(len(birds) + 1), avg_y / float(len(birds) + 1))

        #Start calculating reward
        # Give bad negative reward if we are too close!
        reward = 0
        if len(close_birds) > 0:
            reward = -5
            #reward = -20
            # Two CLOSE birds!!!
            #if len(close_birds) > 1:
                #reward *= 2
            #return reward

        
        # Move toward the centroid
        updated_dist_center = distance((update_boid.x, update_boid.y), updated_centroid)
        #if dist_leader < 50:
        if updated_dist_center <= dist_center:
            reward += 2
        else:
            reward += 0

        # Move toward the leader with more importance than the center
        updated_distance = distanceObj(update_boid, update_leader)
        #if dist_leader >= 50:
        if dist_leader >= updated_distance:
            reward += 10
            #reward += 100
        else:
            reward -= 5 
            #reward -= 5


        return reward


    totalRewards = []  # The rewards we get on each trial
    following = []
    for trial in range(numTrials):
        # We want to start doing the simulation
        # Let us start by placing down a the leader and
        # the learning follower
        leaderBoid = LeadBoid(500, 300)
        # Define the start state for our fixed follow leader algorithm
        follow_boid = LearningBoid(450, 300, 90)

        # Define the start state for our flock algorithm
        flock_boid = LearningBoid(100, 100, 90)

        # Define the start state that will be passed to our learning algorithm
        follow_state = ((follow_boid.x, follow_boid.y, follow_boid.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))
        flock_state = (flock_boid, leaderBoid, [follow_boid], 3)

        #sequence = [state]
        totalDiscount = 1
        totalReward = 0
        time_steps_following = 0
        for _ in range(maxIterations):
            # Save the old state
            # Super ugly???
            save_state = (copy.deepcopy(flock_boid), copy.deepcopy(leaderBoid), [copy.deepcopy(follow_boid)], 3)
            # Get the action predicted by the bird learning algorithm
            follow_leader_a = follow_leader.getAction(follow_state)
            # Move the learning bird
            follow_boid.move(follow_leader_a)
            # Move the leading bird
            leaderBoid.move()

            # Get an action for the flock
            flock_a = flock_rl.getAction(flock_state)
            flock_boid.move(flock_a)

            # Update follow state
            follow_state = ((follow_boid.x, follow_boid.y, follow_boid.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))
            
            # Get the new flock state and reward
            new_flock_state = (flock_boid, leaderBoid, [follow_boid], 3)
            reward1 = reward(save_state, new_flock_state)

            #sequence.append(action)
            #sequence.append(reward)
            #sequence.append(newState)

            flock_rl.incorporateFeedback(flock_state, flock_a, reward1, new_flock_state)

            flock_state = new_flock_state

            totalReward += totalDiscount * reward1
            #if trial % 3 == 0:
                #time_steps_following += 1 if isfollowing(newState) else 0
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        if trial % 3 == 0:
            following.append(time_steps_following)
            flock_rl.printWeights()
        totalRewards.append(totalReward)
    return totalRewards, following

def test_maze(rl):

    # Super simple test right now with one leader and one 
    # follower controlled by the rl algorithm
    screen = pygame.display.set_mode(size)

    bird = pygame.image.load("bird.png")
    birdrect = bird.get_rect()
    lead = pygame.image.load("bird1.png")
    leadrect = lead.get_rect()

    #leaderBoid = StraightLineBoid(55, height / 2.0)
    leaderBoid = SearchBoid()
    #leaderBoid = LeadBoid(55, height / 2.0)
    # Define the start state for our rl algorithm
    #learnerBoid = LearningBoid(25, height / 2.0, 90)
    learnerBoid = LearningBoid(450, 300, 90)
    learnerBoid2 = LearningBoid(350, 310, 90)

    # Define the start state that will be passed to our learning algorithm
    state = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))
    state2 = ((learnerBoid2.x, learnerBoid2.y, learnerBoid2.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))

    background_surface = pygame.Surface((width, height))
    background_surface.fill(white)
    for key in obstacles:
        if obstacles[key]:
            background_surface.set_at(key, black)


    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Move both boids
        leaderBoid.move()

        action = rl.getAction(state)
        action2 = rl.getAction(state2)
        learnerBoid.move(action)
        learnerBoid2.move(action2)

        # Calculate the new state
        newState = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))
        newState2 = ((learnerBoid2.x, learnerBoid2.y, learnerBoid2.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))
    
        #show the maze
        screen.blit(background_surface, (0,0))

        state = newState
        state2 = newState2
        # Draw the boids
        # Draw the leader
        boidRect = pygame.Rect(leadrect)
        boidRect.x = leaderBoid.x
        boidRect.y = leaderBoid.y
        screen.blit(bird, boidRect)

        # Draw the learner
        boidRect = pygame.Rect(birdrect)
        boidRect.x = learnerBoid.x
        boidRect.y = learnerBoid.y
        screen.blit(bird, boidRect)

        boidRect = pygame.Rect(birdrect)
        boidRect.x = learnerBoid2.x
        boidRect.y = learnerBoid2.y
        screen.blit(bird, boidRect)
        
        pygame.display.flip()
        pygame.time.delay(1)
   

# Perform |numTrials| of the following:
# On each trial, take the MDP |mdp| and an RLAlgorithm |rl| and simulates the
# RL algorithm according to the dynamics of the MDP.
# Each trial will run for at most |maxIterations|.
# Return the list of rewards that we get for each trial.
def simulate(rl, numTrials=22, maxIterations=1000, verbose=False,
             sort=False):

    def isfollowing(state):
        # Define following as being within 20-30 units
        #if not(distance(state[0], state[1]) > 20 and distance(state[0], state[1]) <= 35):
            #print distance(state[0], state[1])
        return distance(state[0], state[1]) > crashdistance - 1 and distance(state[0], state[1]) <= crashdistance + 15

    def reward(prev_state, new_state):
        # We will primarily calculate initial reward 
        # based on distance between leader and the flying bird

        # Calculate the previous distance
        old_learner_loc = prev_state[0]
        old_leader_loc = prev_state[1]
        distance_old = distance(old_learner_loc, old_leader_loc)

        # Calculate new distance 
        new_learner_loc = newState[0]
        new_leader_loc = newState[1]
        distance_new = distance(new_learner_loc, new_leader_loc)
        #distance_new = distance(new_learner_loc, old_leader_loc)

        reward = 0
        
        if distance_new < crashdistance:
            #reward = - 600*(1/distance_new)
            reward = -600
            #print reward
        elif distance_old > distance_new:
            #reward = distance_new / float(8)
            reward = 10
            # reward += (1/distance_new)
        elif distance_old < distance_new:
            #reward = - distance_new / float(2)
            reward = -5
        return reward


    totalRewards = []  # The rewards we get on each trial
    following = []
    for trial in range(numTrials):
        # We want to start doing the simulation
        # Let us start by placing down a the leader and
        # the learning follower
        #leaderBoid = LeadBoid(500, 300)
        leaderBoid = CircleBoid(500, 300)
        # Define the start state for our rl algorithm
        learnerBoid = LearningBoid(460, 300, 90)

        # Define the start state that will be passed to our learning algorithm
        state = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))

        # We have to define the start state. We should start the bird close to the
        # follow bird
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        time_steps_following = 0
        for _ in range(maxIterations):
            # Get the action predicted by the bird learning algorithm
            action = rl.getAction(state)
            # Move the learning bird
            learnerBoid.move(action)

            # Move the leading bird
            leaderBoid.move()

            newState = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))
            
            reward1 = reward(state, newState)

            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            rl.incorporateFeedback(state, action, reward1, newState)

            totalReward += totalDiscount * reward1
            if trial % 3 == 0:
                time_steps_following += 1 if isfollowing(newState) else 0

            state = newState
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        if trial % 3 == 0:
            following.append(time_steps_following)
            rl.printWeights()
        totalRewards.append(totalReward)
    return totalRewards, following



# def simulate_fixed(rl, numTrials=10, maxIterations=1000, verbose=False,
#              sort=False):
#     def reward(prev_state, new_state):
#         # We will primarily calculate initial reward 
#         # based on distance between leader and the flying bird

#         # Calculate the previous distance
#         old_learner_loc = prev_state[0]
#         old_leader_loc = prev_state[1]
#         distance_old = distance(old_learner_loc, old_leader_loc)

#         # Calculate new distance 
#         new_learner_loc = newState[0]
#         new_leader_loc = newState[1]
#         distance_new = distance(new_learner_loc, new_leader_loc)

#         reward = 0

#         # Base reward on how the distance changes
#         if distance_new < crashdistance:
#             reward = -110
#         elif distance_old > distance_new:
#             reward = 400
#         elif distance_old < distance_new:
#             reward = -150


#         if new_learner_loc[0] < 0 or new_learner_loc[0] > width:
#             reward += -100 + min(new_learner_loc[0], width - new_learner_loc[0])
#         if new_learner_loc[1] < 0 or new_learner_loc[1] > height:
#             reward += -100 + min(new_learner_loc[1], height - new_learner_loc[1])

#         return reward


#     totalRewards = []  # The rewards we get on each trial
#     for trial in range(numTrials):
#         # We want to start doing the simulation
#         # Let us start by placing down a the leader and
#         # the learning follower
#         leaderBoid = StraightLineBoid(55, height / 2.0)
#         # Define the start state for our rl algorithm
#         learnerBoid = LearningBoid(25, height / 2.0, 90)

#         # Define the start state that will be passed to our learning algorithm
#         state = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, learnerBoid.angle), leaderBoid.speed, (width, height))

#         # We have to define the start state. We should start the bird close to the
#         # follow bird
#         sequence = [state]
#         totalDiscount = 1
#         totalReward = 0
#         for _ in range(maxIterations):
#             # Get the action predicted by the bird learning algorithm
#             action = rl.getAction(state)
#             # Move the learning bird
#             learnerBoid.move(action)

#             # Move the leading bird
#             leaderBoid.move()

#             newState = ((learnerBoid.x, learnerBoid.y, learnerBoid.angle), (leaderBoid.x, leaderBoid.y, leaderBoid.angle), leaderBoid.speed, (width, height))
            
#             reward1 = reward(state, newState)

#             sequence.append(action)
#             sequence.append(reward)
#             sequence.append(newState)

#             totalReward += totalDiscount * reward1

#             state = newState

#         totalRewards.append(totalReward)
#     return totalRewards



## Run the game!
# Define the actions for the boids
# as the angles that can turn
def actions(state):
    # OLD!!
    # return [None, -45, -35, -20, -10, -5, -2, 0, 2, 5, 10, 20, 35, 45, 180]
    angles = [-45, -35, -20, -10, -5, -2, 0, 2, 5, 10, 20, 35, 45]
    velocities = [-.3, -.2, -.1, 0, .1, .2, .3]

    toReturn = []

    for angle in angles:
        for speed in velocities:
            toReturn.append((angle, speed))

    return toReturn
    #return [None, -45, 0, 45, 90, -90, 135, -135, 180]

rl = QLearnBoid(actions, 0.05, followLeaderBoidFeatureExtractorV2)
results, following = simulate(rl)
#rl.weights = {'too-close': -277.2738533630285, 'distance': -61.99941592542029, 'distance-delta': -2.703749051497212}
# Weights for follow with d = 30
#rl.weights = {'too-close': -309.3907888756954, 'distance': -93.85128986645125, 'distance-delta': -4.498854417797437}
print following
rl.printWeights()
#total_rewards = simulate_fixed(rl)
#print "***total rewards for this different simulations***"
#print total_rewards
#rl.explorationProb = 0
#test_maze(rl)
test_rl(rl)

#flock = QLearnBoid(actions, 0.05, threeBirdFlock)
#flock.weights = {"num-close": -5, "leader-delta": -9, "closest": -600, "second": -600, "centroid": -3}
#results, following = simulate_flock(flock, rl)
#flock.printWeights()
#flock.weights = {"num-close": -5, "leader-delta": -9, "closest": -600, "second": -600, "centroid": -3}
#flock.weights = {'num-close': -194.56696867753752, 'second': -46.0414842003419, 'centroid': -85.70090960847638, 'leader-delta': 47.346239400205164, 'closest': -150.9097418891571}
#flock.weights = {'num-close': 5.091556643054558, 'second': -0.023930798504836134, 'centroid': -0.6919207067486197, 'leader-delta': -2.5160067808901267, 'closest': -0.011987485524575334}
#flock.explorationProb = 0

#test_flock(flock, rl, 15)




"""
Dead Code repository

# Old reward stuff
# Base reward on how the distance changes
'''
if distance_new == 0:
    reward = -1000

elif distance_new < crashdistance:
    # OLD!!
    
    #if distance_old <= distance_new:
        #reward = 45
    #else:
        #reward = -45
    
    reward = -45
    # else:

    reward = (-500) * (1/distance_new)
'''
'''
if distance_new < crashdistance:
    reward = - 2*(1/distance_new)
elif distance_old > distance_new:
    
                # OLD!!
    
    # reward = 5
    reward = 10
    reward += 500 * (1/distance_new)
elif distance_old < distance_new:
    # OLD!!!
    # reward = -5


    reward = -10
    reward += 500 * (1/distance_new)
    
    reward = distance_new / float(8)
    # reward += (1/distance_new)
elif distance_old < distance_new:
    reward = - distance_new / float(2)
    # reward -= (1/distance_new)
'''

"""
