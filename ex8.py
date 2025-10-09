def parcours_en_profondeur(g, deb):
    a_explorer = [deb]
    deja_visites = []
    while a_explorer:
        n = a_explorer.pop()
        if n not in deja_visites:
            print(n)
            deja_visites.append(n)
            for voisin in g[n]:
                if voisin not in deja_visites:
                    a_explorer.append(voisin)

def parcours_en_largeur(g, deb):
    a_explorer = [deb]
    deja_visites = []
    while a_explorer:
        n = a_explorer.pop(0)
        if n not in deja_visites:
            print(n)
            deja_visites.append(n)
            for voisin in g[n]:
                if voisin not in deja_visites:
                    a_explorer.append(voisin)
