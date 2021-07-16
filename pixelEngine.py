## Imports

from fenetre.canvas import Canvas
import pickle
import numpy as np
import pygame
import random
import time
import math


## Class Principale

class Pixel:
    def __init__(self,action):
        self.m=1
        self.action = action #fonction action(dt,grille) qui renvoie une liste d'actions à effectuer

class PixelEngine:
    def __init__(self,N,pixels):
        self.N = N #taille_grille
        self.pixels = pixels
        self.grille = np.zeros((N,N),dtype=np.int16)
        self.t = time.time()

        # update_grille
        for i in range(N):
            for j in range(N):
                self.grille[i,j]=-1

    def coord_to_grille(self,x,y):
        return N//2+int(x),N//2+int(y)

    def grille_to_coord(self,i,j):
        return i-N//2,j-N//2

    def evolve(self,to_update):
        dt = (time.time()-self.t)
        actions = []
        for i,j in to_update:
            pixel = self.grille[i,j]
            actions.append(self.pixels[pixel].action(self.grille,dt))

        self.t +=dt

    def save(self,name_file):
        file = open(name_file,'wb',pickle.HIGHEST_PROTOCOL)
        pickle.dump(self,file)
        file.close()

    def load(name_file):
        file = open(name_file,'rb')
        res = pickle.load(file)
        file.close()
        return res

##

class Fenetre(Canvas):
    def __init__(self, monde, taillex, tailley):
        Canvas.__init__(self, monde, taillex, tailley)

    def afficher(self):
        # background
        self.canvas.fill((200, 200, 200))

        #pixels
        for i in range(self.monde.N):
            for j in range(self.monde.N):
                pixel = self.monde.grille[i,j]

                if pixel == -1:
                    color = (0,0,0)
                else:
                    color = (255,255,255)
                px,py = self.pixel(i,j)
                w,h = self.echelle*1, self.echelle*1
                pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))

    def action(self):
        self.monde.evolve([])
    # time.sleep(0.1)

## main

pixelEngine = PixelEngine(100,[]) #PixelEngine.load("pixelEngine.obj")#
pixelEngine.grille[50,50]=1

fenetre = Fenetre(pixelEngine, 1200, 800)
fenetre.run()
monde.save("pixelEngine.obj")











