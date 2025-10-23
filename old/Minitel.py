from time import sleep
from unittest import case

import serial, serial.tools.list_ports
import random

long = 39
haut = 24

#Commandes de contrôle utilisateur :
x_buzzer = b'\x07'                       #Lance un buzzer dans le terminal
x_masquer_curseur = b'\x14'              # masquer curseur (curseur déjà invisible pour ma part)
x_afficher_curseur = b'\x11'             # afficher le curseur
x_mode_semi_graphique = b'\x0E'                   #Change la saisie de texte pour transformer les carractères en "pixels"
x_mode_clavier_etendu = b'\x1B\x3B\x69\x59\x41'
x_mode_texte = b'\x0F'                   #Remet la saisie de texte habituelle
x_mode_mixte = b'\x1B\x3A\x32\x7D'


#Nettoyage :
x_escape = b'\x1B'                       # effacer écran (sauf la ligne max)
x_vider_ecran = b'\x0C'                # effacer écran (sauf la ligne max)
x_vider_rangee_actuelle = b'\x18\x18'     #Effacer tout ce qu'il y a après le curseur dans la même ligne

#Contrôle de la position du curseur
x_curseur_get_position = b'\x1B\x61'         # Le Minitel revera \x1F suivi d'un caractère héxadécimal pour X puis pour Y
x_curseur_rangee_max = b'\x1F\x40\x41'            # Met le curseur une ligne au dessus du point d'origine normal
x_curseur_rangee_min = b'\x0B'                    # Met le curseur à la dernière ligne
x_curseur_home = b'\x1E'                         # Met le curseur au point d'origine normal (pas ligne max)
x_curseur_gauche  = b'\x08'             # Déplace le curseur une caractére à gauche
x_curseur_droite  = b'\x09'             # Déplace le curseur une caractére à droite
x_curseur_haut  = b'\x0B'              # Déplace le curseur une ligne au dessus
x_curseur_bas = b'\x0A'            # Déplace le curseur une ligne en dessous
x_curseur_debut_rangee = b'\x0D'                  #Met le curseur au début de la ligne actuelle

#Contrôle du style d'écriture
#Type :
x_texte_clavier_etendu = b'\x16'            #Le prochain caractère proviendra du clavier étendu
#Taille :
x_texte_taille_normale = b'\x1B\x4C'
x_texte_taille_double = b'\x1B\x4F'
x_texte_taille_double_hauteur = b'\x1B\x4D'
x_texte_taille_double_largeur = b'\x1B\x4E'
#Clignotant
x_texte_clignotant = b'\x1B\x48'
x_texte_fixe = b'\x1B\x49'

#Fond de texte
x_texte_negatif = b'\x1B\x5D'
x_texte_positif = b'\x1B\x5C'

#Accent
x_texte_accent = x_ta = b'\x19\x42' #Le prochain caractére saisi sera un accent


x_o = b'\x7f' #Carré blanc
x_sequence_desactivation_acquittement = b'\x1B\x3A\x64\x53' # En temps normal le minitel peut envoyer un code pour valider le bon fonctionnement d'une séquence. Ici on demande de ne plus le faire.
x_sequence_desactivation_echo = b'\x1B\x3B\x60\x58\x52'   # Le Minitel ne contrôle plus son propre écran, mais on récupère toujours les touches appuyées
x_sequence_activation_echo = b'\x1B\x3B\x61\x58\x52'
x_sequence_teletex = b'\x1B\x5B\x3F\x7B'
x_sequence_minuscule = b'\x1B\x3A\x69\x45'
x_sequence_majuscule = b'\x1B\x3A\x6A\x45'
x_sequence_300bauds = b'\x1B\x3A\x6B\x52'
x_sequence_1200bauds = b'\x1B\x3A\x6B\x64'
x_sequence_4800bauds = b'\x1B\x3A\x6B\x76'

