
'''
Version : Python 3
'''
import tkinter as tk
from tkinter import *
from winsound import *
import random
import json
import os

class Defender(object):
    def __init__(self,game): 
        self.width = 40     #gestion de la largeur du defender
        self.height = 20       #gestion de la hauteur
        self.move_delta = 20    #gestion de la vitesse de deplacement
        self.max_fired_bullets = 7 #gestion du nombre de projectiles pouvant etre tirés simultanement
        self.fired_bullets = [] #gestion de la mise en memoire des projectiles tirés
        self.point=0
        self.game=game
        self.largeur=game.width
        self.hauteur=game.height
        self.image = PhotoImage(file='Defender.png').zoom(1).subsample(2)
    def install_in(self, canvas):
        dificult=self.game.diff_var.get()
        if dificult==1000:
            self.point_en_plus=10
            self.vie=4            
        if dificult==666:
            self.point_en_plus=20
            self.vie=3
        if dificult==333:
            self.point_en_plus=50
            self.vie=2
        
        self.vie_barre=[None]*self.vie
        self.point=0
        lx = 400 + self.width/2 #Permet de centrer le personnage
        ly = 600 - self.height - 10 #permet d elever le personnage
        #self.id = canvas.create_rectangle(lx, ly, lx + self.width, ly + self.height, fill="green") # creation d un rectangle blanc qui representeras le defender
        self.id=canvas.create_image(lx,ly, image=self.image)
        for i in range(self.vie):
            
            self.aff=canvas.create_rectangle(self.largeur/100 +50*i, 50, self.largeur/100 + self.width +50*i, 50 + self.height, fill="green")
            self.vie_barre[i] = self.aff 

        
        self.bullet=Bullet(self)
        self.canvas=canvas
    def move_in(self,canvas, dx): 
        canvas.move(self.id, dx, 0) #permet de deplacer le defender en fonction de la valleur de dx
    def get_id(self):
        return self.id #retourne l identifiant du defender c'est pratique pour d'autres class
    
    def get_bullet(self):
        return self.fired_bullets #retourne la liste des projectiles tirés par le defender
    
    def fire(self,canvas):

        if len(self.fired_bullets) < self.max_fired_bullets: #si la taille de la liste est inférieur a la valleur du nombre max de projectiles que l'on peut tirer alors:
            
            self.bullet=Bullet(self) #création d'un nouvel objet bullet : (c'est un projectile)
            self.bullet.install_in(canvas) #on apelle la methode qui premetteras de desiner un projectile
            self.fired_bullets.append(self.bullet) #on stocke l'objet dans la liste 
    def destruction(self,canvas):
        self.bullet.set_destru()
        canvas.delete(self.id)
        self.game.class_score.supr()
        for i in range(self.vie):
             self.canvas.delete(self.vie_barre[i])

    def Barre_de_vie(self):
        self.vie-=1
        self.canvas.delete(self.vie_barre[self.vie])


class Explosion(object):
    def __init__(self,game):
        self.canvas=game.canvas
        self.defender=game.defender
    def install_in(self,x,y):
        
        self.musique_explo = PlaySound("Explosion.wav", SND_FILENAME | SND_ASYNC)
        self.image = PhotoImage(file='explosion.gif').zoom(1).subsample(2)
        self.explosion_id=self.canvas.create_image(x, y, image=self.image)
        #print("ca explose haaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.canvas.after(100,self.supr)
    def supr(self):
        self.canvas.delete(self.explosion_id)        
            

class Bullet(object):
    destru=False

    def __init__(self,shooter):
        self.radius = 5 #gestion de la taille du projectile
        self.color= "red" #gestion de la couleur 
        self.speed= 8 #gestion de la vitesse 
        self.animspeed=50
        
        self.y=580 #initialisation de la coordonée y de départ 
        self.stop=0 #initialisation d'une variable pour "détruire" le projectile 
        self.defender=shooter #appel de l'objet defender déja créé dans cette class
        self.shooter=self.defender.get_id() #récupération de l'id de çe dernier
        Bullet.destru=False
    def install_in(self,canvas):
        self.canvas=canvas #récupération du canvas 
        self.x=canvas.coords(self.shooter)[0] #récuperation des coordonées en x du defender plus 20 pour avoir son milieu 
        self.id_tir=canvas.create_oval(self.x-self.radius,self.y+self.radius,self.x+self.radius,self.y-self.radius,width=0,fill=self.color) #création du projectile et stockage de son id dans une variable
        
        self.move_in() #appel de la fonction de déplacement
    def get_tir(self):
        return self.id_tir 
    def set_stop(self): #cette methode est appeler plus bas dans le code
        self.stop=1 
    def set_destru(self):
        Bullet.destru=True
        


    def move_in(self):
        if Bullet.destru==True:
            self.destruction()
            return 0
        self.canvas.move(self.id_tir,0,-self.speed)
        if self.canvas.coords(self.id_tir)[1]>0 and self.stop==False: #si la coordonée en y du projectile est supérieur a 0 et que stop est a 0 (False) alors on rapelle la methode
            
            self.canvas.after(self.animspeed,self.move_in) #appel d'une methode après un temps donnée 
        else:

            if self.canvas.coords(self.id_tir)[1]<=0:
                self.defender.point =self.defender.point-10 #ici on gère le score : si le projectile est détruit et que ses coordonnées sont suppérieur au cadre alors on enlève 10 points
                self.defender.game.class_score.change_score()
                
            self.destruction()
            #print("detruit")  #test pour vérifier le mon fonctionnement 
    def destruction(self):
        self.defender.get_bullet().remove(self) #suppression de l'objet dans la liste de l'objet defender 
        self.canvas.delete(self.id_tir) #suppression du canvas 
 
        
