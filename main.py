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
        #self.grille = np.zeros((200,200),dtype=np.int16)
        self.t = time.time()

        for k in range(N):
            self.pixels[k,0] = random.random()
            self.pixels[k,1] = random.random()

        # # update_grille
        # for i in range(200):
        #     for j in range(200):
        #         self.grille[i,j]=-1
        # for k in range(N):
        #     self.grille[int(self.pixels[k,0])+100,int(self.pixels[k,1])+100] = k

    def evolve(self):
        ymin = -50
        dt = (time.time()-self.t)
        for k in range(self.N):
            x,y = int(self.pixels[k,0])+100,int(self.pixels[k,1])+100
            Fx = 0; Fy = 0
            g= 1; m=1
            #gravite
            Fy -= g

            #colision
            k_col = 1; f_liaison = 0.8
            d0 = 1
            for l in range(self.pixels.shape[0]):
                if l != k:
                    d = math.sqrt( (self.pixels[l,0]-self.pixels[k,0])**2 + (self.pixels[l,1]-self.pixels[k,1])**2)
                    ux = (self.pixels[l,0]-self.pixels[k,0])/d; uy = (self.pixels[l,1]-self.pixels[k,1])/d
                    v = (self.pixels[k,2]-self.pixels[l,2])*ux+(self.pixels[k,3]-self.pixels[l,3])*uy
                    Fx += ux*(k_col*(d-d0)-f_liaison*v); Fy += uy*(k_col*(d-d0)-f_liaison*v)

            #frottements
            f_global=0.1
            Fx -= f_global*self.pixels[k,2]
            Fy -= f_global*self.pixels[k,3]

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

            # #grille
            # x2,y2 = int(self.pixels[k,0])+100,int(self.pixels[k,1])+100
            # self.grille[x,y]=-1
            # self.grille[x2,y2]=k

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

monde = Monde(15) #Monde.load("treeSurvival.obj")#

fenetre = Fenetre(monde, 1200, 800)
fenetre.run()
monde.save("treeSurvival.obj")











