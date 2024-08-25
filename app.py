#import Flask
from flask import *
import subprocess
import os
import glob
import pygraphviz as pgv                                  # Am adaugat aici !!!  
import pandas as pd
import json
import plotly
import plotly.express as px
import re
import tellurium as te
import matplotlib.pyplot as plt
#import subprocess
#import StringIO
import base64
from io import StringIO
#from crn2tellurium_module import *
import numpy as np
import base64
from io import BytesIO
from matplotlib.figure import Figure
#create an instance of Flask
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

app = Flask(__name__, template_folder='templates')

class DataStore():
    specs = None

data = DataStore()

def random():
     session['number'] = randint(0,2)
     return None

@app.route('/')
def home():
    return render_template("home.html")

def saveReactiiFile(theRequest):
    ecuatiiCount = int(theRequest.form.get('ecuatiiCount'))
    index = 1
    
    theFile = open("templates/metode_lucru/crn.txt","w")
    
    while index <= ecuatiiCount:
        ecLeft = theRequest.form.get('ec_'+str(index)+'_left')
        ecDir = theRequest.form.get('ec_'+str(index)+'_dir')
        ecRight = theRequest.form.get('ec_'+str(index)+'_right')
        
        ecDirString = ""
        if ecDir == 'left':
            ecDirString = '<--'
        elif ecDir == 'both':
            ecDirString = '<-->'
        elif ecDir == 'right':
            ecDirString = '-->'
            
        ecuatieFinala = ecLeft + " " + ecDirString + " " + ecRight
        
        theFile.write(ecuatieFinala)
        theFile.write("\n")
     
        index += 1
        
    theFile.close()
    
@app.route("/save_reactii", methods=['POST'])
def saveReactii():
    saveReactiiFile(request)
    
    return redirect(f"/input_user")
    
@app.route('/input_user')
def input_user():
    files = sorted(os.listdir('templates/metode_lucru/'))                # Am modificat aici !!! am adaugat: sorted(os.listdir('')) !!! -----------------------------------------
    temp=[]
    for file in files:
        temp.append({'name':file})
    specs1=session.get("specs")

    return render_template("input_user.html", data=temp, specs1=specs1)

@app.route('/input_user', methods=['GET', 'POST'])
def input_user_post():
    global select, text, text1, text2, text3, text4, specs, valInitArray, constArray
    text = request.form['durata']
    session['text'] = text
    processed_text = text.upper()

    text1 = request.form['amplitudine']
    session['text1'] = text1
    processed_text1 = text1.upper()

# Am modificat aici !!! -----------------------------------------------------    
    text2 = request.form['titlu']
    session['text2'] = text2
    processed_text2 = text2.upper()
    
    text3 = request.form['x_titlu']
    session['text3'] = text3
    processed_text3 = text3.upper()
    
    text4 = request.form['y_titlu']
    session['text4'] = text4
    processed_text4 = text4.upper()
    
    print(text2)
    print(text3)
    print(text4)
# Pana aici !!! -------------------------------------------------------------


    valInitArray = []
    valInitIndex = 0
    while True:
        try:
            requestValInit = request.form['valinit'+str(valInitIndex)]
            valInitArray.append(str(requestValInit))
            valInitIndex+=1
        except:
            break



    constArray = []
    constIndex = 0
    while True:
        try:
            requestConstInit = request.form['valk'+str(constIndex)]
            constArray.append(str(requestConstInit))
            constIndex+=1
        except:
            break

    #text3 = request.form['valinit0']
    #session['text3'] = text3
    #processed_text3 = text3.upper()

    #text5 = request.form['valinit1']
    #session['text5'] = text5
    #processed_text5 = text5.upper()

    ##text6 = request.form['valinit2']
    ##session['text6'] = text6
    ##processed_text6 = text6.upper()

    #text4 = request.form['valk0']
    #session['text4'] = text4
    #processed_text4 = text4.upper()

    #text8 = request.form['valk1']
    #session['text8'] = text8
    #processed_text8 = text8.upper()

    ##text9 = request.form['valk2']
    ##session['text9'] = text9
    ##processed_text9 = text9.upper()


    select = request.form.get('comp_select')
    session['select'] = select
    specs1=session.get("specs")
    #print(specs1)
    #print(select)
    #print(text)
    #print (text3)