class Bullet_alien(object):
    destru=False

    def __init__(self,alien,Fleet):
        self.radius = 5 #gestion de la taille du projectile
        self.color= "green" #gestion de la couleur 
        self.speed= 8 #gestion de la vitesse 
        self.animspeed=50
        self.alien=alien
        self.fleet=Fleet
        self.max_alien_bullet=4
        self.bunker_ici=False
        self.stop=0 #initialisation d'une variable pour "détruire" le projectile 
        Bullet_alien.destru=False
    def install_in(self,canvas):
        if self.fleet.game.activ_bunker.get()==1:
            self.bunker_ici=True
        self.canvas=canvas #récupération du canvas 
        self.x=canvas.coords(self.alien.get_alien_id())[0]+10 #récuperation des coordonées en x d'un alien plus 10 pour avoir son milieu 
        self.y=canvas.coords(self.alien.get_alien_id())[1]+10 #récuperation des coordonées en y d'un alien plus 10 pour avoir son milieu 
        self.id_tir=canvas.create_oval(self.x-self.radius,self.y+self.radius,self.x+self.radius,self.y-self.radius,width=0,fill=self.color) #création du projectile et stockage de son id dans une variable
        self.explosion=self.fleet.game.explosion
        
        self.move_in()

    def move_in(self):
        if Bullet_alien.destru==False:

           
            self.canvas.move(self.id_tir,0,+self.speed)
            
            try:

                if self.canvas.coords(self.id_tir)[1]<self.fleet.game.height-10 and self.stop==False: #si la coordonée en y du projectile est supérieur a 0 et que stop est a 0 (False) alors on rapelle la methode
                    self.impact()
                    self.canvas.after(self.animspeed,self.move_in) #appel d'une methode après un temps donnée 
                
                else:
                        
                    self.destruction()


            except:
                #print("ligne 136")
                 self.destruction()
                 return 0
                
        else:
            self.destruction()
            return 0


                
                
                
                #print("detruit")  #test pour vérifier le mon fonctionnement 
    def destruction(self):
        try:
            
            self.alien.get_bullet().remove(self) #suppression de l'objet dans la liste de l'objet defender 
        except:
            None
        
        self.canvas.delete(self.id_tir)

    def impact(self):
        if self.bunker_ici==True:
            for i in range(len(self.fleet.bunker_list)):
            
                if self.fleet.bunker_list[i].get_etat()>0:

                    if self.canvas.coords(self.id_tir)[0]>self.canvas.bbox(self.fleet.bunker_list[i].aff)[0]-10 and self.canvas.coords(self.id_tir)[3]>=self.canvas.bbox(self.fleet.bunker_list[i].aff)[1] and self.canvas.coords(self.id_tir)[2]<self.canvas.bbox(self.fleet.bunker_list[i].aff)[2]+10 and self.canvas.coords(self.id_tir)[3]<=self.canvas.bbox(self.fleet.bunker_list[i].aff)[3]:
                        print("le bunker est detruit ou la la ")
                        self.explosion.install_in(self.canvas.bbox(self.id_tir)[0],self.canvas.bbox(self.id_tir)[1])
                        self.fleet.bunker_list[i].touched()
            
                        self.destruction()
        

        if self.canvas.coords(self.id_tir)[0]>self.canvas.bbox(self.fleet.defender.get_id())[0]-10 and self.canvas.coords(self.id_tir)[3]>=self.canvas.bbox(self.fleet.defender.get_id())[1] and self.canvas.coords(self.id_tir)[2]<self.canvas.bbox(self.fleet.defender.get_id())[2]+10 and self.canvas.coords(self.id_tir)[3]<=self.canvas.bbox(self.fleet.defender.get_id())[3]:
            print("le defender est detruit ou la la ")
            self.explosion.install_in(self.canvas.bbox(self.id_tir)[0],self.canvas.bbox(self.id_tir)[1])
            self.fleet.defender.Barre_de_vie()

            
            self.destruction()
            
            
            if self.fleet.defender.vie<=0 and self.fleet.active == False:
                
                self.fleet.active=True#On arette la boucle de déplacement des aliens dans fleet
                self.canvas.after(5,self.fleet.destruction)
                Bullet_alien.destru=True
                self.canvas.after(5,self.fleet.game.perdu)#on Lance l'écran de defaite

                


        

    def set_destru(self):
        #print("on detruit les projectiles alliens")
        Bullet_alien.destru=True       


