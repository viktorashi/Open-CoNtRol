import re

def crn2tellurium( filename ):

    ## filename = 'crn_a_b_c.txt'
    f = open(filename, 'rt')
    a = f.readlines()
    #print(a)

    b = list( map(lambda x:x.strip(), a) )  # scapa de un <enter> la sfarsit
    #print(b)



    # ---- inlocuirea sagetilor -----
    r = []
    for x in b:
        loc = x.find('<-->')
        if  loc > -1:    # reactie bidirectionala
            r.append( x.replace('<-->', '->') )  # reactia directa
            r.append( x[loc+4:len(x)].strip() + ' -> ' + x[0:loc].strip() )  # reactia inversa
        else:
            loco = x.find('<--')
            if loco > -1:
                r.append( x[loco+4:len(x)].strip() + ' -> ' + x[0:loco].strip() )  # reactia inversa
            else:
                r.append( x.replace('-->', '->') )  # reactia este simpla, doar de la stanga la dreapta
    #print( r )

    s = list( map(lambda x:x.replace(" ", ""), r) )



    kcont = 0   # cate reactii sunt
    krates = []   # lista cu vitezele de reactie
    for x in s:   # gaseste vitezele de reactie
        kcont = kcont + 1  # de la 1 la cate reactii sunt
        krate = ''   # rata de reactie
        krate = krate + 'k' + str(kcont)

        le = x.split('->')[0]
        ats = le.split('+')
        if ats == ['0']:  # zero barat in stanga
            pass
        else:
            for ato in ats:
                coef = re.findall(r'^[0-9]*', ato)[0]   # este sir vid '' daca nu gaseste
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]

                if coef == '':
                    cnt = 1
                else:
                    cnt = int(coef)

                for i in range(cnt):
                    krate = krate + '*' + spec   # adauga *A*A*A de cata ori era, ex.A3
        krates.append( krate )
    ## end -- for x in s


    specs = []
    for x in s:   # gaseste speciile
        ats = x.replace('->', '+').split('+')

        for ato in ats:
            if ato == '0':  # zero barat in stanga
                pass
            else:
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                specs.append( spec )  # in place
    ## end -- for x in s
    specs = list(set(specs))
    specs.sort()  # alfabetic, in place

    #print( krates )
    #print( specs )



    # pune spatii intre coeficienti si specii
    reacts = []   # lista cu reactiile
    for x in s:

        le = x.split('->')[0]  # reactantii
        ri = x.split('->')[1]  # produsii
        atsle = le.split('+')  # 2A3
        atsri = ri.split('+')

        react = ''

        lle = []
        if atsle == ['0']:  # zero barat in stanga
            pass
        else:
            for ato in atsle:
                coef = re.findall(r'^[0-9]*', ato)[0]   # este sir vid '' daca nu gaseste
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                lle.append( coef + ' ' + spec )

        react = react + ' + '.join( lle )
        react = react + ' -> '

        lri = []
        if atsri == ['0']:  # zero barat in stanga
            pass
        else:
            for ato in atsri:
                coef = re.findall(r'^[0-9]*', ato)[0]   # este sir vid '' daca nu gaseste
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                lri.append( coef + ' ' + spec )

        react = react + ' + '.join( lri )

        reacts.append( react )
    ## end --- for x in x

    reacts = list( map(lambda x:x.replace("  ", " "), reacts) )    # elimina spatiile duble
    reacts = list( map(lambda x:x.strip(), reacts) )   # elimina spatiile de la inceput si sfarsit

    #for x in reacts:
    #    print( x )


    ## --- creaza stringul de Tellurium

    tel = ''
    ii = -1
    for x in reacts:
        ii = ii + 1
        tel = tel + x + '; ' + krates[ii] + '\n'


    tel = tel + '\n'


    valk = 1   # valoarea pentru constantele de reactie
    for k in range(kcont):
        tel = tel + 'k' + str(k+1) + ' = ' + str( valk ) + ';\n'


    tel = tel + '\n'


    valinit = 1  # valoarea pentru conditiile initiale
    for x in specs:
        tel = tel + x + ' = ' + str( valinit ) + ';\n'


    tel = tel + '\n'

    return tel


## --- end crn2tellurium() ----------------------------------------------------


if __name__ == "__main__":
    print("This module is not to be run form the __main__ scope")
