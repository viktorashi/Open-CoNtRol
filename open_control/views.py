import json
import os

from flask import request, redirect, url_for

from open_control import app
from open_control.utils import *

save_crn_filepath_location = 'open_control/templates/metode_lucru/crn.txt'


def get_crn_species_reactions() -> dict:
    """

    :return: species data including what they are and how many reactions
    { speciiList: [str], reactsCount: int }
    """

    reactii_individuale: [str] = open(save_crn_filepath_location, 'r').readlines()

    specii, reacts = get_reaction_meta(reactii_individuale)
    species_data = {
        'speciiList': specii,
        'reactsCount': len(reacts),
    }

    print(species_data)
    return species_data


@app.get('/')
def home():
    lma = 'sa moara masa'
    return render_template("home.html")


@app.post("/save_reactii_antimony")
def save_reactii_antimony():
    """
    Only used when submitting the form via the Antimony code textarea
    :return:
    """
    code = request.form.get('antimony-textarea')
    format = request.form.get('format')
    print(code)

    match format:
        case 'antimony':
            custom_format = save_reactions_from_antimony_textarea_to_file(code)
            get_numerical_analysis_save_to_session(code)
            species, reacts = get_reaction_meta(
                custom_format)  # this just saves specii to the session so ion even think we need to get its output
        case 'simple':
            code = code.split('\n')
            save_crn2file(code)
            tellurium_definitions, _ = crn2antimony_definitions(save_crn_filepath_location)
            # delete last two newline characters cuz it breaks for some reason
            tellurium_definitions = tellurium_definitions[:-2]
            get_numerical_analysis_save_to_session(tellurium_definitions)
        case _:
            print("idk what the user submitted if im being honest")

    return redirect(url_for('numerical_analysis'))


@app.post("/save_reactii_dropdowns")
def save_reactii_dropdowns():
    """
    Only used when submitting the form via the manual writing dropdowns
    :return:
    """
    save_reactions_in_file_from_dropdowns(request)

    # you essentially have to have antimony code to do numerical analysis,
    # the call got get_numerical_analysis_save_to_session is with the same antimony code that it would on
    # the save_reactii_antimony route, but this time it's read from the file (it was saved to) and generated on the fly
    # with 0 init values instead of the ones from the form of time_graph_input.
    # I know, it's spaghetti code literally schizo coding

    reactii_individuale: [str] = open(save_crn_filepath_location, 'r').readlines()

    # parsing the reactions to get the species and the reactions
    specii, reacts = get_reaction_meta(reactii_individuale)
    val_init_array = [str(0)] * len(specii)
    const_array = [str(0)] * len(reacts)

    session['init_vals'] = val_init_array
    session['react_constants'] = const_array

    antimony_code, _ = crn2antimony_definitions('crn.txt')
    # remove double newlines
    antimony_code = antimony_code.replace('\n\n', '\n')[:-1]  # remove the last newline, don't ask why, just trust me
    print(antimony_code)

    get_numerical_analysis_save_to_session(antimony_code)

    return redirect(url_for('numerical_analysis'))


def get_numerical_analysis_save_to_session(antimony_code: str):
    """
    :return: Saves the data from the numerical analysis form to the current session
    """
    [stoichiometry_in_latex, new_antimony, tex_equations, species_to_index_mapping, stoich_matrix_rank] = get_numerical_analysis(
        antimony_code)
    # absolutely unreadable but it just deletes all the right-hand side (rate laws with k1*A...) of the equations
    definitions = [definition.split(';')[0] for definition in new_antimony.split('\n')]
    species_to_index_in_tex = {key: f"${value}$" for key, value in species_to_index_mapping.items()}

    session['definitions'] = definitions
    session['stoichiometry_in_latex'] = stoichiometry_in_latex
    session['tex_equations'] = tex_equations
    session['species_to_index_in_tex'] = species_to_index_in_tex
    session['stoich_matrix_rank'] = stoich_matrix_rank


@app.get("/numerical_analysis")
def numerical_analysis():
    return render_template("numerical_analysis.html", definitions=session.get('definitions'),
                           stoichMatrix=session.get('stoichiometry_in_latex'), equations=session.get('tex_equations'),
                           species_mapping=session.get('species_to_index_in_tex'), stoich_matrix_rank=session.get('stoich_matrix_rank'))