class Score_aff(object):
    def __init__(self,defender,canvas,game):
        self.game=game
        self.defender=defender
        self.canvas=canvas
    def install_in(self):
        self.label_score=self.canvas.create_text(self.game.width/2,self.game.height/30,text="Score : "+str(self.defender.point), font=("Arial", 20),fill="red", )
    def change_score(self):
        self.canvas.delete(self.label_score)
        self.label_score=self.canvas.create_text(self.game.width/2,self.game.height/30,text="Score : "+str(self.defender.point), font=("Arial", 20),fill="red", )
    def supr(self):
        self.canvas.delete(self.label_score)


class Fleet(object):
    def __init__(self,Largeur,Hauteur,game):
        self.largeur=Largeur
        self.hauteur=Hauteur
        self.aliens_lines = 4
        self.aliens_columns = 7
        self.aliens_inner_gap = 50 #distance en pixel entre chaque allien 
        self.alien_x_delta = 10  #nombre de pixel en X de parcourus a chauqe déplacement
        self.alien_y_delta = 30 # nombre de pixel en Y parcourus a chaque deplacement
        self.active=False  #variable me permettant de stoper mes boucle en cas de victoire ou de défaite 
        self.fleet_size= self.aliens_lines * self.aliens_columns
        self.aliens_fleet = [None] * self.fleet_size #ici on crée une liste vide de fleet_size element 
        self.game=game #permet d'appeler des methodes de la class Game
        
        self.max_fired_alien_bullet=20
        self.fired_bullets_alien = []
        self.Nb_bunker=3
        self.Nb_bunker_actif=self.Nb_bunker

    def install_in(self,canvas,Defender):
        self.fleet_size= self.aliens_lines * self.aliens_columns
        self.canvas=canvas
        self.defender=Defender
        self.position=0
        self.fleet_speed=50
        self.fire_Alien_speed=self.game.diff_var.get()
        j=0
        self.signal=False
        self.active=False
        if self.game.activ_bunker.get()==1:

            self.bunker_list= [None]*self.Nb_bunker
            for i in range(self.Nb_bunker):

                self.bunker_list[i] = Bunker(self.game,i)

        Py=100
        while j<self.aliens_lines:
            i=0 
            Px=100  # a chaque boucle on re initialise a position en x a l avaleur voulu 
            while i<self.aliens_columns:
                self.alien=Alien(self.defender) # appel de la class Alien
                self.alien.install_in(Px,Py,self.canvas,self) # appel de la méthode de cration d'un alien et envois des coordonnées voulu
                #print(self.alien.get_alien_id()) #test pour avoir les coordonnées de l'alien créé 
                self.aliens_fleet[self.position]=self.alien # mise de l'objet alien dans une liste 
                self.position+=1 # incrementation de la liste 
                Px+=self.aliens_inner_gap #augmentation des coordonnés en X
                i+=1
                
            j+=1
            Py+=self.aliens_inner_gap #Augementation des coordonnées en Y 
        #print("test coordonnées")  #divers test pour le debuging 
        #print(self.aliens_fleet[1].get_alien_id())
        self.aliens_fleet_bis=list(self.aliens_fleet)
        self.move_it() # une fois les aliens créé appel de la fonction de déplaement des aliens 
        self.feu()
        self.Anime_les()
    def move_it(self):
        
        

        
        if self.fleet_size>=1: #tant qu'il y a des aliens en vie alors on execute les boucles suivantes
            i=0
            if self.active==False: #si false alors ni victoire ni défaite alors on continue le deplacement des aliens
                #print(self.fleet_size) 
                
                while i < len(self.aliens_fleet):#cette boucle a pour but de déplacer les aliens sur l'axe horizontale
                   
                    if self.aliens_fleet[i].get_alive()==True: #test si les aliens sont vivant
                        '''
                        La partie de code qui suit a pour but de tester si l'utilisateur a activer les bunker 
                        si oui on vérifie si il en reste un qui n'a pas été detruit par les tir aliens
                        si oui on regarde si un des alien encore vivant et sur la même hauteur que les bunker 
                        si oui le joueur a perdu


                        '''





                        if self.game.activ_bunker.get()==1:
                            if self.Nb_bunker_actif>=1:

                                #print(self.Nb_bunker_actif)
                                if self.canvas.bbox(self.aliens_fleet[i].get_alien_id())[3] >= self.bunker_list[0].y2-20:

                                    self.active=True

                                    self.destruction()

                                    self.game.perdu()#appel de la methode qui affiche l'ecrant de defaite 
                                    return 0
                        



                        if self.canvas.coords(self.aliens_fleet[i].get_alien_id())[1] > self.canvas.bbox(self.defender.get_id())[1]-5:#test si la coordonée y1 d'un alien vivant rentre en colision avec la coordonée en y du haut du defender
                            
                            if self.active==False:#destruction des aliens
                                self.active=True

                                self.destruction()

                                self.game.perdu()#appel de la methode qui affiche l'ecrant de defaite 
                                return 0
                    self.aliens_fleet[i].move_in(self.alien_x_delta,0)#deplace tout les aliens 
                    i+=1
                i=0
                while i  <  len(self.aliens_fleet): #toute cette boucle a pour but de tester si les alien vivant touchent le bord de l'écrant et de faire l'action appropriée

                    j=0
                    '''
                    La partie de code qui suit a pour but de tester si un alien encore en vie touche le bord de l'écran si oui 
                    on inverse leur sens de déplacenment sur l'axe horizontal 
                    et on déplace tout les aliens une fois vers le bas


                    '''



                    if self.aliens_fleet[i].get_alive()==True:
                        if self.canvas.bbox(self.aliens_fleet[i].get_alien_id())[2] > self.largeur or self.canvas.bbox(self.aliens_fleet[i].get_alien_id())[0] < 0:
                            self.alien_x_delta = -self.alien_x_delta
                            #i=len(self.aliens_fleet) #petite astuce me permettant de de ne déplacer qu'une fois vers le bas
                            while j  < len(self.aliens_fleet):
                                self.aliens_fleet[j].move_in(self.alien_x_delta,self.alien_y_delta)
                                j+=1
                    i+=1
                if self.fleet_size<5: #augmentation de la vitesse si il reste moins de  aliens en vie
                    self.fleet_speed=25  

                self.canvas.after(self.fleet_speed,self.move_it) #rappel de ma fonction
        else:

            k=0
            while k  < len(self.aliens_fleet):
                self.aliens_fleet[k].destruction()
                k+=1



            if self.active==False:
                self.active=True
                if self.signal==True:
                    
                    self.game.titre()
                else:
                    self.game.Winn()#appel de la methode qui affiche l'ecrant de victoire 

    def feu(self):
            if len(self.fired_bullets_alien) < self.max_fired_alien_bullet and self.active==False: #si la taille de la liste est inférieur a la valleur du nombre max de projectiles que l'on peut tirer alors:
                j=random.choice(self.aliens_fleet_bis)
                self.bullet_alien=Bullet_alien(j,self) #création d'un nouvel objet bullet : (c'est un projectile)
                self.bullet_alien.install_in(self.canvas) #on apelle la methode qui premetteras de desiner un projectile
                j.Animation.tir()
                self.fired_bullets_alien.append(self.bullet_alien) #on stocke l'objet dans la liste 
            if self.active==False:

                self.canvas.after(self.fire_Alien_speed,self.feu)

    def Anime_les(self):
        if self.active==False:
            i=len(self.aliens_fleet_bis)
            i-=1
            alien=self.aliens_fleet_bis[random.randint(0,i)]
            if alien.anime==False:

                alien.anime_moi()
            self.canvas.after(500,self.Anime_les)
        
    def fin(self):
        self.signal=True
        try:
            
            self.bullet_alien.set_destru()
        except:
            None
        self.supr_bunker()
        self.alien.change()
    def supr_bunker(self):
        if self.game.activ_bunker.get()==1:

            for i in range(len(self.bunker_list)):
                self.bunker_list[i].suppr()
    def nb_bunker_actif(self):
        self.Nb_bunker_actif-=1

        
    def get_fleet(self):
        return self.aliens_fleet
    def destruction(self):

        k=0
        while k  < len(self.aliens_fleet):
            self.aliens_fleet[k].destruction()
            k+=1
        self.canvas.delete(self.aliens_fleet)         
        

