## Imports

from canvas import Canvas
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
        self.t = time.time()

        self.to_update = []

        # update_grille
        for i in range(N):
            for j in range(N):
                self.grille[i,j]=-1

    def coord_to_grille(self,x,y):
        return self.N//2+int(x),self.N//2+int(y)

    def grille_to_coord(self,i,j):
        return i-self.N//2,j-self.N//2

    def evolve(self,to_update):
        dt = (time.time()-self.t)

        #calculs changements
        changements = []
        for i,j in to_update:
            pixel_id = self.grille[i,j]
            if pixel_id>=0:
                changements += self.pixels[pixel_id].action((i,j),self.grille,dt)

        #update grille
        for (i,j,value) in changements :
            self.grille[i,j] = value

        self.t +=dt

    def set_pixel(self,i,j,value):
        self.grille[i,j]=value
        self.to_update.append((i,j))

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
        self.create_pixel = False
        self.pixel_id = 0

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
                x,y = self.monde.grille_to_coord(i,j)
                px,py = self.pixel(x,y)
                w,h = self.echelle*1, self.echelle*1
                pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))

    def action(self):
        to_update = [ (i,j) for i in range(self.monde.N) for j in range(self.monde.N) ]
        self.monde.evolve(to_update)

    def handleEvent(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:#right button
            self.create_pixel = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:#left button
            (x,y)= pygame.mouse.get_pos()
            self.Xmouse = x
            self.Ymouse = y

            self.Xram = self.X
            self.Yram = self.Y
            self.translate = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4: #mousewheel up
            self.echelle *= 1.5

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5: #mousewheel down
            self.echelle /= 1.5

        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(event.button)

        elif  self.translate and event.type == pygame.MOUSEMOTION:
            (x,y)=pygame.mouse.get_pos()
            self.X = self.Xram+self.sensibilite*(self.Xmouse-x)/self.echelle
            self.Y = self.Yram+self.sensibilite*(y-self.Ymouse)/self.echelle

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:#left button
            self.translate = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3: #right button
            self.create_pixel = False

        elif event.type == pygame.KEYDOWN:
            if event.key == 32: #espace
                self.pixel_id += 1
                if self.pixel_id >= len(self.monde.pixels):
                    self.pixel_id = 0
            else:
                print(event.key)

        elif self.create_pixel :
            (px, py) = pygame.mouse.get_pos()

            x, y = self.coord(px, py)
            i, j = self.monde.coord_to_grille(x, y)
            self.monde.grille[i, j] = self.pixel_id

        #TODO: Mettre les evenements que l'on veut


## main


def action_sable(coord,grille,dt):
    changements = []
    i,j = coord
    if j>0 and i>0 and i<grille.shape[0]-1:
        if grille[i,j-1]==-1:
            changements.append((i,j,-1))
            changements.append((i,j-1,0))
        elif grille[i-1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i-1,j-1,0))
        elif grille[i+1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i+1,j-1,0))
    return changements

def action_eau(coord,grille,dt):
    changements = []
    i,j = coord
    if j>0 and i>0 and i<grille.shape[0]-1:
        if grille[i,j-1]==-1:
            changements.append((i,j,-1))
            changements.append((i,j-1,1))
        elif grille[i-1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i-1,j-1,1))
        elif grille[i+1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i+1,j-1,1))
        elif grille[i-1,j] == -1:
            changements.append((i,j,-1))
            changements.append((i-1,j,1))
        elif grille[i+1,j] == -1:
            changements.append((i,j,-1))
            changements.append((i+1,j,1))
    return changements

sable = Pixel((200,150,0),action_sable)
eau = Pixel((0,0,180),action_eau)

pixels = [sable,eau]
N = 100
pixelEngine = PixelEngine(N,pixels) #PixelEngine.load("pixelEngine.obj")#

fenetre = Fenetre(pixelEngine, 1200, 800)
fenetre.run()
pixelEngine.save("pixelEngine.obj")











