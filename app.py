#import Flask
from random import randint


#import subprocess
#import StringIO
#from crn2tellurium_module import *
#create an instance of Flask
# import subprocess
# import StringIO
# from crn2tellurium_module import *
# create an instance of Flask
import io
import json
import os
import re
import subprocess
from random import randint
import tellurium as te
from flask import *

app = Flask(__name__, template_folder='templates')


#nu-s folosite astea dar ok
class DataStore():
    specii = None


data = DataStore()


def random():
    session['number'] = randint(0, 2)
    return None


@app.get('/')
def home():
    return render_template("home.html")


def saveReactiiFile(theRequest):
    ecuatiiCount = int(theRequest.form.get('ecuatiiCount'))
    index = 1

    theFile = open("templates/metode_lucru/crn.txt", "w")

    while index <= ecuatiiCount:
        ecLeft = theRequest.form.get('ec_' + str(index) + '_left')
        ecDir = theRequest.form.get('ec_' + str(index) + '_dir')
        ecRight = theRequest.form.get('ec_' + str(index) + '_right')

        ecDirString = ""
        if ecDir == 'left':
            ecDirString = '<--'
        elif ecDir == 'both':
            ecDirString = '<-->'
        elif ecDir == 'right':
            ecDirString = '-->'

        ecuatieFinala = ecLeft + " " + ecDirString + " " + ecRight

#asa ii da overwrite la templates/metode_lucru/crn.txt
        theFile.write(ecuatieFinala)
        theFile.write("\n")

        index += 1

    theFile.close()


@app.post("/save_reactii")
def saveReactii():
    saveReactiiFile(request)
    return redirect(f"/input_user")


@app.get('/input_user')
def input_user():
    files = sorted(os.listdir('templates/metode_lucru/'))  # Am modificat aici !!! am adaugat: sorted(os.listdir('')) !!! -----------------------------------------
    temp = []
    for file in files:
        temp.append({'name': file})

    specii1 = session.get("specii")
    #specii inseamna gen speciile presupun??? idk simcer
    print('specurile din session de la get input user sunt')
    print(specii1)

    return render_template("input_user.html", data=temp, specii1=specii1)


@app.post('/input_user')
def input_user_post():
    global select, durata, amplitudine, titlu, x_titlu, y_titlu, specii, valInitArray, constArray
    durata = request.form['durata']
    session['durata'] = durata
    # processed_text = durata.upper()

    amplitudine = request.form['amplitudine']
    session['amplitudine'] = amplitudine
    # processed_text1 = amplitudine.upper()

    titlu = request.form['titlu']
    session['titlu'] = titlu
    # processed_text2 = titlu.upper()

    x_titlu = request.form['x_titlu']
    session['x_titlu'] = x_titlu
    # processed_text3 = x_titlu.upper()

    y_titlu = request.form['y_titlu']
    session['y_titlu'] = y_titlu
    # processed_text4 = y_titlu.upper()

    #lista cu coeficientii pt fiecare specie
    valInitArray = []
    valInitIndex = 0

    while True:
        try:
            requestValInit = request.form['valinit' + str(valInitIndex)]
            valInitArray.append(str(requestValInit))
            valInitIndex += 1
        except:
            break

    constArray = []
    constIndex = 0

    while True:
        try:
            requestConstInit = request.form['valk' + str(constIndex)]
            constArray.append(str(requestConstInit))
            constIndex += 1
        except:
            break

    select = request.form.get('comp_select')
    session['select'] = select
    specii = session.get("specii")

    print(session.get('durata'))
    print(session.get('amplitudine'))
    print(session.get('titlu'))
    print(session.get('x_titlu'))
    print(session.get('y_titlu'))
    print(constArray)
    print(valInitArray)
    print(session.get('select'))
    print(session.get('specii'))

    # return(str(select), text) # just to see what select is
    return redirect(f"/graph2")


@app.route('/graph2')
def plot_svg():
    [fig, listaToShow, listaToShowMatrice] = create_figure()
    output = io.BytesIO()
    #    FigureCanvas(fig).print_png(output)
    #    return Response(output.getvalue(), mimetype='image/png')
    #listaToShow = ['A','B','C']
    return render_template("graph.html", listaEcuatii=listaToShow, listaMatrice=listaToShowMatrice,
                           pageName="Chemical Reaction Network (CRN) - 2D")