class Alien(object):
    destru=False
    
    def __init__(self,Defender):
        self.defender=Defender
        self.alive = True
        self.anime=False
        

    def install_in(self,x,y,Canvas,Fleet):
        self.canvas=Canvas
        self.image = PhotoImage(file='alien.png').zoom(1).subsample(2)#appel de l'imege et permet de redefinir ça taille ici elle est moitié plus petite
        self.multiplicateur_bonus=1
        self.fleet=Fleet
        self.alien_id=self.canvas.create_image(x, y, image=self.image)#affichage de l'image pour des coordonnées x et  y données
        Alien.destru=False
        self.Animation=AnimAlien(self)
    def anime_moi(self):
        #print("ici")
        self.Animation.start()
        self.anime=True
    def non_anime(self):
        self.anime=False




    def touched_by(self,canvas): #dans cette methode on va  gerer les conditions de mort d'un alien et ses conséquences

        #print(self.overlapped)
        
        for i in range(len(self.defender.get_bullet())):
            
            if self.alive == True:
                
                #print(self.overlapped)
                self.liste=self.defender.get_bullet()#ici on récupère la liste des projectiles qui sont actuellement a l'écrant
                


                for j in range(len(self.overlapped)):




                    if self.overlapped[j]==self.liste[i].get_tir():# on sait que l'element 0 de la liste c'est forcément l'id de l'alien (Cf code ci-dessous) l'element en position 1 est un element qui rentre en colision avec l'alien on vérifie donc si cette element est présent dans la liste
                        #print("oui ")
                        self.defender.point+=self.defender.point_en_plus*self.multiplicateur_bonus
                        self.liste[i].set_stop() #on apelle une méthode de la class bullet
                        self.kill_alien(canvas)
                        self.fleet.game.class_score.change_score()
                        return 0
            #self.fleet.get_fleet().remove(self)
            #self.canvas.delete(self.alien_id)
            else:
                None
    def kill_alien(self,canvas):
        self.fleet.fleet_size-=1
        
        self.image1 = PhotoImage(file='explosion.gif').zoom(1).subsample(2)     #ici on change l'image     
        self.canvas.itemconfigure(self.alien_id, image=self.image1)
        
        self.alive = False 
        self.canvas.after(150,self.mort)

    def destruction(self):
        #print("je suis detruit")
        self.canvas.delete(self.alien_id)
        
    def get_bullet(self):
        return self.fleet.fired_bullets_alien

    def mort(self):

            
         self.image1 = PhotoImage(file='test.png').zoom(1).subsample(2)          
         self.canvas.itemconfigure(self.alien_id, image=self.image1)
         if Alien.destru == True:
             self.destruction()
         else:
             self.fleet.aliens_fleet_bis.remove(self)

    
             
    def get_def_id(self):
        return self.defender.get_id()
    def get_alien_id(self):
        return self.alien_id
    def get_alive(self):
        return self.alive
    def change(self):
        #print("change alien")
        Alien.destru=True
        

    def move_in(self,dx,dy):
        if Alien.destru==True:
            self.kill_alien(self.canvas)
        
        self.x=dx
        self.y=dy
        self.canvas.move(self.alien_id,self.x,self.y)
        x1,y1,x2,y2 = self.canvas.bbox(self.alien_id)
        self.overlapped = self.canvas.find_overlapping(x1, y1, x2, y2)#on reherche tout les objets qui rentrent en colision dans une zone définie ici se sont les coordonnées entière de l'alien
        if len(self.overlapped)>1:
            self.touched_by(self.canvas)

