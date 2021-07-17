
import pygame

class Canvas:
    def __init__(self,monde,taillex,tailley):
        pygame.init()

        self.monde = monde
        self.canvas = pygame.display.set_mode((taillex,tailley))
        pygame.display.set_caption("Solveur Binaire Elementaire")

        #attributs
        self.X = 0; self.Y = 0
        self.echelle = 1
        self.taillex = taillex; self.tailley = tailley

        #gestion de la souris
        self.move = False; self.translate = False
        (self.Xmouse,self.Ymouse) = (0,0)
        (self.Xram,Yram) = (0,0)
        self.sensibilite = 1

        #couleurs
        self.fond_color = (220,220,220)

    def pixel(self,x,y):
        resx = int(self.echelle*(x-self.X)) + int(self.taillex/2)
        resy = int(-self.echelle*(y-self.Y)) + int(self.tailley/2)

        return (resx,resy)

    def coord(self,px,py):
        return ((px-int(self.taillex/2))/self.echelle+self.X,-(py-int(self.tailley/2))/self.echelle+self.Y )

    def afficher(self):

        #background

        self.canvas.fill(self.fond_color)

        #canvas

        #TODO: afficher les éléments du monde souhaité

    def action(self):
        #TODO: action à effectuer à chaque frame
        pass

    def handleEvent(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:#right button
            print(event.button)

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

        elif event.type == pygame.KEYDOWN:
            if event.key == 119: #z
                print("z")
            else:
                print(event.key)

        #TODO: Mettre les evenements que l'on veut

    def run(self):
        """ Main Loop """
        continuer = 1
        while continuer:

            self.action()
            self.afficher()
            pygame.display.flip()
            # Handle events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    continuer = 0
                    pygame.quit()

                else:
                    self.handleEvent(event)