@app.get('/reactmeta')
def getReactionMetaHandler():
    reactionFileName = request.args.get('filename')
    f = open("templates/metode_lucru/" + reactionFileName, 'rt')
    fileLines = f.readlines()

    reactii_individuale : [str] = getReactii4Tellurium(fileLines)

    specii, reacts = getReactionMeta(session, reactii_individuale)
    data = {
             'speciiList' : specii,
             'reactsCount' : str(len(reacts)),
             }
    return json.dumps(data)


def getReactionMeta(session, reactii_individuale : [str] ):
    global specii  #Aici o sa fie colectia de specii
    specii = []

    for reactie in reactii_individuale:  # gaseste speciile
        ats = reactie.replace('->', '+').split('+') #transforma si 4A + 5B -> C in 4A + 5B + C si le da split la +

        print('ats:')
        print(ats)

        #scoate coeficientul din fata de la fiecare specie
        for ato in ats:
            if ato != '0':  # sa nu fie zero barat
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                specii.append(spec)  # in place

    ## end -- for x in s

    #TODO: problema aici ca daca am in reactii diferite aceeasi specie nu pot sa le pun coeficientii diferite
    specii = list(set(specii)) #scoate duplicatele
    specii.sort()  # alfabetic
    session['specii'] = specii
    #print( krates )
    print("Cate specii sunt:")
    print(specii)

    #transforma din reactiile individuale de forma 2A + 3B -> 10C in 2  A  3  B -> 10  C
    reacts = []  # lista cu reactiile
    for reactie in reactii_individuale:

        [le , ri] = reactie.split('->') #reactantii si produsii
        # le = reactie.split('->')[0]  # reactantii
        # ri = reactie.split('->')[1]  # produsii

        atsle = le.split('+')  #reactantii cu tot cu coeficientii
        atsri = ri.split('+') #produsii cu tot cu coeficientii


        lle = []
        if atsle != ['0']:  #sa nu fie zero barat in stanga
            for ato in atsle:
                coef = re.findall(r'^[0-9]*', ato)[0]  # este sir vid '' daca nu gaseste
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                lle.append(coef + ' ' + spec)

        react = '' + ' + '.join(lle) + ' -> '

        lri = []
        if atsri != ['0']:  # zero barat in stanga
            for ato in atsri:
                coef = re.findall(r'^[0-9]*', ato)[0]  # este sir vid '' daca nu gaseste
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                lri.append(coef + ' ' + spec)

        react = react + ' + '.join(lri)

        reacts.append(react)
    ## end --- for reactie in reactie

    reacts = list(map(lambda x: x.replace("  ", " "), reacts))  # elimina spatiile duble
    reacts = list(map(lambda x: x.strip(), reacts))  # elimina spatiile de la inceput si sfarsit

    print("Cate reactie sunt")
    print(reacts)

    return specii, reacts


def getReactii4Tellurium(listaLiniiFisier : [str] ) -> [str]:
    '''
    :param listaLiniiFisier:
        obtinuta prin readlines()
    :return reactii_individuale: [str]
       conversteste reactii <--> bidirectioanale in 2 catre dreapta ->
       inverseaza <-- in ->
       si --> devine ->
    '''
    lista_ecuatii : [] = list(map(lambda x: x.strip(), listaLiniiFisier))  # scapa de un <enter> la sfarsit
    #print(b)

    # ---- inlocuirea sagetilor -----
    reactii_individuale : [str] = []
    for ecuatie in lista_ecuatii:
        positionFound = ecuatie.find('<-->')
        if positionFound > -1:  # reactie bidirectionala
            reactii_individuale.append(ecuatie.replace('<-->', '->'))  # reactia directa
            #o inverseaza si o face directa
            reactii_individuale.append(ecuatie[positionFound + 4:len(ecuatie)].strip() + '->' + ecuatie[0:positionFound].strip())
        else:
            positionFound = ecuatie.find('<--')
            if positionFound > -1:
                # o inverseaza ca sa aiba acelasi format
                reactii_individuale.append(ecuatie[positionFound + 4:len(ecuatie)].strip() + '->' + ecuatie[0:positionFound].strip())
            else:
                reactii_individuale.append(ecuatie.replace('-->', '->'))  # reactia este simpla, doar de la stanga la dreapta
    #print( reactii_individuale )

    return list(map(lambda x: x.replace(" ", ""), reactii_individuale))