#    return(str(select), text) # just to see what select is
    return redirect(f"/graph2")
    
@app.route('/graph2')
def plot_svg():
    [fig,listaToShow,listaToShowMatrice] = create_figure()
    output = io.BytesIO()
#    FigureCanvas(fig).print_png(output)
#    return Response(output.getvalue(), mimetype='image/png')
    #listaToShow = ['A','B','C']
    return render_template("graph.html",listaEcuatii=listaToShow,listaMatrice=listaToShowMatrice,pageName="Chemical Reaction Network (CRN) - 2D")

@app.route('/reactmeta', methods=['GET'])
def getReactionMetaHandler():
    reactionFileName = request.args.get('filename')
    f = open("templates/metode_lucru/"+reactionFileName, 'rt')
    a = f.readlines()
    s = getReactii4Tellurium(a)
    specs,reacts = getReactionMeta(session,s)

    specsJson = json.dumps(specs)
    return "{ \"specCount\":\""+str(len(specs))+"\",\"specsList\":"+specsJson+",\"reactsCount\":\""+str(len(reacts))+"\"}"   #Json facut de mana :)

def getReactionMeta(session,s):

    global specs #Aici o sa fie colectia de specii
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
    session["specs"]=specs
    #print( krates )
    print("Cate specii sunt:")
    print( specs )
    print( specs[0] )
    print( specs[1] )

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

    print("Cate reactii sunt")
    print(reacts)

    return specs,reacts

def getReactii4Tellurium(listaLiniiFisier):
    b = list( map(lambda x:x.strip(), listaLiniiFisier) )  # scapa de un <enter> la sfarsit
    #print(b)



    # ---- inlocuirea sagetilor -----
    r = [];
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

    return list( map(lambda x:x.replace(" ", ""), r) )

def create_figure():
    global select
    session['select']=select
    filename = 'templates/metode_lucru/'+select
    tel = crn2tellurium(filename)    #   tellurium output !!!
    #print(select)
    print(text)
    print("ceva")
    #session['text'] = text
    #session['text1'] = text1
    #session['text3'] = text3
    #session['text4'] = text4
    #session['text5'] = text5
    #session['text6'] = text6
    #session['text8'] = text8
    #session['text9'] = text9
    print(text)
    print(select)
    #print(text3)

#teltest =' -> A; k1\n2 A + 3 B -> 4 C; k2*A*A*B*B*B\n4 C -> 2 A + 3 B; k3*C*C*C*C\n2 B -> C + 3 A; k4*B*B\n2 B -> C; k5*B*B\nC -> 2 B; k6*C\nC -> ; k7*C\n\nk1 = 7;\nk2 = 7;\nk3 = 7;\nk4 = 7;\nk5 = 7;\nk6 = 7;\nk7 = 7;\n\n\nA = 1;\nB = 1;\nC = 1;\n'
#simu = te.loada(teltest)

    
# Am modificat aici !!! ------------------------------------------------
    simu = te.loada(tel)
    print(tel)
    print(type(tel))
    print(simu)
    print(type(simu))
    
    listaToShowEcuatii = []
    for telLine in tel.split("\n"):
        #if telLine and not telLine.isspace():
        listaToShowEcuatii.append(telLine)
    
    # matricea stoichiometrica
    stoicm = simu.getFullStoichiometryMatrix();
    print(stoicm)
    
    listaToShowMatrice = []
    for stoicmLine in str(stoicm).split("\n"):
        if stoicmLine and not stoicmLine.isspace():
            listaToShowMatrice.append(stoicmLine)
    
    # numele ratelor de reactie
    ka = simu.getGlobalParameterIds();
    print(ka)
    
    # valoriel ratelor de reactie
    ra = simu.getReactionRates();
    print(ra)
    
