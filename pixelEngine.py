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
    def __init__(self,N,pixels,tps):
        self.N = N #taille_grille
        self.pixels = pixels
        self.grille = np.zeros((N,N),dtype=np.int16)
        self.t = time.time() #time of the previous tic
        self.tps = tps #tic par seconde

        self.to_update = []
        self.grille_to_update = np.zeros((N,N), dtype=bool)
        self.grille_changed = np.zeros((N,N),dtype=bool)

        self.changements = []

        # update_grille
        for i in range(N):
            for j in range(N):
                self.grille[i,j]=-1

    def coord_to_grille(self,x,y):
        return self.N//2+int(x)-1,self.N//2+int(y)

    def grille_to_coord(self,i,j):
        return i-self.N//2,j-self.N//2

    def evolve(self):
        changements = []
        dt = (time.time()-self.t)
        if dt>1/self.tps:
            self.t = time.time()

            #calculs changements
            new_to_update = []

            reset_grille_changed = []

            for i,j in self.to_update:
                pixel_id = self.grille[i,j]
                if pixel_id == -1:
                    changes = []
                else:
                    changes = self.pixels[pixel_id].action((i,j),self.grille)

                apply_changes = True
                for change in changes:
                    if self.grille_changed[change[0],change[1]] == False:
                        self.grille_changed[change[0],change[1]] = True
                        reset_grille_changed.append((change[0],change[1]))
                    else:
                        apply_changes = False
                        break

                if apply_changes:
                    self.changements+= changes
                    self.grille_to_update[i,j] = False
                else :
                    new_to_update.append((i,j))
            self.to_update = new_to_update

            #rest pixels changed
            for i,j in reset_grille_changed:
                self.grille_changed[i, j] = False

            #update grille
            for k in range(len(self.changements)) :
                (i, j, value) = self.changements.pop()
                changements.append((i, j, value))
                if i>0 and i<self.N-1 and j>0 and j <self.N-1:
                    self.grille[i, j] = value

                for ex in [-1,0,1]:
                    for ey in [-1,0,1]:
                        self.add_pixel_to_update(i+ex,j+ey)

        return changements

    def add_pixel_to_update(self,i,j):
        if i>0 and i<self.N-1 and j>0 and j <self.N-1 and not(self.grille_to_update[i,j]) and self.grille[i,j] != -1:
            self.to_update.append((i,j))
            self.grille_to_update[i,j]=True

    def add_changement(self,i,j,value):
        if i>0 and i<self.N-1 and j>0 and j <self.N-1:
            self.changements.append((i,j,value))

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
        self.graphic_changes = True
        self.changements = []
        self.t = time.time()
        self.play = True

    def afficher(self):
        #pixels
        # for i in range(self.monde.N):
        #     for j in range(self.monde.N):
        #         if self.monde.grille[i,j] != -1:
        #             pixel_id = self.monde.grille[i,j]
        #             color = self.monde.pixels[pixel_id].color
        #
        #             x,y = self.monde.grille_to_coord(i,j)
        #             px,py = self.pixel(x,y)
        #             w,h = self.echelle*1, self.echelle*1
        #             pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))

        if not(self.graphic_changes):
            for (i,j,value) in self.changements:
                if self.monde.grille[i,j] != -1:
                    pixel_id = self.monde.grille[i,j]
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
        else:
            # background
            self.canvas.fill((200, 200, 200))

            # pixel zone
            px, py = self.pixel(-self.monde.N // 2, self.monde.N // 2)
            w, h = self.echelle * self.monde.N, self.echelle * self.monde.N
            pygame.draw.rect(self.canvas, (0, 0, 0), (px, py, w, h))

            for i in range(self.monde.N):
                for j in range(self.monde.N):
                    if self.monde.grille[i,j] != -1:
                        pixel_id = self.monde.grille[i,j]
                        color = self.monde.pixels[pixel_id].color

                        x,y = self.monde.grille_to_coord(i,j)
                        px,py = self.pixel(x,y)
                        w,h = self.echelle*1, self.echelle*1
                        pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))
            self.graphic_changes = False

        if self.t<time.time():
            fps = int(1/(time.time()-self.t))
            self.t = time.time()

            #display fps
            display_width = 100; display_height = 20
            pygame.draw.rect(self.canvas,(255,255,255),(0,0,display_width,display_height))
            text = str(fps)+" fps"
            largeText = pygame.font.Font('freesansbold.ttf', 20)
            textSurface = largeText.render(text, True, (0,0,0))
            rect = textSurface.get_rect()
            rect.center = ((display_width / 2), (display_height / 2))
            self.canvas.blit(textSurface, rect)

        # update zone
        # for (i,j) in self.monde.to_update:
        #     x, y = self.monde.grille_to_coord(i, j)
        #     px, py = self.pixel(x, y)
        #     w, h = self.echelle * 1, self.echelle * 1
        #     pygame.draw.rect(self.canvas, (0, 255, 0), (px, py, w + 1, h + 1))

    def action(self):
        if self.play:
            self.changements = self.monde.evolve()
        else:
            self.changements = []

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
            self.graphic_changes = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5: #mousewheel down
            self.echelle /= 1.5
            self.graphic_changes = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(event.button)

        elif  self.translate and event.type == pygame.MOUSEMOTION:
            (x,y)=pygame.mouse.get_pos()
            self.X = self.Xram+self.sensibilite*(self.Xmouse-x)/self.echelle
            self.Y = self.Yram+self.sensibilite*(y-self.Ymouse)/self.echelle

            self.graphic_changes = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:#left button
            self.translate = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3: #right button
            self.create_pixel = False

        elif event.type == pygame.KEYDOWN:
            if event.key == 32: #espace
                self.pixel_id += 1
                if self.pixel_id >= len(self.monde.pixels):
                    self.pixel_id = 0
            elif event.key == 13: #entree
                self.play = not(self.play)
            else:
                print(event.key)

        if self.create_pixel :
            (px, py) = pygame.mouse.get_pos()

            x, y = self.coord(px, py)
            i, j = self.monde.coord_to_grille(x, y)
            self.monde.add_changement(i,j,self.pixel_id)

        #TODO: Mettre les evenements que l'on veut


