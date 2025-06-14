import tellurium as te
import matplotlib
import re
from flask import render_template, session
from typing import List, Tuple, Dict, Any, LiteralString

save_crn_filepath_location = 'open_control/templates/metode_lucru/crn.txt'


def parse_reaction(reaction: str):
    """
    Parse a single reaction line into reactants, products, and rate law.
    :param reaction: reaction of example A + B -> C;k1*A*B
    :return Tuple[reactants, products, rate_law] in this case
    """
    reaction_parts = reaction.split(';')
    if len(reaction_parts) != 2:
        raise ValueError("Invalid reaction format. Expected 'reaction; rate_law'")

    equation, rate_law = [part.strip() for part in reaction_parts]

    sides = equation.split('->')
    if len(sides) != 2:
        raise ValueError("Invalid equation format. Expected 'reactants -> products'")

    reactants = [r.strip() for r in sides[0].split('+')]
    products = [p.strip() for p in sides[1].split('+')]

    return reactants, products, rate_law.strip()


def parse_species_term(term: str) -> Tuple[str, int]:
    """Parse a species term to get species name and its coefficient.
    returns: [species, coefficient]
    """
    match = re.match(r'^(\d+)?\s*([A-Za-z]\w*)$', term.strip())
    if not match:
        raise ValueError(f"Invalid species term: {term}")

    coef, species = match.groups()
    coef = int(coef) if coef else 1
    return species, coef


# This probably has so much functionality that I can reuse in the project and delete the old stuff ong too lazy to see what it is tho
class AntimonyConverter:
    def __init__(self):
        self.species = []
        self.species_to_index = {}  # a mapping for clarification which xi corresponds to which species

    def collect_species(self, reactions: List[str]):
        """Collect all unique species and assign them indices to the properties of the class."""
        all_species = set()
        for reaction in reactions:
            reactants, products, _ = parse_reaction(reaction)
            for term in reactants + products:
                species, coeff = parse_species_term(term)
                all_species.add(species)

        self.species = sorted(list(all_species))
        self.species_to_index = {species: f"x_{i + 1}" for i, species in enumerate(self.species)}

    def convert_rate_law(self, rate_law: str, species_powers: Dict[str, int]) -> str:
        """
        Convert species names in rate law to x_i notation with powers.

        example: k1*S0*S0 becomes k_1 x_4^2 given if the species S0 maps to x_4

        param: rate_law of the form k{integer}\*{species}+
        param: species_powers of the
        return:
        """

        # Convert all species to their x_i notation with appropriate powers
        for species, power in species_powers.items():
            index = self.species_to_index[species]
            if power > 1:
                rate_law = re.sub(rf'\b{species}\b(?:\*{species}\b)*', f"{index}^{power}(t)", rate_law)
            else:
                old_rate = rate_law
                rate_law = re.sub(rf'\b{species}\b\*', f"{index}(t)", rate_law)
                # if it doesn't have a star for multiplication, meaning its at the end
                if old_rate == rate_law:
                    rate_law = re.sub(rf'\b{species}\b', f"{index}(t)", rate_law)

        # k1*x_t(t) to k1 x_t(t)
        k_index = re.match(r'k(\d+)', rate_law).groups()[0]
        rate_law = re.sub(r'k(\d+\*)', f'k_{k_index} ', rate_law)

        return rate_law

    def diff_equations_in_tex_format(self, reactions: List[str]) -> str:
        """
        Title says it all \s
        :param reactions: reactions in antimony definition format ( https://tellurium.readthedocs.io/en/latest/antimony.html#introduction-and-basics ):
        example:
            A + B -> C; k1*A*B
            2B -> C; k2*B*B

        :return: system of differential equations for the system with the corresponding form for the example above being :
        \begin{equation*}
        \begin{array}{ll}
        \dot{x}_1(t) = -k_1 x_1(t) x_2(t) \\
        \dot{x}_2(t) = -k_1 x_1(t) x_2(t) - k_2 x_2^3(t) \\
        \dot{x}_3(t) =  k_1 x_1(t) x_2(t) + k_2 x_2^3(t)
        \end{array}
        \end{equation*}
        """

        self.collect_species(reactions)
        species_terms = {species: [] for species in self.species}

        for reaction in reactions:
            reactants, products, rate = parse_reaction(reaction)

            # Count species occurrences in reactants
            species_powers = {}
            for reactant in reactants:
                species, coefficient = parse_species_term(reactant)
                species_powers[species] = coefficient

            # Convert the rate law
            converted_rate = self.convert_rate_law(rate, species_powers)

            # Process reactants (negative terms)
            for reactant in reactants:
                species, coefficient = parse_species_term(reactant)
                if coefficient > 1:
                    term = f"-{coefficient}\cdot {converted_rate}"
                else:
                    term = f"-{converted_rate}"
                species_terms[species].append(term)

            # Process products (positive terms)
            for product in products:
                species, coefficient = parse_species_term(product)
                if coefficient > 1:
                    term = f"+{coefficient}\cdot {converted_rate}"
                else:
                    term = f"+{converted_rate}"
                species_terms[species].append(term)

        equations = {}
        for species in self.species:
            if species_terms[species]:
                eqn = ''.join(species_terms[species])
                if eqn.startswith('+'):
                    eqn = eqn[1:]
                equations[species] = eqn
            else:
                equations[species] = '0'

        # equations nw has all the equations

        """And now we write them in TeX format"""
        tex_equations = []
        for i, species in enumerate(self.species, 1):
            eqn = equations[species]
            tex_eqn = f"\dot{{x}}_{i}(t) = {eqn} \\\\"
            tex_equations.append(tex_eqn)

        tex_equations = "\n".join(tex_equations)
        # whatever else is necessary to make the equations symmetric
        tex_equations = f"""
        \\begin{{equation*}}
        \\begin{{array}}{{ll}}
        {tex_equations}
        \\end{{array}}
        \\end{{equation*}}
        """
        return tex_equations


