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
    def __init__(self,color,action):
        self.color = color
        self.action = action #fonction action((i,j),grille,new_grille,dt) qui modifie la grille

class PixelEngine:
    def __init__(self,N,pixels):
        self.N = N #taille_grille
        self.pixels = pixels
        self.grille = np.zeros((N,N),dtype=np.int16)
        self.new_grille = np.zeros((N,N),dtype=np.int16)
        self.t = time.time()

        # update_grille
        for i in range(N):
            for j in range(N):
                self.grille[i,j]=-1
                self.new_grille[i,j]=-1

    def coord_to_grille(self,x,y):
        return N//2+int(x),N//2+int(y)

    def grille_to_coord(self,i,j):
        return i-N//2,j-N//2

    def evolve(self,to_update):
        dt = (time.time()-self.t)
        for i,j in to_update:
            pixel_id = self.grille[i,j]
            if pixel_id>=0:
                self.pixels[pixel_id].action((i,j),self.grille,self.new_grille,dt)

        self.grille = np.copy(self.new_grille)

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
                pixel_id = self.monde.grille[i,j]

                if pixel_id == -1:
                    color = (0,0,0)
                else:
                    color = self.monde.pixels[pixel_id].color
                px,py = self.pixel(i,j)
                w,h = self.echelle*1, self.echelle*1
                pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))

    def action(self):
        to_update = [ (i,j) for i in range(self.monde.N) for j in range(self.monde.N) ]
        self.monde.evolve(to_update)

## main


def action_sable(coord,grille,new_grille,dt):
    i,j = coord
    if j>0 and i>0 and i<grille.shape[0]-1:
        if grille[i,j-1]==-1:
            new_grille[i,j]=-1
            new_grille[i,j-1]=0
        elif grille[i-1,j-1] == -1:
            new_grille[i,j]=-1
            new_grille[i-1,j-1]=0
        elif grille[i+1,j-1] == -1:
            new_grille[i,j]=-1
            new_grille[i+1,j-1]=0

    new_grille[grille.shape[0]//2,grille.shape[1]//2]=0

sable = Pixel((180,180,0),action_sable)

pixels = [sable]
N = 100
pixelEngine = PixelEngine(N,pixels) #PixelEngine.load("pixelEngine.obj")#
pixelEngine.grille[10,10]=0

fenetre = Fenetre(pixelEngine, 1200, 800)
fenetre.run()
pixelEngine.save("pixelEngine.obj")