class Minitel(serial.Serial):
    def __init__(self, baud_rate_start=1200, baud_rate_goal=4800, parity=serial.PARITY_EVEN, byte_size=7, force_COM=False):
        #Si un port de COM est déjà saisi, on essaie de s'y connecter directement
        if force_COM:
            try:
                super().__init__(force_COM, baud_rate_start, parity=parity, bytesize=byte_size, rtscts=1)
                print("Port " + force_COM + " connecté (choisi de force)")
            except serial.SerialException as e:
                print("Port " + force_COM + " non compatible (choisi de force)")
        else :
            #Sans port séléctionné à l'avance, on liste tous les ports disponible et on se connecte au premier qui fonctionne
            liste_ports = serial.tools.list_ports.comports()
            for port in liste_ports:
                try:
                    super().__init__(port.name, baud_rate_start, parity=parity, bytesize=byte_size, rtscts=1)
                    print("Port " + port.name + " connecté")
                except serial.SerialException as e:
                    print("Port " + port.name + " non compatible")

        #Après avoir établi la connexion avec le Minitel, on cherche à changer la vitesse de transfert pour l'otpimiser
        #Par défaut le minitel est réglé sur 1200 bauds, mais on peut lui demander de passer à un autre puis relancer un connexion adaptée
        if baud_rate_goal == 4800 and baud_rate_start != 4800:
            self.write(x_sequence_4800bauds)
        elif baud_rate_goal == 1200 and baud_rate_start != 1200:
            self.write(x_sequence_1200bauds)
        elif baud_rate_goal == 300 and baud_rate_start != 300:
            self.write(x_sequence_300bauds)

        self.close(avec_instruction=False)
        self.baudrate = baud_rate_goal
        self.open()


    #On overload la méthode de close de Serial pour ajouter les commandes à envoyer avant la fermeture de la connexion
    #A savoir que la connexion est automatiquement fermée à la fin de la communication, par défaut avec les instructions
    def close(self, avec_instruction=True):
        if avec_instruction:
            #Après la fin de connexion, on remet le Minitel à sa vitesse standard de 1200 bauds
            self.write(x_sequence_1200bauds)
        super().close()

    def test_neige(self, taille=haut, rand=3):
        for i in range (taille):
            random_string = b''
            while len(random_string) < long+1:
                random_string += b' '*random.randint(1,rand)+b'o'
            random_string = random_string[:long+1]
            self.write(b'\r' + random_string)


    def test_boing(self, speed=0.05):
        self.mode_expo()
        self.write(x_curseur_debut_rangee+b' ')
        #Vers le bas
        for i in range(haut-1):
            self.write(x_curseur_gauche+b' '+x_curseur_bas+x_curseur_gauche+b'o')
            sleep(speed)
        # Vers la droite
        for i in range(long):
            self.write(x_curseur_gauche + b' ' + b'o')
            sleep(speed)
        #Vers le haut
        for i in range(haut-1):
            self.write(x_curseur_gauche + b' ' + x_curseur_haut + x_curseur_gauche + b'o')
            sleep(speed)
        # Vers la gauche
        for i in range(long):
            self.write(x_curseur_gauche + x_curseur_gauche)
            self.write(x_vider_rangee_actuelle)
            self.write(b'o')
            sleep(speed)
        self.mode_saisie()


    def desactiver_diffusion_acquitement(self):
        self.write(x_sequence_desactivation_acquittement)

    def mode_clavier_etendu(self):
        self.write(x_mode_clavier_etendu)

    def vider_ecran(self):
        self.write(x_vider_ecran)

    def mode_expo(self):
        self.write(x_masquer_curseur+x_sequence_desactivation_echo)

    def mode_saisie(self):
        self.write(x_afficher_curseur+x_sequence_activation_echo)

    def mode_teletex(self):
        self.write(x_sequence_teletex)

    def mode_minuscule(self):
        self.write(x_sequence_minuscule)

    def deplacement_vertical_curseur(self, rangee=1):
        if rangee >= 0:
            self.write(b'\x1B\x5B'+rangee+b'\x41')
        else:
            rangee = -rangee
            self.write(b'\x1B\x5B'+rangee+b'\x42')

    def deplacement_horizontal_curseur(self, colonne=1):
        if colonne >= 0:
            self.write(b'\x1B\x5B'+colonne+b'\x43')
        else:
            rangee = -colonne
            self.write(b'\x1B\x5B'+rangee+b'\x44')

    def adressage_curseur(self, rangee=0, colonne=0):
        rangee = bytes(str(rangee), encoding='ascii')
        colonne = bytes(str(colonne), encoding='ascii')
        self.write(b'\x1B\x5B'+rangee+b'\x3B'+colonne+b'\x48')
        print(b'\x1B\x5B'+rangee+b'\x3B'+colonne+b'\x48')

    def test_deplacement(self):
        #On s'assure que l'utilisateur puisse saisir du texte
        self.mode_expo()
        #self.write(b'o'+x_curseur_gauche)
        #Tant que l'utilisateur ne passe pas à la ligne, on écoute ce qu'il écrit
        entree = None
        while entree !=b'\r':
            entree = self.read()
            print(str(entree))
            match entree:
                case b'\x1B':
                    #Si c'est un bouton de séquence, on récupère les caractères suivant pour la récupérer
                    sequence = self.read()
                    match sequence:
                        case b'\x5B':
                            #C'est une séquence de mouvement de curseur, on récupère la direction en question
                            direction = self.read()
                            match direction:
                                #Haut
                                case b'\x41':
                                    self.write(b' '+x_curseur_gauche)
                                    self.write(x_curseur_haut)
                                    self.write(b'o'+x_curseur_gauche)
                                #Bas
                                case b'\x42':
                                    self.write(b' '+x_curseur_gauche)
                                    self.write(x_curseur_bas)
                                    self.write(b'o'+x_curseur_gauche)
                                #Droite
                                case b'\x43':
                                    self.write(b' '+x_curseur_gauche)
                                    self.write(x_curseur_droite)
                                    self.write(b'o'+x_curseur_gauche)
                                #Gauche
                                case b'\x44':
                                    self.write(b' '+x_curseur_gauche)
                                    self.write(x_curseur_gauche)
                                    self.write(b'o'+x_curseur_gauche)

if __name__ == '__main__':
    howitzer = Minitel(force_COM='COM4')
    howitzer.adressage_curseur(5,5)
    #howitzer.desactiver_diffusion_acquitement()
    #howitzer.mode_teletex()
    #howitzer.mode_minuscule()
    #howitzer.vider_ecran()
    #howitzer.mode_clavier_etendu()
    #howitzer.test_deplacement()