def create_figure():
    global select, durata

    filename = 'templates/metode_lucru/' + select
    tel = crn2tellurium(filename)  #   tellurium output !!!

    print(select)
    print(durata)

    #teltest =' -> A; k1\n2 A + 3 B -> 4 C; k2*A*A*B*B*B\n4 C -> 2 A + 3 B; k3*C*C*C*C\n2 B -> C + 3 A; k4*B*B\n2 B -> C; k5*B*B\nC -> 2 B; k6*C\nC -> ; k7*C\n\nk1 = 7;\nk2 = 7;\nk3 = 7;\nk4 = 7;\nk5 = 7;\nk6 = 7;\nk7 = 7;\n\n\nA = 1;\nB = 1;\nC = 1;\n'
    #simu = te.loada(teltest)

    # Am modificat aici !!! ------------------------------------------------
    te.setDefaultPlottingEngine('matplotlib')
    simu = te.loada(tel)
    print(tel)

    # matricea stoichiometrica
    stoicm = simu.getFullStoichiometryMatrix()
    print('asta stoichiometrica')
    print(stoicm)
    print(type(stoicm))

    listaToShowMatrice = []
    for stoicmLine in str(stoicm).split("\n"):
        if stoicmLine and not stoicmLine.isspace():
            listaToShowMatrice.append(stoicmLine)

    # numele ratelor de reactie
    ka = simu.getGlobalParameterIds()
    print(ka)

    # valorile retelor de reactie
    ra = simu.getReactionRates()
    print(ra)

    #gen de ce s-a numit amplitudine si durata cand amandoua arata practic durata?=)) de unde pana unde
    number_of_points = 1000
    simulation_results = simu.simulate(start = float(amplitudine), end = float(durata), points=number_of_points, output_file='') #da return la rezultate

    # simu.plot(title=str(titlu), xtitle=str(x_titlu), ytitle=str(y_titlu))

    import matplotlib
    from matplotlib import pyplot as plt
    # sa poata plotui fara sa printeze pe ecran ceva, doar in fisier
    matplotlib.use('agg')
    import numpy as np

    x_axis = []
    for i in range(number_of_points):
        x_axis.append(simulation_results[i][0])

    np_simulation_results = np.array(simulation_results)
    # like gen the first column (representing time) would become the first line so we scrap that and we're only left with this
    #TODO: poti sa tai coloana unu fara sa faci transpusa lol faci pythnon way st sa ma intorc del kauflad si fac
    np_simulation_results_species = np_simulation_results.transpose()[1:].transpose() #dmn ce clunky sincer incredibile calculatoarele ca pot sa faca asta in the blink of an eye

    # print('xaxis')
    # print(x_axis)
    print('doar speciile')
    print(len(np_simulation_results_species))
    print(np_simulation_results_species)

    plt.plot(x_axis, np_simulation_results_species)
    plt.savefig('static/graficvik.svg')

    #   simul = te.loada(tel)

    #   m = simul.simulate(float(text1), float(text), 1000)   # era 100

    #   from matplotlib import pyplot as simul
    #   figg = simul.figure(figsize=(9,6))
    #   ax = figg.gca(projection='3d')
    #   ax.view_init(20,40)
    #   ax.plot(m[:,0], m[:,1], m[:,2], 'r', label='parametric curve')
    #   ax.legend()
    #   ax.set_title('wireframe');
    #   ax.set_xlabel('time')
    #   ax.set_ylabel('S1')
    #   ax.set_zlabel('S2');
    #   simul.show()
    #   from matplotlib import pyplot as simul
    #   simul.savefig('static/1grafic3d.svg')

    simull = te.loada(tel)

    simull.simulate(float(amplitudine), float(durata), 1000, session.get('specii'))  # era 100
    print('inainte de al doilea plot')
    simull.plot(title=str(titlu), xtitle=str(x_titlu), ytitle=str(y_titlu))
    print('dupa de al doilea plot')

    # simull.show()
    from matplotlib import pyplot as simull
    simull.savefig('static/grafic1.svg')

    #   simulll = te.loada(tel)

    #   m = simulll.simulate(float(text1), float(text), 1000)   # era 100

    #   from matplotlib import pyplot as simulll
    #   figg = simulll.figure(figsize=(9,6))
    #   ax = figg.gca(projection='3d')
    #   ax.view_init(20,40)
    #   ax.plot(m[:,1], m[:,2], m[:,3], 'r')
    #   ax.legend()
    #   ax.set_title('wireframe');
    #   ax.set_xlabel('S1')
    #   ax.set_ylabel('S2')
    #   ax.set_zlabel('S3');
    #   simul.show()
    #   from matplotlib import pyplot as simulll
    #   simulll.savefig('static/2grafic3d.svg')

    # Pana aici !!! --------------------------------------------------------

    listaToShowEcuatii = tel.split("\n")

    return [render_template("home.html"), listaToShowEcuatii, listaToShowMatrice]