def save_reactions_in_file_from_dropdowns(req):
    """
    :param req:
         The Flask request object containing form data.
                    Expects form data with 'ecuatiiCount' (number of reactions) and for each reaction:
                    - 'ec_<index>_left': Left side of the reaction.
                    - 'ec_<index>_dir': Direction of the reaction. left := <-- ; right := --> ; both := <-->
                    - 'ec_<index>_right': Right side of the reaction.

    Saves to open_control/templates/metode_lucru/crn.txt file in this format:
       converteste reactii <--> bidirectioanale in 2 catre dreapta ->
       inverseaza <-- in ->
       si --> devine ->
       practic scrie toate reactiile ca reactie cu sageata catre dreapta, si inlocuieste --> cu ->
       pt formatul antimony
       deci sa fie clar face asta DOAR cu reactiile iar functia "crn2tellurium"

    :return: None
    """
    ecuatii_count = int(req.form.get('ecuatiiCount'))
    equations_list = []

    for index in range(1, ecuatii_count + 1):
        ec_left = req.form.get('ec_' + str(index) + '_left')
        ec_dir = req.form.get('ec_' + str(index) + '_dir')
        ec_right = req.form.get('ec_' + str(index) + '_right')

        ec_dir_string = ""
        if ec_dir == 'left':
            ec_dir_string = '<--'
        elif ec_dir == 'both':
            ec_dir_string = '<-->'
        elif ec_dir == 'right':
            ec_dir_string = '-->'

        ecuatie_finala = ec_left + " " + ec_dir_string + " " + ec_right

        # asa ii da overwrite la open_control/templates/metode_lucru/crn.txt
        equations_list.append(ecuatie_finala)

    # scapa de un <enter> la sfarsit
    lista_ecuatii: [] = list(map(lambda x: x.strip(), equations_list))

    # ---- inlocuirea sagetilor si rasucirea de ecuatii -----
    reactii_individuale: [str] = []
    for ecuatie in lista_ecuatii:
        positionFound = ecuatie.find('<-->')
        if positionFound > -1:  # reactie bidirectionala
            reactii_individuale.append(ecuatie.replace('<-->', '->'))  # reactia directa
            # o inverseaza si o face directa
            reactii_individuale.append(
                ecuatie[positionFound + 4:len(ecuatie)].strip() + '->' + ecuatie[0:positionFound].strip())
        else:
            positionFound = ecuatie.find('<--')
            if positionFound > -1:
                # o inverseaza ca sa aiba acelasi format
                reactii_individuale.append(
                    ecuatie[positionFound + 4:len(ecuatie)].strip() + '->' + ecuatie[0:positionFound].strip())
            else:
                reactii_individuale.append(
                    ecuatie.replace('-->', '->'))  # reactia este simpla, doar de la stanga la dreapta

    reactiile_individuale: [str] = list(map(lambda x: x.replace(" ", ""), reactii_individuale))

    the_file = open(save_crn_filepath_location, "w")
    for reactie in reactiile_individuale:
        the_file.write(reactie)
        the_file.write("\n")

    the_file.close()