#    dsr = simu.draw(width=100)
#    import matplotlib.pyplot as dsr
#    dsr.savefig('static/DSRgraph.png')
    
    simu.simulate(float(text1), float(text), 1000)   # era 100
    simu.plot(title = str(text2), xtitle = str(text3), ytitle = str(text4))
# Pana aici !!! --------------------------------------------------------
    simu.show()
    from matplotlib import pyplot as simu
    simu.savefig('static/grafic.svg')
    
    
    
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
    
    simull.simulate(float(text1), float(text), 1000, ['A','B'])   # era 100
    simull.plot(title = str(text2), xtitle = str(text3), ytitle = str(text4))

    simull.show()
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
    return [render_template("home.html"),listaToShowEcuatii,listaToShowMatrice]

def crn2tellurium(filename):

    ## filename = 'crn_a_b_c.txt'
#    filename = 'crn.txt'
    f = open(filename, 'rt')
    a = f.readlines()
    #print(a)

    s = getReactii4Tellurium(a)

    kcont = 0   # cate reactii sunt
    krates = []   # lista cu vitezele de reactie
    for x in s:   # gaseste vitezele de reactie
        kcont = kcont + 1;  # de la 1 la cate reactii sunt
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

    specs,reacts = getReactionMeta(session,s)


    ## --- creaza stringul de Tellurium

    tel = ''
    ii = -1;
    for x in reacts:
        ii = ii + 1;
        tel = tel + x + '; ' + krates[ii] + '\n'


    tel = tel + '\n'

    #session['text4'] = text4
    #session['text8'] = text8
    #session['text9'] = text9

    #valk=str(text9)
    
    # THE VALUE FOR THE CONSTANTS REACTIONS!!!
    ######valk = [str(text4), str(text8)]   # valoarea pentru constantele de reactie
    valk = constArray #Asta e globala setata in input_user
    print(len(constArray), kcont)
    #valk=1
    for k in range(0,kcont):        # era: range(1,kcont)
        tel = tel + 'k' + str(k+1) + ' = ' + str(valk[k]) + ';\n'     # era: str(valk[k-1])

    tel = tel + '\n'
    print('acumaa')
    print(kcont)
    print(tel)
    #session['text3'] = text3
    #session['text5'] = text5
    #session['text6'] = text6

    #print (text3)
    
    # THE VALUE FOR THE INITIAL CONDITIONS!!!
    #valinit = str(text3)  # valoarea pentru conditiile initiale
    ######valinit=[str(text3), str(text5), str(text6)]
    valinit = valInitArray #Asta e globala setata in input_user
    for i in range(0,len(specs)):
        tel = tel + specs[i] + ' = ' + str( valinit[i] ) + ';\n'

    tel = tel + '\n'
###

    #print(tel)
    #specs1=session.get("specs")
    #print(specs1)
    return tel


## --- end crn2tellurium() ----------------------------------------------------


if __name__ == "__main__":
    print("This module is not to be run form the __main__ scope")





@app.route('/dateuser')
def form():
    return render_template('form.html')

@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        return render_template('data.html',form_data = form_data)


ip = subprocess.check_output(["ifconfig ens33 | grep 'inet'| awk '{print$2}'"],shell=True,text=True).split("\n")[0].strip()

### ----- old way to set the IP ----- ###

if __name__ == '__main__':
    app.secret_key="ceva"
    '''
    indented because of 
    * Ignoring a call to 'app.run()' that would block the current 'flask' CLI command.
   Only call 'app.run()' in an 'if __name__ == "__main__"' guard.
    '''
    app.run(host=ip, port ='5000', debug=True)

# ---------------------------------------

# US ip     10.0.0.50, port:5000
# campus ip 172.30.5.50, port:5000
# Ro ip     192.168.1.50, port:5000
