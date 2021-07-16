## Imports

from fenetre.canvas import Canvas
import pickle
import numpy as np
import pygame
import random
import time
import math


## Class

class Monde:
    def __init__(self,N):
        self.N = N
        self.pixels = np.zeros((N,4))
        self.grille = np.zeros((200,200),dtype=np.int16)
        self.t = time.time()

        for k in range(N):
            self.pixels[k,0] = random.randint(0,10)
            self.pixels[k,1] = random.randint(0,10)

        # update_grille
        for i in range(200):
            for j in range(200):
                self.grille[i,j]=-1
        for k in range(N):
            self.grille[int(self.pixels[k,0])+100,int(self.pixels[k,1])+100] = k

    def evolve(self):
        ymin = 0
        dt = (time.time()-self.t)
        for k in range(self.N):
            x,y = int(self.pixels[k,0])+100,int(self.pixels[k,1])+100
            Fx = 0; Fy = 0
            g= 1; m=1
            #gravite
            Fy -= g

            #colision
            k_col = 1
            for voisin in self.voisins(x,y):
                d = math.sqrt( (voisin[0]-self.pixels[k,0])**2 + (voisin[1]-self.pixels[k,1])**2)
                ux = (voisin[0]-self.pixels[k,0])/d; uy = (voisin[1]-self.pixels[k,1])/d
                Fx += ux*k_col*(d-1); Fy += uy*k_col*(d-1)

            #frottements
            f=0.1
            Fx -= f*self.pixels[k,2]
            Fy -= f*self.pixels[k,3]

            # vitesse
            self.pixels[k,2] += Fx*dt/m
            self.pixels[k,3] += Fy*dt/m

            #deplacement
            self.pixels[k,0] += self.pixels[k,2]*dt
            self.pixels[k,1] += self.pixels[k,3]*dt

            #sol
            if self.pixels[k,1]<ymin:
                self.pixels[k,1]=ymin
                self.pixels[k,3] = -self.pixels[k,3]

            #grille
            x2,y2 = int(self.pixels[k,0])+100,int(self.pixels[k,1])+100
            self.grille[x,y]=-1
            self.grille[x2,y2]=k

        self.t +=dt

    def voisins(self,x,y):
        res = []
        if self.grille[x-1,y] != -1:
            res.append(self.pixels[self.grille[x-1,y]])
        if self.grille[x+1,y] != -1:
            res.append(self.pixels[self.grille[x+1,y]])
        if self.grille[x,y+1] != -1:
            res.append(self.pixels[self.grille[x,y+1]])
        if self.grille[x,y-1] != -1:
            res.append(self.pixels[self.grille[x,y-1]])

        return res

    def save(self,name_file):
        file = open(name_file,'wb',pickle.HIGHEST_PROTOCOL)
        pickle.dump(self,file)
        file.close()

    def load(name_file):
        file = open(name_file,'rb')
        res = pickle.load(file)
        file.close()
        return res

class Fenetre(Canvas):
    def __init__(self, monde, taillex, tailley):
        Canvas.__init__(self, monde, taillex, tailley)
        self.fps = 0

    def afficher(self):
        # background
        self.canvas.fill((200, 200, 200))

        #pixels
        color = (0,0,0)
        for pixel in self.monde.pixels:
            px,py = self.pixel(pixel[0],pixel[1])#self.pixel(int(pixel[0]),int(pixel[1]))
            w,h = self.echelle*1, self.echelle*1
            pygame.draw.rect(self.canvas,color,(px,py,w,h))

    def action(self):
        self.monde.evolve()
    # time.sleep(0.1)

## main

monde = Monde(10) #Monde.load("treeSurvival.obj")#

fenetre = Fenetre(monde, 1200, 800)
fenetre.run()
monde.save("treeSurvival.obj")