def save_crn2file(custom_format):
    the_file = open(save_crn_filepath_location, "w")
    for line in custom_format:
        the_file.write(line)
        the_file.write("\n")
    the_file.close()


def save_reactions_from_antimony_textarea_to_file(antimony_code):
    """
    The code comes in the format
        A + B-> B; k1*A*B
        and then it gets saved in our (simpler) format in / to save_crn_filepath_location
        A + B -> B

    :param antimony_code:
        The Antimony code containing the reactions to be saved in the file.
    :return: the thing it wrote to the file
    """
    weird_custom_format: [str] = [line.split(';')[0] for line in antimony_code.split('\n')]
    save_crn2file(weird_custom_format)
    return weird_custom_format


# TODO dati seama cate are in comut cu crn2antomony ca sa nu mai fie atata cod duplicat
def get_reaction_meta(reactii_individuale: [str]) -> [[str], [str]]:
    """
    :param session: the global object session for the current user
    :param reactii_individuale: The reactions in Antimony format
    :return: The list of unique species and the reactions in Antimony format
    """
    specii: [str] = []

    for reactie in reactii_individuale:  # gaseste speciile
        ats = reactie.replace('->', '+').split('+')  # transforma si 4A + 5B -> C in 4A + 5B + C si le da split la +

        # scoate coeficientul din fata de la fiecare specie
        for ato in ats:
            if ato != '0':  # sa nu fie zero barat
                ato = ato.strip()
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                specii.append(spec)  # in place

    ## end -- for x in s

    specii = list(set(specii))  # removes duplicates
    specii.sort()  # alfabetic
    session['specii'] = specii

    # transforma din reactiile individuale de forma 2A + 3B -> 10C in 2  A  3  B -> 10  C
    reacts = []  # lista cu reactiile
    for reactie in reactii_individuale:

        [le, ri] = reactie.split('->')  # reactantii si produsii
        # le = reactie.split('->')[0]  # reactantii
        # ri = reactie.split('->')[1]  # produsii

        atsle = le.split('+')  # reactantii cu tot cu coeficientii
        atsri = ri.split('+')  # produsii cu tot cu coeficientii

        lle = []
        if atsle != ['0']:  # sa nu fie zero barat in stanga
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

    return specii, reacts


def get_stoichiometry_matrix_and_rank(antimony_code: str) -> list[2]:
    """
    Get the resulting stoichiometry matrix from the definitions of the system in antimony code
    :param antimony_code:
    :return: [ "the stoichiomatreic matrix in the roadRunner doubleMatrix format" , "the rank of the matrix" ]
    """
    road_runner = 'lmao'
    antimony_code_with_init = ''
    try:
        road_runner = te.loada(antimony_code)
        # gets thrown if the user hasn't specified a value for the parameters specified
    except RuntimeError:
        # k1, k2 ... params need to be initialised for it to work, so we'll just initialise them all with 0
        param_initialisation = ''
        # double newline means the end of a section in my format, the first section is the declaration part, and then we see how many lines are in that
        no_declaration_lines = len(antimony_code.split('\n\n')[0].split('\n'))

        antimony_code_with_init = antimony_code + '\r\n'
        for i in range(1, no_declaration_lines + 1):
            param_initialisation = param_initialisation + 'k' + str(i) + ' = 0 \r\n'

        antimony_code_with_init = antimony_code_with_init + param_initialisation
        road_runner = te.loada(antimony_code_with_init)

    return_val = [road_runner.getFullStoichiometryMatrix(), road_runner.getNrMatrix().shape[0]]
    return return_val