class AnimAlien(object):
    def __init__(self,alien):
        self.imageA = PhotoImage(file='alien.png').zoom(1).subsample(2)
        self.imageB = PhotoImage(file='alien1_bis.png').zoom(1).subsample(2)
        self.imageC = PhotoImage(file='alien_charge.png').zoom(1).subsample(2)
        self.imageD = PhotoImage(file='alien_tir.png').zoom(1).subsample(2)
        self.alien=alien
        self.canvas=alien.canvas
        self.alien_id=alien.alien_id
        self.etat=0
        self.etat_tir=0
    def start(self):
        
        if self.alien.get_alive()==True:
            if self.etat==0:
                self.etat=1
                #print("la")
                self.canvas.itemconfigure(self.alien_id, image=self.imageB)
                if self.etat_tir==0:

                    self.canvas.after(600,self.end)

 
    def end(self):
        if self.alien.get_alive()==True:
            self.alien.multiplicateur_bonus=1
            self.etat=0
            self.etat_tir=0
            self.alien.non_anime()
            self.canvas.itemconfigure(self.alien_id, image=self.imageA)
            

    def tir(self):
        if self.etat_tir==0:

            self.etat=1
            self.etat_tir=1
            self.alien.multiplicateur_bonus=2
            self.canvas.itemconfigure(self.alien_id, image=self.imageD)
            self.canvas.after(300,self.tirB)
    def tirB(self):
        if self.alien.get_alive()==True:
            self.canvas.itemconfigure(self.alien_id, image=self.imageC)
            self.canvas.after(300,self.end)



