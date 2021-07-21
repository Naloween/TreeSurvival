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
    def __init__(self,color):
        self.color = color

    def update(self, coord, grille):
        changements = []
        return changements

class GroupePixel:
    def __init__(self,pixels_coord):
        self.pixels_coord = pixels_coord

    def update(self,coord,grille):
        changements = []
        return changements

class PixelEngine:
    def __init__(self,N,tps):
        self.N = N #taille_grille
        self.grille_pixels = np.zeros((N,N),dtype=object)
        self.grille_groupes = np.zeros((N, N), dtype=object)
        self.t = time.time() #time of the previous tic
        self.tps = tps #tic par seconde

        self.to_update = []
        self.grille_to_update = np.zeros((N,N), dtype=bool) #enegistre les pixels déjà dans le to_update
        self.grille_changed = np.zeros((N,N),dtype=bool) #enregistre les pixels qui ont déjà étés changés au cours du tic

        self.maxTimer = 500
        self.start_index = 0
        self.changements = [ [] for k in range(self.maxTimer) ]

        #init grille
        for i in range(self.N):
            for j in range(self.N):
                self.grille_pixels[i,j] = None
                self.grille_groupes[i, j] = None

    def coord_to_grille(self,x,y):
        if x<0:
            i = self.N//2+int(x)-1
        else:
            i = self.N//2+int(x)
        if y>0:
            j = self.N // 2 + int(y)+1
        else:
            j =self.N//2+int(y)
        return i,j

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
                pixel = self.grille_pixels[i,j]
                if pixel == None:
                    changes = []
                elif self.grille_groupes[i,j] == None:
                    changes = pixel.update((i,j),self.grille_pixels)
                else:
                    changes = self.grille_groupes[i,j].update((i,j),self.grille_pixels)

                # évite les conflits
                apply_changes = True
                for change in changes:
                    if self.grille_changed[change[0],change[1]] == False:
                        self.grille_changed[change[0],change[1]] = True
                        reset_grille_changed.append((change[0],change[1]))
                    else:
                        apply_changes = False
                        break

                #enregistre les changements à appliquer
                if apply_changes:
                    for change in changes:
                        index = (change[3]+self.start_index)%self.maxTimer
                        self.changements[index].append(change)
                    self.grille_to_update[i,j] = False
                else :
                    new_to_update.append((i,j))
            self.to_update = new_to_update

            #rest pixels changed
            for i,j in reset_grille_changed:
                self.grille_changed[i, j] = False

            #update grille
            for k in range(len(self.changements[self.start_index])) :
                (i, j, value, tic) = self.changements[self.start_index].pop()
                changements.append((i, j, value))
                if i>0 and i<self.N-1 and j>0 and j <self.N-1:
                    self.grille_pixels[i, j] = value

                for ex in [-1,0,1]:
                    for ey in [-1,0,1]:
                        self.add_pixel_to_update(i+ex,j+ey)

            self.start_index = (self.start_index + 1) % self.maxTimer

        return changements

    def add_pixel_to_update(self,i,j):
        if i>0 and i<self.N-1 and j>0 and j <self.N-1 and not(self.grille_to_update[i,j]) and self.grille_pixels[i,j] != None:
            self.to_update.append((i,j))
            self.grille_to_update[i,j]=True

    def add_changement(self,i,j,value,tic):
        if i>0 and i<self.N-1 and j>0 and j <self.N-1:
            index = (self.start_index+tic)%self.maxTimer
            self.changements[index].append((i,j,value,tic))

    def save(self,name_file):
        file = open(name_file,'wb',pickle.HIGHEST_PROTOCOL)
        pickle.dump(self,file)
        file.close()

    def load(name_file):
        file = open(name_file,'rb')
        res = pickle.load(file)
        file.close()
        return res

## Graphismes