def get_numerical_analysis(antimony_code):
    """
    :param antimony_code: what is sounds like: https://tellurium.readthedocs.io/en/latest/antimony.html#introduction-and-basics
    :return: stoichiometry matrix along with the differential equations (in LaTeX form) used to describe the system and the species to index mapping to better understand the equations.

        Example: for a system :
            A + B -> C; k1*A*B
            3B -> C; k2*B*B*B

        we get the list of species: [A, B, C], corresponding to the functions [x1, x2, x3] respectively.
        we have the equations:
            x_1' = -k_1*x_1*x_2
            x_2' = -k_1*x_1*x_2 - k_2*x_2^3
            x_3' = k_1*x_1*x_2 + k_2*x_2^3

        which, in TeX should look like:
        $$ x_1'(t) = -k_1 \cdot x_1(t) \cdot x_2(t) $$
        $$ x_2'(t) = -k_1 \cdot x_1(t) \cdot x_2(t) - k_2 \cdot x_2^3(t) $$
        $$ x_3'(t) = k_1 \cdot x_1(t) \cdot x_2(t) + k_2 \cdot x_2^3(t) $$

    """
    # ok I done used claude for this cuz I got lazy https://claude.site/artifacts/bc895634-74fe-418b-bad2-f801907fc4ea

    converter = AntimonyConverter()
    print('kktu asta chiar imi ce era inainte')
    print(antimony_code)
    print('gata kktu asta chiar imi ce era inainte')
    tex_equations = converter.diff_equations_in_tex_format(antimony_code.split('\n'))
    species_to_index_mapping = converter.species_to_index
    [stoich_matrix, stoich_matrix_rank] = get_stoichiometry_matrix_and_rank(antimony_code)
    stoichiometry_in_latex = stoichiometry_in_tex(stoich_matrix)

    return [stoichiometry_in_latex, antimony_code, tex_equations, species_to_index_mapping, stoich_matrix_rank]


def create_figure():
    """
    takes the data from the session and simulates then plots the simulation results to a file,
    which will then be used in the template to be displayed do the frontend
    :return: the antimony code and stoichiometry matrix
    """

    select = session.get('select')
    end_time = session.get('end_time')
    start_time = session.get('start_time')
    titlu = session.get('titlu')
    x_titlu = session.get('x_titlu')
    y_titlu = session.get('y_titlu')
    checked_species = session.get('checked_species')

    print(select)
    print(end_time)

    # Am modificat aici !!! ------------------------------------------------
    matplotlib.use(
        'agg')  # agg e un backend cu care poti sa plotuiesti in fisiere direct, fara sa vezi tu in terminal sau cv
    te.setDefaultPlottingEngine('matplotlib')  # o sa foloseasca backendu acela bun din matplot

    antimony_code = crn2antimony(select)  # tellurium output !!!
    print('coadele de antiomony')
    print(antimony_code)
    print('------pana aici-------------')
    road_runner = te.loada(antimony_code)

    # sa poata plotui fara sa printeze pe ecran ceva, doar in fisier
    print(antimony_code)

    # matricea stoichiometrica

    # numele ratelor de reactie
    k_s = road_runner.getGlobalParameterIds()
    print(k_s)

    # valorile retelor de reactie
    reation_rates = road_runner.getReactionRates()
    print(reation_rates)

    checked_species_with_time = checked_species
    checked_species_with_time.insert(0, 'time')
    number_of_points = 1000
    # da return la rezultate si pot fi folosite rezultatele din simulare pentru plot()
    road_runner.simulate(start=float(start_time), end=float(end_time), points=number_of_points,
                         selections=checked_species_with_time)

    print(select)
    print(start_time)
    print(end_time)
    print(titlu)
    print(x_titlu)
    print(y_titlu)

    save_graph_to_file = 'open_control/static/graphic.svg'
    road_runner.plot(xlabel=x_titlu, ylabel=y_titlu, figsize=(9, 6), title=str(titlu), savefig=save_graph_to_file,
                     ordinates=checked_species)


