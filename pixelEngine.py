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
        self.grille = np.zeros((N,N),dtype=object)
        self.t = time.time()

        self.to_update = []
        self.grille_to_update = np.zeros((N,N), dtype=bool)

        # update_grille
        for i in range(N):
            for j in range(N):
                self.grille[i,j]=[]

    def coord_to_grille(self,x,y):
        return self.N//2+int(x),self.N//2+int(y)

    def grille_to_coord(self,i,j):
        return i-self.N//2,j-self.N//2

    def evolve(self):
        dt = (time.time()-self.t)

        #calculs changements
        changements = []
        for i,j in self.to_update:
            for k in range(len(self.grille[i,j])):
                pixel_id = self.grille[i,j][k]
                changements += self.pixels[pixel_id].action((i,j),k,self.grille,dt)
            self.grille_to_update[i,j] = False
        self.to_update = []

        #update grille
        for (i,j,value,add) in changements :
            if i>0 and i<self.N-1 and j>0 and j <self.N-1:
                if add:
                    self.grille[i, j].append(value)
                else:
                    if value in self.grille[i,j]:
                        self.grille[i, j].remove(value)

            for ex in [-1,0,1]:
                for ey in [-1,0,1]:
                    if not(self.grille_to_update[i+ex,j+ey]):
                        self.to_update.append((i+ex, j+ey))
                        self.grille_to_update[i+ex,j+ey] = True
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
        self.create_pixel = False
        self.pixel_id = 0

    def afficher(self):
        # background
        self.canvas.fill((200, 200, 200))

        #pixels
        for i in range(self.monde.N):
            for j in range(self.monde.N):
                if self.monde.grille[i,j] != []:
                    pixel_id = self.monde.grille[i,j][0]
                    color = self.monde.pixels[pixel_id].color

                    x,y = self.monde.grille_to_coord(i,j)
                    px,py = self.pixel(x,y)
                    w,h = self.echelle*1, self.echelle*1
                    pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))
                else:
                    x,y = self.monde.grille_to_coord(i,j)
                    px,py = self.pixel(x,y)
                    w,h = self.echelle*1, self.echelle*1
                    pygame.draw.rect(self.canvas,(0,0,0),(px,py,w+1,h+1))
        # update zone
        # for (i,j) in self.monde.to_update:
        #     x, y = self.monde.grille_to_coord(i, j)
        #     px, py = self.pixel(x, y)
        #     w, h = self.echelle * 1, self.echelle * 1
        #     pygame.draw.rect(self.canvas, (0, 255, 0), (px, py, w + 1, h + 1))

    def action(self):
        self.monde.evolve()

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
            if i > 0 and i < self.monde.N-1 and j > 0 and j < self.monde.N-1:
                self.monde.grille[i, j].append(self.pixel_id)
                self.monde.to_update.append((i,j))

        #TODO: Mettre les evenements que l'on veut


## main


def action_sable(coord,k,grille,dt):
    changements = []
    i,j = coord
    if j>1:
        if grille[i,j-1]==[] or grille[i,j-1]==len(grille[i,j-1])*[1]:
            changements.append((i,j,0,False))
            changements.append((i,j-1,0,True))
        elif grille[i-1,j-1] == []:
            changements.append((i,j,0,False))
            changements.append((i-1,j-1,0,True))
        elif grille[i+1,j-1] == []:
            changements.append((i,j,0,False))
            changements.append((i+1,j-1,0,True))
    return changements

def action_eau(coord,k,grille,dt):
    changements = []
    i,j = coord
    e = 2*random.randint(0,1)-1
    nb_pixels = len(grille[i,j])

    if k == 0 and grille[i,j] == len(grille[i,j])*[1]:
        if grille[i, j - 1] == []:
            changements.append((i, j, 1, False))
            changements.append((i, j - 1, 1, True))
        elif grille[i - 1, j - 1] == []:
            changements.append((i, j, 1, False))
            changements.append((i - 1, j - 1, 1, True))
        elif grille[i + 1, j - 1] == []:
            changements.append((i, j, 1, False))
            changements.append((i + 1, j - 1, 1, True))
        # elif grille[i+e,j] == []:
        #     changements.append((i,j,1,False))
        #     changements.append((i+e,j,1,True))
        # elif grille[i-e,j] == []:
        #     changements.append((i,j,1,False))
        #     changements.append((i-e,j,1,True))
    else :
        changements.append((i, j, 1, False))
        changements.append((i, j + 1, 1, True))
    return changements

def action_pierre(coord,k,grille,dt):
    return []

sable = Pixel((200,150,0),action_sable)
eau = Pixel((0,0,180),action_eau)
pierre = Pixel((150,150,150),action_pierre)

pixels = [sable,eau,pierre]
N = 100
pixelEngine = PixelEngine(N,pixels) #PixelEngine.load("pixelEngine.obj")#

fenetre = Fenetre(pixelEngine, 1200, 800)
fenetre.run()
pixelEngine.save("pixelEngine.obj")
print(pixelEngine.grille)











