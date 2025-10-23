import sys
import time
import subprocess
from threading import Thread
#On essaie de récupérer le module PyMinitel. Comme il n'est pas sur pip, on vient le récupérer directment sur Git
try :
    from minitel.Minitel import Minitel
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/Fafafy/PyMinitel.git"])
    from minitel.Minitel import Minitel

from minitel.constantes import (SS2, SEP, ESC, CSI, PRO1, PRO2, PRO3, MIXTE1,
                                              MIXTE2, TELINFO, ENQROM, SOH, EOT, TYPE_MINITELS, STATUS_FONCTIONNEMENT,
                                              LONGUEUR_PRO2, STATUS_TERMINAL, PROG, START, STOP, LONGUEUR_PRO3,
                                              RCPT_CLAVIER, ETEN, C0, MINUSCULES, RS, US, VT, LF, BS, TAB, CON, COF,
                                             AIGUILLAGE_ON, AIGUILLAGE_OFF, RCPT_ECRAN, EMET_MODEM, FF, CAN, BEL, CR,
                                              SO, SI, B300, B1200, B4800, B9600, REP, COULEURS_MINITEL,
                                              CAPACITES_BASIQUES, CONSTRUCTEURS, ROULEAU)

def test_deplacement(minitel):
    #On s'assure que l'utilisateur peut saisir du texte
    minitel.echo(False)
    minitel.envoyer('o')
    minitel.position(-1, 0, True)
    #Tant que l'utilisateur ne passe pas à la ligne, on écoute ce qu'il écrit
    entree = None
    while entree != [13]: #Touche entree
        entree = minitel.recevoir_sequence(bloque=True).valeurs
        print(entree)
        match entree:
            # Haut
            case [27, 91, 65]:
                minitel.envoyer(' ')
                minitel.position(-1, -1, True)
                minitel.envoyer('o')
                minitel.position(-1, 0, True)
            # Bas
            case [27, 91, 66]:
                minitel.envoyer(' ')
                minitel.position(-1, 1, True)
                minitel.envoyer('o')
                minitel.position(-1, 0, True)
            # Droite
            case [27, 91, 67]:
                minitel.envoyer(' o')
                minitel.position(-1, 0, True)
            # Gauche
            case [27, 91, 68]:
                minitel.position(-1, 0, True)
                minitel.envoyer('o ')
                minitel.position(-2, 0, True)

def dessiner_route(minitel,position_joueur) :
    while 1:

        ancienne_postition = position_joueur
        if position_joueur[1]>1:
            position_joueur[1]-=1
        minitel.envoyer([US, 0x40 + 24, 0x40 + 1]+['$', REP, 0x40 + 39]+[US, 0x40 + position_joueur[1], 0x40 + position_joueur[0], 'o'])
        time.sleep(1)


def test_route(minitel):
    position_joueur = [1,1]
    t1 = Thread(target=dessiner_route, args=(minitel,position_joueur,))
    t1.start()
    print("coucou")
    minitel.echo(False)
    minitel.position(1, 1)
    minitel.envoyer('o')
    minitel.position(-1, 0, True)
    entree = None
    while entree != [13]: #Touche entree
        try :
            entree = minitel.recevoir_sequence(False).valeurs
            print(entree)
            #On se remet à la position pour supprimer l'ancien caractère
            ancienne_postition = position_joueur[:]
            match entree:

                # Haut
                case [27, 91, 65] | [122]:
                    if position_joueur[1]>1:
                        position_joueur[1]-=1
                # Bas
                case [27, 91, 66] | [115]:
                    if position_joueur[1]<24:
                        position_joueur[1]+=1
                # Droite
                case [27, 91, 67] | [100]:
                    if position_joueur[0]<40:
                        position_joueur[0]+=1
                # Gauche
                case [27, 91, 68] | [113]:
                    if position_joueur[0]>1:
                        position_joueur[0]-=1

            #minitel.position(position_joueur[0], position_joueur[1])
            print(position_joueur)
            print(ancienne_postition)
            #minitel.envoyer('o')
            minitel.envoyer([US, 0x40 + ancienne_postition[1], 0x40 + ancienne_postition[0], ' ']+[US, 0x40 + position_joueur[1], 0x40 + position_joueur[0], 'o'])
        except :
            pass
    minitel.efface('tout')


if __name__ == '__main__':
    sandbox = Minitel(peripherique='COM4')
    sandbox.definir_vitesse(4800)
    sandbox.efface('tout')
    sandbox.curseur(False)
    sandbox.configurer_clavier(etendu=True, minuscule=True)
    sandbox.definir_mode(rouleau=True)
    test_route(sandbox)