## main

def action_sable(coord,grille):
    changements = []
    i,j = coord
    if j>1:
        if grille[i,j-1]==-1:
            changements.append((i,j,-1))
            changements.append((i,j-1,0))
        elif grille[i,j-1] == 1:
            changements.append((i,j,1))
            changements.append((i,j-1,0))
        elif grille[i-1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i-1,j-1,0))
        elif grille[i-1,j-1] == 1:
            changements.append((i,j,1))
            changements.append((i-1,j-1,0))
        elif grille[i+1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i+1,j-1,0))
        elif grille[i+1,j-1] == 1:
            changements.append((i,j,1))
            changements.append((i+1,j-1,0))
    return changements

def action_eau(coord,grille):
    changements = []
    i,j = coord
    e = 2*random.randint(0,1)-1
    if j>1:
        if grille[i,j-1]==-1:
            changements.append((i,j,-1))
            changements.append((i,j-1,1))
        elif grille[i-1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i-1,j-1,1))
        elif grille[i+1,j-1] == -1:
            changements.append((i,j,-1))
            changements.append((i+1,j-1,1))
        elif grille[i+e,j] == -1:
            changements.append((i,j,-1))
            changements.append((i+e,j,1))
        elif grille[i-e,j] == -1:
            changements.append((i,j,-1))
            changements.append((i-e,j,1))
    return changements

def action_gaz(coord,grille):
    changements = []
    i,j = coord
    e = 2*random.randint(0,1)-1
    if j>1:
        if grille[i,j+1]==-1:
            changements.append((i,j,-1))
            changements.append((i,j+1,3))
        elif grille[i-1,j+1] == -1:
            changements.append((i,j,-1))
            changements.append((i-1,j+1,3))
        elif grille[i+1,j+1] == -1:
            changements.append((i,j,-1))
            changements.append((i+1,j+1,3))
        elif grille[i,j+1]==1:
            changements.append((i,j,1))
            changements.append((i,j+1,3))
        elif grille[i-1,j+1] == 1:
            changements.append((i,j,1))
            changements.append((i-1,j+1,3))
        elif grille[i+1,j+1] == 1:
            changements.append((i,j,1))
            changements.append((i+1,j+1,3))
        elif grille[i+e,j] == -1:
            changements.append((i,j,-1))
            changements.append((i+e,j,3))
        elif grille[i-e,j] == -1:
            changements.append((i,j,-1))
            changements.append((i-e,j,3))
    return changements

def action_pierre(coord,grille):
    seuil = 50
    changements = []
    i,j = coord

    #calcul pixels attachés
    pierre = [(i,j)]
    check = [ (i-1,j-1),(i-1,j),(i-1,j+1),(i,j-1),(i,j+1),(i+1,j-1),(i+1,j),(i+1,j+1) ]

    for x,y in check:
        if grille[x,y] == 2 and not (x,y) in pierre:
            pierre.append((x,y))
            check += [ (x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1) ]
        if len(pierre)>seuil:
            return []

    # centre de gravité
    G = [0,0]
    for x,y in pierre:
        G[0]+=x; G[1]+=y
    G[0] /= len(pierre); G[1] /= len(pierre)

    #can fall
    fall = True
    for x,y in pierre:
        if grille[x,y-1] != -1 and grille[x,y-1] != 2:
            fall = False

    if fall:
        for x,y in pierre:
            if grille[x,y+1] != 2 and grille[x,y-1] == 2:
                changements.append((x,y,-1))
            if grille[x,y-1] == -1:
                changements.append((x,y-1,2))

    return changements

def action_bois(coord,grille):
    changements = []
    i,j = coord
    if j>1:
        if grille[i,j-1]==-1:
            changements.append((i,j,-1))
            changements.append((i,j-1,4))
        elif grille[i,j-1] == 1 and grille[i,j+1] == -1:
            changements.append((i,j+1,4))
            changements.append((i,j-1,-1))
        elif grille[i-1,j] == 1 and grille[i,j+1] == -1:
            changements.append((i,j+1,4))
            changements.append((i-1,j,-1))
        elif grille[i+1,j] == 1 and grille[i,j+1] == -1:
            changements.append((i,j+1,4))
            changements.append((i+1,j,-1))
        elif grille[i-1,j-1] == 1 and grille[i,j+1] == -1:
            changements.append((i,j+1,4))
            changements.append((i-1,j-1,-1))
        elif grille[i+1,j-1] == 1 and grille[i,j+1] == -1:
            changements.append((i,j+1,4))
            changements.append((i+1,j-1,-1))
    return changements


sable = Pixel((200,150,0),action_sable)
eau = Pixel((0,0,180),action_eau)
pierre = Pixel((150,150,150),action_pierre)
gaz = Pixel((0,180,0),action_gaz)
bois = Pixel((100,50,80),action_bois)

pixels = [sable,eau,pierre,gaz,bois]
N = 100; tps = 60
pixelEngine = PixelEngine(N,pixels,tps) #PixelEngine.load("pixelEngine.obj")#

fenetre = Fenetre(pixelEngine, 1200, 800)
fenetre.run()
pixelEngine.save("pixelEngine.obj")