@app.post('/graph')
def graph():
    graph_type = request.form.get('graph_type')
    print('tipu de graph: ', graph_type)

    match graph_type:
        case 'regular':
            return redirect(url_for('time_graph_input'))
        case 'diagram':
            return redirect(url_for('diagram'))
        case 'phase_portrait':
            return redirect(url_for('phase_portrait_input'))


# todo sa vezi unde se foloeste asta
@app.get('/time_graph_input')
def time_graph_input():
    """
    :return: Renders the time graph input front-end with the species data
    """
    species_data = get_crn_species_reactions()

    return render_template('time_series_graph_input.html', species_data=species_data)


@app.post('/time_graph_input')
def time_graph_post():
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
    val_init_array = []
    val_init_index = 0

    while True:
        try:
            request_val_init = request.form['valinit' + str(val_init_index + 1)]
            val_init_array.append(str(request_val_init))
            val_init_index += 1
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

    checked_species = []
    for i in range(val_init_index):
        try:
            request_checked_species = request.form['check' + str(i + 1)]
            checked_species.append(str(request_checked_species))
        except:
            pass

    session['checked_species'] = checked_species
    session['init_vals'] = val_init_array
    session['react_constants'] = const_array

    print(session.get('end_time'))
    print(session.get('start_time'))
    print(session.get('titlu'))
    print(session.get('x_titlu'))
    print(session.get('y_titlu'))
    print(session.get('init_vals'))
    print(session.get('react_constants'))
    print(session.get('select'))
    print('toate speciile:')
    print(session.get('specii'))
    print('daor speciile checkuite:')
    print(session.get('checked_species'))

    return redirect(url_for('time_graph'))


@app.get('/time_graph')
def time_graph():
    """
    :return: Renders the graph front-end with the antimony code shown and stoichiometry matrix
    """
    create_figure()
    [lista_ecuatii, stoichiometric_matrix] = get_crn_equations_stoich()
    return render_template('time_graph.html', listaEcuatii=lista_ecuatii, stoichMatrix=stoichiometric_matrix)


@app.get('/diagram')
def diagram():
    draw_diagram()
    [listaToShow, stoichiometric_matrix] = get_crn_equations_stoich()
    return render_template('diagram.html', listaEcuatii=listaToShow, stoichMatrix=stoichiometric_matrix)


@app.get('/phase_portrait_input')
def phase_portrait_input():

    species_data = get_crn_species_reactions()

    return render_template('phase_portrait_input.html', species_data=species_data)


# todo nu merge pentru a+b <-> c si 1,1,1,1 la toate cu a vs c
@app.post('/phase_portrait_input')
def phase_portrait_post():
    """
    Saves the form data from the request to the current flask session
    including the "select"-ed file name
    start_time, end_time, titlu, x_titlu, y_titlu,
    the initial values of concentration for each species,
    the values for the reaction rates (the k's)
    and the species for each you want to generate the phase portrait for

    :return: Redirects the user to '/phase_portrait' for displaying the graph generated
    """

    session['select'] = request.form.get('comp_select')

    session['start_time'] = request.form['start_time']

    session['end_time'] = request.form['end_time']

    session['titlu'] = request.form['titlu']

    # lista cu coeficientii pt fiecare specie
    val_init_array = []
    val_init_index = 0

    while True:
        try:
            request_val_init = request.form['valinit' + str(val_init_index)]
            val_init_array.append(str(request_val_init))
            val_init_index += 1
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

    checked_species = []
    species_index = 0
    while True:
        try:
            request_checked_species = request.form['check' + str(species_index)]
            checked_species.append(str(request_checked_species))
            species_index += 1
        except:
            break

    session['init_vals'] = val_init_array
    session['react_constants'] = const_array
    session['checked_species'] = checked_species

    print(session.get('end_time'))
    print(session.get('start_time'))
    print(session.get('titlu'))
    print(session.get('init_vals'))
    print(session.get('react_constants'))
    print(session.get('checked_species'))
    print(session.get('select'))
    print(session.get('specii'))

    return redirect(url_for('phase_portrait'))


@app.get('/phase_portrait')
def phase_portrait():
    draw_phase_portrait()

    [listaToShow, stoichiometric_matrix] = get_crn_equations_stoich()
    return render_template('phase_portrait.html', listaEcuatii=listaToShow, stoichMatrix=stoichiometric_matrix)