def crn2tellurium(filename):
    ## filename = 'crn_a_b_c.txt'
    #  filename = 'crn.txt'

    file_lines = open(filename, 'rt').readlines()

    reactii_individuale = getReactii4Tellurium(file_lines)

    kcont = 0  # cate reactii sunt
    krates = []  # lista cu vitezele de reactie

    for reactie in reactii_individuale:  # gaseste vitezele de reactie
        kcont = kcont + 1  # de la 1 la cate reactii sunt
        krate = ''  # rata de reactie
        krate = krate + 'k' + str(kcont) #incepe cu 1:  k1 k2 k3

        le = reactie.split('->')[0]
        ats = le.split('+')
        if ats != ['0']:  # zero barat in stanga
            for ato in ats:
                coef = re.findall(r'^[0-9]*', ato)[0]  # este sir vid '' daca nu gaseste
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]

                cnt = 0
                if coef == '':
                    cnt = 1
                else:
                    cnt = int(coef)

                for i in range(cnt):
                    krate = krate + '*' + spec  # adauga *A*A*A de cata ori era, ex: A3. edit viktorashi: darr astsa face daca e 3A nu A3
                    #daca e 3ABC devine k1*ABC*ABC*ABC
                    #daca e ABC3 devine k1*ABC3
                    #daca e 3ABC + 3C -> 2C
                    #       3C -> 2A devine [ k1*ABC*ABC*ABC*3C , k2*C*C*C ]

        krates.append(krate)

    print('krates: ')
    print(krates)
    specii, reacts = getReactionMeta(session, reactii_individuale)

    ## --- creeaza stringul de Tellurium

    tel = ''
    ii = 0
    for reactie in reacts:
        tel = tel + reactie + '; ' + krates[ii] + '\n'
        ii = ii + 1

    tel = tel + '\n'

    # THE VALUE FOR THE CONSTANTS REACTIONS!!!
    ######valk = [str(text4), str(text8)]   # valoarea pentru constantele de reactie
    global constArray
    valk = constArray  #Asta e globala setata in input_user_post
    print('constArrayu cu cate kuri adica reactii sunt')
    print(constArray, kcont)
    #pt fiecare reactie face k1 = valoarea;
            #                k2 = valoarea;
    for k in range(kcont):
        tel = tel + 'k' + str(k + 1) + ' = ' + str(valk[k]) + ';\n'  # era: str(valk[k-1])

    tel = tel + '\n'

    # THE VALUE FOR THE INITIAL CONDITIONS!!!
    valinit = valInitArray  #Asta e globala setata in input_user
    for i in range(len(specii)):
        tel = tel + specii[i] + ' = ' + str(valinit[i]) + ';\n'
            #aici pune A = ce valoare a dat useru in UI

    tel = tel + '\n'

    print('acm da return crn2telluriumm')
    return tel


@app.route('/dateuser')
def form():
    return render_template('form.html')


@app.route('/data/', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        return render_template('data.html', form_data=form_data)


ip = subprocess.check_output(["ifconfig en0 | grep 'inet'| awk '{print$2}'"], shell=True, text=True).split("\n")[
    1].strip()

### ----- old way to set the IP ----- ###


if __name__ == '__main__':
    app.secret_key = "ceva"
    '''
    indented because of 
    * Ignoring a call to 'app.run()' that would block the current 'flask' CLI command.
   Only call 'app.run()' in an 'if __name__ == "__main__"' guard.
    '''
    port = 5000
    print('intra pe http://' + ip + ':' + str(port))
    app.run(host=ip, port=port, debug=True)

# ---------------------------------------

# US ip     10.0.0.50, port:5000
# campus ip 172.30.5.50, port:5000
# Ro ip     192.168.1.50, port:5000