class Fenetre(Canvas):
    def __init__(self, monde, taillex, tailley):
        Canvas.__init__(self, monde, taillex, tailley)
        self.create_pixel = False
        self.pixel_id = 0; self.pixel = Sable()
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
                if self.monde.grille_pixels[i,j] != None:
                    pixel = self.monde.grille_pixels[i,j]
                    color = pixel.color

                    x,y = self.monde.grille_to_coord(i,j)
                    px,py = self.coord_to_pixel(x,y)
                    w,h = self.echelle*1, self.echelle*1
                    pygame.draw.rect(self.canvas,color,(px,py,w+1,h+1))
                else:
                    x,y = self.monde.grille_to_coord(i,j)
                    px,py = self.coord_to_pixel(x,y)
                    w,h = self.echelle*1, self.echelle*1
                    pygame.draw.rect(self.canvas,(0,0,0),(px,py,w+1,h+1))
        else:
            # background
            self.canvas.fill((200, 200, 200))

            # pixel zone
            px, py = self.coord_to_pixel(-self.monde.N // 2, self.monde.N // 2)
            w, h = self.echelle * self.monde.N, self.echelle * self.monde.N
            pygame.draw.rect(self.canvas, (0, 0, 0), (px, py, w, h))

            for i in range(self.monde.N):
                for j in range(self.monde.N):
                    if self.monde.grille_pixels[i,j] != None:
                        pixel = self.monde.grille_pixels[i,j]
                        color = pixel.color

                        x,y = self.monde.grille_to_coord(i,j)
                        px,py = self.coord_to_pixel(x,y)
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

            #display pixel to draw
            pygame.draw.rect(self.canvas,self.pixel.color,(0,self.tailley-100,100,100))

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
                maxTypePixel = 2
                if self.pixel_id >= maxTypePixel:
                    self.pixel_id = 0

                if self.pixel_id == 0:
                    self.pixel = Sable()
                elif self.pixel_id == 1:
                    self.pixel = Eau()
                
            elif event.key == 13: #entree
                self.play = not(self.play)
            else:
                print(event.key)

        if self.create_pixel :
            (px, py) = pygame.mouse.get_pos()

            x, y = self.pixel_to_coord(px, py)
            i, j = self.monde.coord_to_grille(x, y)

            if self.pixel_id == 0:
                self.pixel = Sable()
            elif self.pixel_id == 1:
                self.pixel = Eau()

            self.monde.add_changement(i,j,self.pixel,0)

        #TODO: Mettre les evenements que l'on veut

## main
class Sable(Pixel):
    def __init__(self):
        color = (200,150,0)
        Pixel.__init__(self,color)

    def update(self,coord,grille):
        changements = []
        i,j = coord
        if j>1:
            if grille[i,j-1]==None or type(grille[i,j-1]) == Eau:
                changements.append((i,j,grille[i,j-1],0))
                changements.append((i,j-1,self,0))
            elif grille[i-1,j-1] == None or type(grille[i-1,j-1]) == Eau:
                changements.append((i,j,grille[i-1,j-1],0))
                changements.append((i-1,j-1,self,0))
            elif grille[i+1,j-1] == None or type(grille[i+1,j-1]) == Eau:
                changements.append((i,j,grille[i+1,j-1],0))
                changements.append((i+1,j-1,self,0))
        return changements

class Eau(Pixel):
    def __init__(self):
        color = (0,0,180)
        Pixel.__init__(self,color)

    def update(self,coord,grille):
        changements = []
        i,j = coord
        e = 2*random.randint(0,1)-1
        if j>1:
            if grille[i,j-1]== None:
                changements.append((i,j,None,0))
                changements.append((i,j-1,self,0))
            elif grille[i-1,j-1] == None:
                changements.append((i,j,None,0))
                changements.append((i-1,j-1,self,0))
            elif grille[i+1,j-1] == None:
                changements.append((i,j,None,0))
                changements.append((i+1,j-1,self,0))
            elif grille[i+e,j] == None:
                changements.append((i,j,None,0))
                changements.append((i+e,j,self,0))
            elif grille[i-e,j] == None:
                changements.append((i,j,None,0))
                changements.append((i-e,j,self,0))
        return changements

class Gaz(Pixel):
    def __init__(self):
        color = (0,180,0)
        Pixel.__init__(color)

    def update(self,coord,grille):
        changements = []
        i,j = coord
        e = 2*random.randint(0,1)-1
        if j>1:
            if grille[i,j+1]==-1:
                changements.append((i,j,-1,0))
                changements.append((i,j+1,3,0))
            elif grille[i-1,j+1] == -1:
                changements.append((i,j,-1,0))
                changements.append((i-1,j+1,3,0))
            elif grille[i+1,j+1] == -1:
                changements.append((i,j,-1,0))
                changements.append((i+1,j+1,3,0))
            elif grille[i,j+1]==1:
                changements.append((i,j,1,0))
                changements.append((i,j+1,3,0))
            elif grille[i-1,j+1] == 1:
                changements.append((i,j,1,0))
                changements.append((i-1,j+1,3,0))
            elif grille[i+1,j+1] == 1:
                changements.append((i,j,1,0))
                changements.append((i+1,j+1,3,0))
            elif grille[i+e,j] == -1:
                changements.append((i,j,-1,0))
                changements.append((i+e,j,3,0))
            elif grille[i-e,j] == -1:
                changements.append((i,j,-1,0))
                changements.append((i-e,j,3,0))
        return changements

class Pierre(Pixel):
    def __init__(self):
        color = (150,150,150)
        Pixel.__init__(color)

    def update(self,coord,grille):
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
                    changements.append((x,y,-1,0))
                if grille[x,y-1] == -1:
                    changements.append((x,y-1,2,0))

        return changements

class Bois(Pixel):
    def __init__(self):
        color = (125, 83, 41)
        Pixel.__init__(color)

    def update(self,coord,grille):
        changements = []
        i,j = coord
        if j>1:
            if grille[i,j-1]==-1:
                changements.append((i,j,-1,0))
                changements.append((i,j-1,4,0))
            iswater = False
            for e1 in [-1,0,1]:
                for e2 in [-1,0,1]:
                    if grille[i+e1,j+e2] == 1:
                        iswater = True
                        changements.append((i+e1,j+e2,-1,100))

            if iswater:
                j_add = j+1
                while grille[i,j_add] == 4:
                    j_add += 1
                if grille[i,j_add] == -1:
                    changements.append((i,j_add,4,100))

        return changements

class Electricity(Pixel):
    def __init__(self):
        color = (255, 255, 0)
        Pixel.__init__(color)

    def update(self,coord,grille):
        changements = []
        e1 = random.randint(-1,1); e2 = random.randint(-1,1)
        i,j = coord

        changements.append((i,j,-1,0))
        if grille[i+e1,j+e2] == -1:
            changements.append((i+e1, j+e2, 5,0))

        return changements

class Wire(Pixel):
    def __init__(self):
        color = (207, 70, 70)
        Pixel.__init__(color)

    def update(self,coord, grille):
        changements = []
        i, j = coord

        exit = False
        for e1 in [-1,0,1]:
            for e2 in [-1,0,1]:
                if grille[i+e1,j+e2] == 5:
                    changements.append((i+e1,j+e2,-1,0))
                    changements.append((i, j, 7,0))
                    exit = True
                    break
                elif grille[i+e1,j+e2] == 7:
                    changements.append((i, j, 7,0))
                    exit = True
                    break
            if exit:
                break

        return changements

if __name__ == "__main__":

    N = 200; tps = 60
    pixelEngine = PixelEngine(N,tps) #PixelEngine.load("pixelEngine.obj")#

    fenetre = Fenetre(pixelEngine, 1200, 800)
    fenetre.run()
    pixelEngine.save("pixelEngine.obj")



