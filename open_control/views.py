import json
import os

from flask import render_template, request, redirect, session, url_for

from open_control import app
from open_control.utils import *


@app.get('/')
def home():
    return render_template("home.html")


@app.post("/save_reactii_antimony")
def save_reactii_antimony():
    """
    Only used when submitting the form via the Antimony code textarea
    :return:
    """
    antimony_code = request.form.get('antimony-textarea')
    print(antimony_code)

    get_numerical_analysis_save_to_session(antimony_code)

    return redirect(url_for('numerical_analysis'))


@app.post("/save_reactii_dropdowns")
def save_reactii_dropdowns():
    """
    Only used when submitting the form via the manual writing dropdowns
    :return:
    """
    save_reactions_file(request)

    # you essentially have to have antimony code to do numerical analysis,
    # the call got get_numerical_analysis_save_to_session is with the same antimony code that it would on
    # the save_reactii_antimony route, but this time it's read from the file (it was saved to) and generated on the fly
    #with 0 init values instead of the ones from the form of input_user.
    #I know, it's spaghetti code literally schizo coding

    reactii_individuale: [str] = reactions2tellurium_format('crn.txt')

    #parsing the reactions to get the species and the reactions
    specii, reacts = get_reaction_meta(reactii_individuale)
    val_init_array = [str(0)] * len(specii)
    const_array = [str(0)] * len(reacts)

    session['init_vals'] = val_init_array
    session['react_constants'] = const_array

    antimony_code, _ = crn2antimony_definitions('crn.txt')
    #remove double newlines
    antimony_code = antimony_code.replace('\n\n', '\n')[:-1] #remove the last newline, don't ask why, just trust me
    print(antimony_code)

    get_numerical_analysis_save_to_session(antimony_code)

    return redirect(url_for('numerical_analysis'))


@app.get("/numerical_analysis")
def numerical_analysis():
    return render_template("numerical_analysis.html", definitions=session.get('definitions'),
                           stoichMatrix=session.get('stoichiometry_in_latex'), equations=session.get('tex_equations'),
                           species_mapping=session.get('species_to_index_in_tex'))

@app.get('/input_user')
def input_user():
    """
    :return: The template with the inputs required to generate the graph, with all the file names
    that contain CRN's
    """
    files = sorted(os.listdir('open_control/templates/metode_lucru/'))
    filename_data = []
    for file in files:
        filename_data.append({'name': file})

    specii = session.get("specii")
    print('speciiles deja in sesiune:')
    print(specii)

    return render_template("input_user.html", data=filename_data)

@app.get('/crn_data')
def get_crn_data():
    """
    gets called by the input_user.html template with the filename, parses its data
    to find its species and how many reactions are in the CRN's, returning them back
    to the same template
    :return:
    """

    reactii_individuale: [str] = reactions2tellurium_format(request.args.get('filename'))

    specii, reacts = get_reaction_meta(reactii_individuale)
    data = {
        'speciiList': specii,
        'reactsCount': str(len(reacts)),
    }
    print("Speciile:")
    print(specii)
    print("reactiile")
    print(reacts)
    print("dictu de o sa se trimita")
    print(data)
    jsonu = json.dumps(data)
    print("jsonu de o sa se trimita")
    print(jsonu)
    return jsonu


@app.post('/input_user')
def input_user_post():
    """
    Saves the form data from the request to the current flask session
    including the "select"-ed file name
    start_time, end_time, titlu, x_titlu, y_titlu,
    the initial values of concentration for each species
    and the values for the reaction rates (the k's)

    :return: Redirects the user to '/graph' for displaying the graph generated
    """

    session['select'] = request.form.get('comp_select')

    session['start_time'] = request.form['start_time']

    session['end_time'] = request.form['end_time']

    session['titlu'] = request.form['titlu']

    session['x_titlu'] = request.form['x_titlu']

    session['y_titlu'] = request.form['y_titlu']

    # lista cu coeficientii pt fiecare specie
    valInitArray = []
    valInitIndex = 0

    while True:
        try:
            request_val_init = request.form['valinit' + str(valInitIndex)]
            valInitArray.append(str(request_val_init))
            valInitIndex += 1
        except:
            break

    const_array = []
    const_index = 0

    while True:
        try:
            request_const_init = request.form['valk' + str(const_index)]
            const_array.append(str(request_const_init))
            const_index += 1
        except:
            break

    session['init_vals'] = valInitArray
    session['react_constants'] = const_array

    print(session.get('end_time'))
    print(session.get('start_time'))
    print(session.get('titlu'))
    print(session.get('x_titlu'))
    print(session.get('y_titlu'))
    print(session.get('init_vals'))
    print(session.get('react_constants'))
    print(session.get('select'))
    print(session.get('specii'))

    return redirect(url_for('plot_svg'))


@app.get('/graph')
def plot_svg():
    """
    :return: Renders the graph front-end with the antimony code shown and stoichiometry matrix
    """
    [fig, listaToShow, stoichiometric_matrix] = create_figure(session)
    #    FigureCanvas(fig).print_png(output)
    #    return Response(output.getvalue(), mimetype='image/png')
    return render_template("graph.html", listaEcuatii=listaToShow, stoichMatrix=stoichiometric_matrix,
                           pageName="Chemical Reaction Network (CRN) - 2D")


def get_numerical_analysis_save_to_session(antimony_code: str):
    """
    :return: Saves the data from the numerical analysis form to the current session
    """
    [stoichiometry_in_latex, new_antimony, tex_equations, species_to_index_mapping] = get_numerical_analysis(antimony_code)
    # absolutely unreadable but it just deletes all the right-hand side (rate laws with k1*A..) of the equations
    definitions = [definition.split(';')[0] for definition in new_antimony.split('\n')]
    species_to_index_in_tex = {key: f"${value}$" for key, value in species_to_index_mapping.items()}

    session['definitions'] = definitions
    session['stoichiometry_in_latex'] = stoichiometry_in_latex
    session['tex_equations'] = tex_equations
    session['species_to_index_in_tex'] = species_to_index_in_tex