def get_crn_equations_stoich():
    antimony_code = crn2antimony(save_crn_filepath_location)

    # zici ca-i naming convention TJ Miles
    lista_to_show_ecuatii = antimony_code.split("\n")

    road_runner = te.loada(antimony_code)

    stoicm = road_runner.getFullStoichiometryMatrix()
    print('asta stoichiometrica')
    print(stoicm)
    print(type(stoicm))

    # "template not found" error keeps popping up for some reason (it works lol)
    return [lista_to_show_ecuatii, stoichiometry_in_tex(stoicm)]


# TODO dati seama cate are asta in comun cu get_reaction_meta sa nu mai fie atatea functii
def crn2antimony(filename: str):
    """
    :session: the global object session for the current user
    :param filename:
        Name of the file whose contents will be transformed in a full Antimony syntax
         network with species, constants and everything, as opposed to
         "crn2antimony_definitions" which only does that for the reactions
    :return:
    """
    ## filename = 'crn_a_b_c.txt'
    #  filename = 'crn.txt'

    krates = []  # lista cu vitezele de reactie

    tel, specii = crn2antimony_definitions(0, krates)
    kcont = len(krates)

    # THE VALUE FOR THE CONSTANTS REACTIONS!!!
    reaction_constants = session.get('react_constants')
    if reaction_constants:
        val_k = reaction_constants
    else:
        val_k = [0] * kcont
    print('constArrayu cu cate kuri adica reactii sunt')
    print(reaction_constants, kcont)
    # pt fiecare reactie face k1 = valoarea;
    #                k2 = valoarea;
    for k in range(kcont):
        tel = tel + 'k' + str(k + 1) + ' = ' + str(val_k[k]) + ';\n'  # era: str(valk[k-1])

    tel = tel + '\n'

    # THE VALUE FOR THE INITIAL CONDITIONS!!!
    init_vals = session.get('init_vals')
    if not init_vals:
        init_vals = [0] * len(specii)

    for i in range(len(specii)):
        tel = tel + specii[i] + ' = ' + str(init_vals[i]) + ';\n'
        # aici pune A = ce valoare a dat useru in UI

    tel = tel + '\n'

    print('aici stringu final')
    return tel


def crn2antimony_definitions(kcont=0, krates=None):
    reactii_individuale = open(save_crn_filepath_location, 'r').readlines()

    krates = [] if krates is None else krates
    for reactie in reactii_individuale:  # gaseste vitezele de reactie
        kcont = kcont + 1  # de la 1 la cate reactii sunt
        krate = 'k' + str(kcont)  # incepe cu 1:  k1 k2 k3

        reactii_stanga = reactie.split('->')[0].split('+')
        # scoate coeficientul din fata de la fiecare specie

        # scoate coeficientul din fata de la fiecare specie
        for specie in reactii_stanga:
            if specie != '0':
                coeficient = re.findall(r'^[0-9]*', specie)[0]  # este sir vid '' daca nu gaseste
                subtanta = re.findall(r'[a-zA-Z]+.*', specie)[0]

                cnt = 0
                if coeficient == '':
                    cnt = 1
                else:
                    cnt = int(coeficient)

                print('countu de coefieicent e')
                print(cnt)
                for i in range(cnt):
                    krate = krate + '*' + subtanta  # adauga *A*A*A de cata ori era, ex: A3. edit viktorashi: darr astsa face daca e 3A nu A3
                    # daca e 3ABC devine k1*ABC*ABC*ABC
                    # daca e ABC3 devine k1*ABC3
                    # daca e 3ABC + 3C -> 2C
                    #       3C -> 2A devine [ k1*ABC*ABC*ABC*3C , k2*C*C*C ]
        krates.append(krate)

    print('krates: ')
    print(krates)

    specii, reacts = get_reaction_meta(reactii_individuale)

    ## --- creeaza stringul de Tellurium

    tel = ''
    ii = 0
    for reactie in reacts:
        tel = tel + reactie + '; ' + krates[ii] + '\n'
        ii = ii + 1

    tel = tel + '\n'

    return tel, specii