class Bunker(object):
    def __init__(self,game,i):
        self.game=game
        self.largeur=game.width
        self.hauteur=game.height
        self.width = 80     #gestion de la largeur du bunker
        self.height = 20       #gestion de la hauteur
        self.i=i
        self.Nb_bunker = 2
        self.espacement=300
        self.canvas=game.canvas
        self.y2=self.hauteur/1.2 + self.height
        self.install_in()
    def install_in(self):
        self.etat=3
        
        
            
        self.aff=self.canvas.create_rectangle(self.largeur/6 +self.espacement*self.i, self.hauteur/1.2, self.largeur/6 + self.width +self.espacement*self.i, self.y2, fill="green")
        
    def touched(self):
        self.etat-=1
        self.change_etat()
    def change_etat(self):
        if self.etat==2:

            self.canvas.itemconfigure(self.aff,fill="orange")
        if self.etat==1:

            self.canvas.itemconfigure(self.aff,fill="red")
        if self.etat==0:
            self.canvas.delete(self.aff)
            self.game.fleet.nb_bunker_actif()
    def suppr(self):
        self.canvas.delete(self.aff)

    def get_etat(self):
        return self.etat

   

     
class Score:
    def __init__(self, nom,points):
        self.nom=nom
        self.points=points
    def get_score(self):
        return self.points
    def __str__(self):
        return "Le Joueur du nom de : " + self.nom + " a fait : "+ str(self.points)    


class Resultat(object):
    def __init__(self):
        self.lesScores=[]
    def ajout(self,score):
        position=0
        try:

            for i in range(len(self.lesScores)):
                if int(self.lesScores[i].get_score()) >= score.get_score():
                    position = i+1

            self.lesScores.insert(position, score)
            #print("bla bla bla")
            #print(position)
        except:
            self.lesScores.insert(1,score)
        

    def __str__(self):
        chaine=str()
        for e in self.lesScores:
            chaine=chaine + "\n" + str(e)
        return chaine
    def suppr(self):
        del self.lesScores[:]

    def fromFile(cls,fich):
        f = open(fich,"r")

        tmp = json.load(f)

        liste = []

        for d in tmp:
            l=Score(d["nom"],d["scores"])

            liste.append(l)
        result=Resultat()
        result.lesScores= liste
        f.close()
        return result

    def toFile(self,fich):
        f = open(fich,"w")
        tmp = []
        for l in self.lesScores:

            d = {}
            d["nom"]= l.nom
            d["scores"]= l.points
            tmp.append(d)
        json.dump(tmp,f)
        f.close()


class Game(object):
    
    def __init__(self, frame):
        self.width=1000 #X largeur
        self.height=600 #Y hauteur 
        self.frame=frame
        self.back_ground = PhotoImage(file='Espace_invader.png')
        self.canvas=tk.Canvas(self.frame,width=self.width, height=self.height,bg="black")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.create_image(0,0,anchor=NW,image=self.back_ground)
        self.defender=Defender(self)
        self.fleet=Fleet(self.width,self.height,self)
        self.nb=0
        self.actif= False
        self.defaite=False
        self.defender_present=False
        self.diff_var = IntVar()
        self.activ_bunker = IntVar()
        self.class_score=Score_aff(self.defender,self.canvas,self)
        self.resultat=Resultat()
        self.pseudo= StringVar() #permet de récuperer le texte de Entry
        self.explosion=Explosion(self)
        self.joueur_score=self.resultat
        self.posX_Boutton=self.width/1.1
        self.posY_Boutton=self.height/2
        self.lecture=False
    def start(self):

        self.titre()
        
        self.frame.winfo_toplevel().bind("<Key>", self.keypress)
    
    def titre(self):
        try:
            self.boutton_score.destroy()
            self.canvas.delete(self.boutton_score_w)
            self.boutton_reset_score.destroy()
            self.canvas.delete(self.boutton_reset_score_w)

            self.canvas.delete(self.label_gg)
            
        except:
            None
        if self.lecture==False:
            self.lecture=True
            self.musique_explo = PlaySound("Accueil.wav", SND_FILENAME | SND_ASYNC)
        'création de multiple objet et intégration dans la fenettre'
        self.boutton_score=Button(self.canvas,text="Score",font=("Arial", 20),bg="red",fg="blue", command=self.score) #création d'un boutton
        self.boutton_score_w=self.canvas.create_window(self.width/2,self.height/1.05, window=self.boutton_score) #mise du boutton a l'intérieur de notre canvas 
        self.Label_Titre=self.canvas.create_text(self.width/2,self.height/4,text="Space Invader", font=("Arial", 30),fill="red", )
        

        self.boutton_debut=Button(self.canvas,text="Jouer",font=("Arial", 40),bg="red",fg="blue", command=self.lancement)
        self.boutton_debut_w=self.canvas.create_window(self.width/2,self.height/2, window=self.boutton_debut)
        self.label_Consigne=self.canvas.create_text(self.width/8,self.height/20,text="Entrez un pseudo", font=("Arial", 20),fill="red", )
        self.ecrire=Entry(self.canvas,font="Arial",textvariable=self.pseudo,fg="black")
        self.ecrire_w=self.canvas.create_window(self.width/8,self.height/8, window=self.ecrire)
        
        self.R1 = Radiobutton(self.canvas, text="Facile", variable=self.diff_var,bg="green", value=1000)
        self.R2 = Radiobutton(self.canvas, text="Normal", variable=self.diff_var,bg="orange", value=666) 
        self.R3 = Radiobutton(self.canvas, text="Difficile", variable=self.diff_var,bg="red", value=333)
        self.R1_w = self.canvas.create_window(self.posX_Boutton,self.posY_Boutton-50, window=self.R1)
        self.R2_w = self.canvas.create_window(self.posX_Boutton,self.posY_Boutton, window=self.R2)
        self.R3_w = self.canvas.create_window(self.posX_Boutton,self.posY_Boutton+50, window=self.R3)
        self.diff_var.set(1000)
        self.label_bunker=self.canvas.create_text(self.posX_Boutton-800,self.posY_Boutton-100,text="Présence de bunker ?", font=("Arial", 15),fill="red", )
        self.RChoix1 = Radiobutton(self.canvas, text="Oui", variable=self.activ_bunker,bg="green", value=1)
        self.RChoix2 = Radiobutton(self.canvas, text="Non", variable=self.activ_bunker,bg="red", value=0)
        self.RChoix1_w = self.canvas.create_window(self.posX_Boutton-800,self.posY_Boutton-50, window=self.RChoix1)
        self.RChoix2_w = self.canvas.create_window(self.posX_Boutton-800,self.posY_Boutton, window=self.RChoix2)
        self.activ_bunker.set(1)
            
    def lancement(self):
        if not self.pseudo.get():
            self.pseudo.set("invité")#modifie la valleur du entry
        '''Supression de tout les elements du menu'''
        self.R1.destroy()
        self.R2.destroy()
        self.R3.destroy()
        self.canvas.delete(self.R1_w)
        self.canvas.delete(self.R2_w)
        self.canvas.delete(self.R3_w)
        self.RChoix1.destroy()
        self.RChoix2.destroy()
        self.canvas.delete(self.RChoix1_w)
        self.canvas.delete(self.RChoix2_w)
        self.ecrire.destroy()
        self.canvas.delete(self.Label_Titre)
        self.canvas.delete(self.label_bunker)
        self.canvas.delete(self.boutton_debut_w)
        self.boutton_debut.destroy()
        self.lecture=False
        self.boutton_score.destroy()
        self.canvas.delete(self.boutton_score_w)
        self.boutton_quit=Button(self.canvas,text="Quitter",font=("Arial", 10),bg="red",fg="blue", command=self.quit)
        self.boutton_quit_w=self.canvas.create_window(self.width/30,self.height/30, window=self.boutton_quit)
        self.canvas.delete(self.label_Consigne)
        self.actif=True
        self.musique_explo = PlaySound("vitup.wav", SND_FILENAME | SND_ASYNC)
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas,self.defender)
        self.class_score.install_in()
        self.defender_present=True
        

    def quit(self):
        self.actif=False
        self.fleet.fin()
        self.canvas.after(50,self.quit_action)

    def score(self):
        #print("ici")
        try:
            
            self.joueur_score=self.resultat.fromFile("resultat.json")
            self.label_gg=self.canvas.create_text(self.width/2,self.height/2,text=self.joueur_score, font=("Arial", 20),fill="red", )
            #print(self.joueur_score)
        except:
            self.label_gg=self.canvas.create_text(self.width/2,self.height/2,text="Aucun score d'enregistré", font=("Arial", 20),fill="red", )
        self.R1.destroy()
        self.R2.destroy()
        self.R3.destroy()
        self.canvas.delete(self.R1_w)
        self.canvas.delete(self.R2_w)
        self.canvas.delete(self.R3_w)
        self.RChoix1.destroy()
        self.RChoix2.destroy()
        self.canvas.delete(self.RChoix1_w)
        self.canvas.delete(self.RChoix2_w)
        self.boutton_score.destroy()
        self.canvas.delete(self.boutton_debut_w)
        self.canvas.delete(self.Label_Titre)
        self.canvas.delete(self.label_bunker)
        self.boutton_debut.destroy()
        self.boutton_score=Button(self.canvas,text="Retour",font=("Arial", 20),bg="red",fg="blue", command=self.titre)
        self.boutton_score_w=self.canvas.create_window(self.width/2,self.height/1.05, window=self.boutton_score)
        self.boutton_reset_score=Button(self.canvas,text="Réinitialiser les scores",font=("Arial", 10),bg="red",fg="blue", command=self.suppr_score)
        self.boutton_reset_score_w=self.canvas.create_window(self.width/2+200,self.height/1.05, window=self.boutton_reset_score)
        self.ecrire.destroy()
        self.canvas.delete(self.label_Consigne)
        
        
    def suppr_score(self):
        try:

            os.remove("resultat.json")
            self.canvas.delete(self.label_gg)
            self.label_gg=self.canvas.create_text(self.width/2,self.height/2,text="Scores supprimés", font=("Arial", 20),fill="red", )
            self.joueur_score.suppr()

        except:
           self.canvas.delete(self.label_gg)
           self.label_gg=self.canvas.create_text(self.width/2,self.height/2,text="Il n'y a aucun score a effacer", font=("Arial", 20),fill="red", )


    def keypress(self, event):
        x = 0

    
            
        if event.keysym == 'Left': 
            if self.defender_present==True:

                x = -30
                self.defender.move_in(self.canvas, x)
        elif event.keysym == 'Right': 
            if self.defender_present==True:

                x = 30
                self.defender.move_in(self.canvas, x)
        
        if event.keysym == 'space': 
            
            if self.defender_present==True:#permet d'éviter des erreurs lorsque le defender nest pas initialisé

                self.defender.fire(self.canvas)


    def quit_action(self):
        try:
            
            self.boutton_quit.destroy()
        except:
            None
        if self.defender_present==True:
            self.defender_present=False
            self.defender.destruction(self.canvas)
        if self.defaite==True:#si on est déja sur l'écran de defaite on le rapelle afin de supprimer ses éléments et de retourner a l'écran titre 
            self.perdu()
    def start_animation(self):

        self.start()
    def Winn(self):
        self.fleet.supr_bunker()
        if self.defender_present==True:
            self.defender_present=False
            self.defender.destruction(self.canvas)
        self.win = PhotoImage(file='Victoire.gif').zoom(2)
        self.carrey=self.canvas.create_image(self.width/2, self.height/2, image=self.win)
        self.label_gg=self.canvas.create_text(self.width/2,self.height/2,text="Victoire", font=("Arial", 40),fill="red", )
        self.label_score=self.canvas.create_text(self.width/2.5,self.height/4,text="Le score de "+str(self.pseudo.get())+" est de :"+str(self.defender.point)+" points", font=("Arial", 25),fill="green", )
        #print(self.defender.point)
        self.musique_game_over = PlaySound("Bravo.wav", SND_FILENAME | SND_ASYNC)
        try:
            
            self.joueur_score=self.resultat.fromFile("resultat.json")
            #print("les calculs ne sont pas bon kevin")
        except:
            None
        self.joueur_score.ajout(Score(self.pseudo.get(),self.defender.point))
        self.joueur_score.toFile("resultat.json")
        
        self.Winn_play()
        
    def Winn_play(self):
        if self.nb==12:
            self.nb=0
        if self.actif== True:

            
            img_nb = "gif -index " + str(self.nb) #recupere le numéro d'une image du gif de l'explosion
            self.nb+=1
            self.win = PhotoImage(file = 'Victoire.gif', format = img_nb) #recupere l'image de l'explosion
            self.canvas.itemconfigure(self.carrey, image=self.win)
            self.canvas.after(50,self.Winn_play)
        else:
            self.canvas.delete(self.label_score)
            self.canvas.delete(self.win)
            self.canvas.delete(self.carrey)
            self.canvas.delete(self.label_gg)
            self.titre()
            
    def perdu(self):
        
        if self.actif== True:
            self.fleet.supr_bunker()
            if self.defender_present==True:
                self.defender_present=False
                self.defender.destruction(self.canvas)
            self.musique_game_over = PlaySound("gameover.wav", SND_FILENAME | SND_ASYNC)
            #print("on passe par ici")
            self.defaite= True
            self.loose = PhotoImage(file='Tnul.png').zoom(1).subsample(2)
            self.nul=self.canvas.create_image(200, 200, image=self.loose)
            self.label_perdu=self.canvas.create_text(self.width/2,self.height/2,text="Perdu !", font=("Arial", 40),fill="red", )
            self.label_retour=self.canvas.create_text(self.width/2,self.height/4,text="Essaye encore", font=("Arial", 40),fill="red", )
            
            
        else:
            #print("on passe par la")
            self.defaite= False
            self.canvas.delete(self.label_perdu)
            self.canvas.delete(self.label_retour)
            self.canvas.delete(self.loose)
            self.canvas.delete(self.nul)

            self.titre()       

                      
class SpaceInvaders(object): 
    ''' Main Game class '''

    def __init__(self): 
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        width=800
        height=600
        self.frame=tk.Frame(self.root,width=width, height=height,bg="green")
        self.frame.pack()
        self.game = Game(self.frame)
        
    def play(self): 
        self.game.start_animation()
        self.root.mainloop()        
                        
jeu=SpaceInvaders()
jeu.play()