def stoichiometry_in_tex(stoichiometric_matrix):
    """

    :param stoichiometric_matrix: type: roadrunner._roadrunner.NamedArray
        the value returned by road_runner.getFullStoichiometryMatrix()
    :return:
        the stoichiometric matrix in LaTeX form to be displayed in the webpage
    Example:
        For the equation 2 H2 + O2 -> 2 H2O
        would result the parameter stoichiometric_matrix.array =
                    _J1
                   H2 [[-2],
                   O2 [-1],
                   H2O [2]]

        which would need to become
        $$
         \matrix{
              H2 & -2 \cr
              O2 & -1 \cr
              H2O & 2 \cr}
        $$
    """

    # begin
    tex = ("$$\n"
           "\matrix{ \n")

    # append the equation names on the first (header) line
    # for i in range(no_equations):
    #     tex = tex + '& J_' + str(i+1)

    # new matrix row
    tex = tex + '\cr '

    # now completing each line, with the name of the species as the headers for the lines
    species_names = stoichiometric_matrix.rownames
    for species in species_names:
        # the header of the line
        tex = tex + species
        values_in_each_eq = stoichiometric_matrix[species]
        # truncate to an integer if it ends in .0 for each digit
        values_in_each_eq = [int(value) if value.is_integer() else value for value in values_in_each_eq]
        # the value that species has in each equation
        for value in values_in_each_eq:
            if value >= 0:
                tex = tex + '&\ ' + str(value)
            else:
                tex = tex + '& ' + str(value)
        # new row in matrix
        tex = tex + '\cr '

    # aaand end it
    tex = tex + '} \n $$'

    return tex


def draw_diagram():
    rr = te.loada(crn2antimony(save_crn_filepath_location))
    rr.draw(path='open_control/static/diagram.svg', width=200)


def draw_phase_portrait():
    """
    Draws the phase diagram to open_control/static/phase_portrait.svg
        2D if only 2 species are selected
        3D if 3 species are selected
    """

    ##>>>>>>>INIT PART
    select = session.get('select')
    end_time = session.get('end_time')
    start_time = session.get('start_time')
    titlu = session.get('titlu')
    x_titlu = session.get('x_titlu')
    y_titlu = session.get('y_titlu')

    print(select)
    print(end_time)

    # Am modificat aici !!! ------------------------------------------------
    import matplotlib

    matplotlib.use(
        'agg')  # agg e un backend cu care poti sa plotuiesti in fisiere direct, fara sa vezi tu in terminal sau cv
    te.setDefaultPlottingEngine('matplotlib')  # o sa foloseasca backendu acela bun din matplot

    antimony_code = crn2antimony(select)  # tellurium output !!!
    print('coadele de antiomony')
    print(antimony_code)
    print('------pana aici-------------')
    road_runner = te.loada(antimony_code)

    # sa poata plotui fara sa printeze pe ecran ceva, doar in fisier
    print(antimony_code)

    # matricea stoichiometrica

    # numele ratelor de reactie
    k_s = road_runner.getGlobalParameterIds()
    print(k_s)

    # valorile retelor de reactie
    reation_rates = road_runner.getReactionRates()
    print(reation_rates)
    print(select)
    print(start_time)
    print(end_time)
    print(titlu)
    print(x_titlu)
    print(y_titlu)
    ##<<<<<<<<<<INIT PART

    checked_species = session.get('checked_species')
    checked_species_count = len(checked_species)

    number_of_points = 1000
    # da return la rezultate si pot fi folosite rezultatele din simulare pentru plot()
    m = road_runner.simulate(start=float(start_time), end=float(end_time), points=number_of_points,
                             selections=checked_species)

    save_graph_to_file = 'open_control/static/phase_portrait.svg'
    if checked_species_count == 2:

        road_runner.plot(xlabel=checked_species[0], ylabel=checked_species[1], figsize=(9, 6), title=str(titlu),
                         savefig=save_graph_to_file)
    elif checked_species_count == 3:
        import matplotlib.pyplot as plt

        ax = plt.figure().add_subplot(projection='3d')
        ax.plot(m[:, 1], m[:, 2], m[:, 0], label=str(titlu))
        ax.legend()
        ax.set_xlabel(checked_species[0])
        ax.set_ylabel(checked_species[1])
        ax.set_zlabel(checked_species[2])
        ax.view_init(elev=20., azim=-35, roll=0)
        plt.savefig(save_graph_to_file)
    else:
        print('prea multe sau prea putine specii aici maa')
