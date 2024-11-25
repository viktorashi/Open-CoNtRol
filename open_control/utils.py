import tellurium as te
import re
from flask import  render_template
from typing import List, Tuple, Dict

def parse_reaction(reaction: str) -> Tuple[List[str], List[str], str]:
    """Parse a single reaction line into reactants, products, and rate law."""
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
    """Parse a species term to get species name and its coefficient."""
    match = re.match(r'^(\d+)?([A-Za-z]\w*)$', term.strip())
    if not match:
        raise ValueError(f"Invalid species term: {term}")

    coef, species = match.groups()
    coef = int(coef) if coef else 1
    return species, coef

#This probably has so much functionality that I can reuse in the project and delete the old stuff ong
class AntimonyConverter:
    def __init__(self):
        self.species = []
        self.species_to_index = {}

    def collect_species(self, reactions: List[str]):
        """Collect all unique species and assign them indices."""
        all_species = set()
        for reaction in reactions:
            reactants, products, _ = parse_reaction(reaction)
            for term in reactants + products:
                species, _ = parse_species_term(term)
                all_species.add(species)

        self.species = sorted(list(all_species))
        self.species_to_index = {species: f"x_{i + 1}" for i, species in enumerate(self.species)}

    def convert_rate_law(self, rate_law: str, species_powers: Dict[str, int]) -> str:
        """Convert species names in rate law to x_i notation with powers."""
        # First convert all species to their x_i notation with appropriate powers
        for species, power in species_powers.items():
            index = self.species_to_index[species]
            if power > 1:
                rate_law = re.sub(rf'\b{species}\b(?:\*{species}\b)*', f"{index}^{power}(t)", rate_law)
            else:
                rate_law = re.sub(rf'\b{species}\b', f"{index}(t)", rate_law)
        return rate_law

    def generate_differential_equations(self, reactions: List[str]) -> Dict[str, str]:
        """Generate differential equations from list of reactions."""
        self.collect_species(reactions)
        species_terms = {species: [] for species in self.species}

        for reaction in reactions:
            reactants, products, rate = parse_reaction(reaction)

            # Count species occurrences in reactants
            species_powers = {}
            for reactant in reactants:
                species, coef = parse_species_term(reactant)
                species_powers[species] = coef

            # Convert the rate law
            converted_rate = self.convert_rate_law(rate, species_powers)

            # Process reactants (negative terms)
            for reactant in reactants:
                species, _ = parse_species_term(reactant)
                term = f"-{converted_rate}"
                species_terms[species].append(term)

            # Process products (positive terms)
            for product in products:
                species, coef = parse_species_term(product)
                if coef > 1:
                    term = f"+{coef}\dot{converted_rate}"
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

        return equations

    def generate_tex_equations(self, equations: Dict[str, str]) -> List[str]:
        """Generate TeX formatted equations."""
        tex_equations = []
        for i, species in enumerate(self.species, 1):
            eqn = equations[species]
            tex_eqn = f"$$ x_{i}'(t) = {eqn} $$"
            tex_equations.append(tex_eqn)
        return tex_equations

def reactions_to_tellurium_format(filename : str) -> [str]:
    """
    :param filename: numele fisierului din care reactii sa le faci in format antimony
    :return reactii_individuale:
       converteste reactii <--> bidirectioanale in 2 catre dreapta ->
       inverseaza <-- in ->
       si --> devine ->
       practic scrie toate reactiile ca reactie cu sageata catre dreapta, si inlocuieste --> cu ->
       pt formatul antimony
       deci sa fie clar face asta DOAR cu reactiile iar functia "crn2tellurium"
       face un string complet de Antimony
    """

    filename = 'open_control/templates/metode_lucru/' + filename
    f = open( filename, 'rt')
    file_lines = f.readlines()
    # scapa de un <enter> la sfarsit
    lista_ecuatii : [] = list(map(lambda x: x.strip(), file_lines))

    # ---- inlocuirea sagetilor si rasucirea de ecuatii -----
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

    return list(map(lambda x: x.replace(" ", ""), reactii_individuale))

def save_reactions_file(req):
    """
    :param req:
         The Flask request object containing form data.
                    Expects form data with 'ecuatiiCount' (number of reactions) and for each reaction:
                    - 'ec_<index>_left': Left side of the reaction.
                    - 'ec_<index>_dir': Direction of the reaction. left := <-- ; right := --> ; both := <-->
                    - 'ec_<index>_right': Right side of the reaction.

    Saves to open_control/templates/metode_lucru/crn.txt file in the format specified above

    :return: None
    """
    ecuatii_count = int(req.form.get('ecuatiiCount'))

    the_file = open("open_control/templates/metode_lucru/crn.txt", "w")

    for index in range(1,ecuatii_count+1):
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

#asa ii da overwrite la open_control/templates/metode_lucru/crn.txt
        the_file.write(ecuatie_finala)
        the_file.write("\n")

    the_file.close()
#TODO dati seama cate are in comut cu crn2antomony ca sa nu mai fie atata cod duplicat

def get_reaction_meta(session , reactii_individuale : [str]) -> [[str],[str]] :
    """
    :param session: the global object session for the current user
    :param reactii_individuale: The reactions in Antimony format
    :return: The list of unique species and the reactions in Antimony format
    """
    specii :[str] = []

    for reactie in reactii_individuale:  # gaseste speciile
        ats = reactie.replace('->', '+').split('+') #transforma si 4A + 5B -> C in 4A + 5B + C si le da split la +

        #scoate coeficientul din fata de la fiecare specie
        for ato in ats:
            if ato != '0':  # sa nu fie zero barat
                spec = re.findall(r'[a-zA-Z]+.*', ato)[0]
                specii.append(spec)  # in place

    ## end -- for x in s

    specii = list(set(specii)) #removes duplicates
    specii.sort()  # alfabetic
    session['specii'] = specii

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

    return specii, reacts

def get_numerical_analysis(antimony_code):
    """
    :param antimony_code: what is sounds like: https://tellurium.readthedocs.io/en/latest/antimony.html#introduction-and-basics
    :return: stoichiometry matrix along with the differential equations (in LaTeX form) used to describe the system.

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

    #TODO: make it so that it detects when the user hasn't even initialised the values themselves
    # (preferably in the frontend to reduce the load over here) and just delete the parameter definitions from the code before submitting
    #orr just see if it throws the RuntimeError

    road_runner = 'lmao'
    antimony_code_with_init = ''
    try:
        road_runner = te.loada(antimony_code)
        #gets thrown if the user hasn't specified a value for the parameters specified
    except RuntimeError:
        # k1, k2 ... params need to be initialised for it to work, so we'll just initialise them all with 0
        param_initialisation = ''
        #double newline means the ned of a section in my format, the first section is the declaration part, and then we see how many lines are in that
        no_declaration_lines = len(antimony_code.split('\n\n')[0].split('\n'))

        antimony_code_with_init = antimony_code + '\r\n'
        for i in range(1, no_declaration_lines + 1):
            param_initialisation = param_initialisation + 'k' + str(i) + ' = 0 \r\n'

        antimony_code_with_init = antimony_code_with_init + param_initialisation
        road_runner = te.loada(antimony_code_with_init)


    #ok i done used claude for this cuz i got lazy https://claude.site/artifacts/bc895634-74fe-418b-bad2-f801907fc4ea
    # it did a surprisingly good job in correcting its bugs after several iterations

    converter = AntimonyConverter()

    reactions = antimony_code.split('\n')
    equations = converter.generate_differential_equations(reactions)
    tex_equations = converter.generate_tex_equations(equations)
    tex_equations = '\n'.join(tex_equations)

    species_to_index_mapping = converter.species_to_index

    stoich = road_runner.getFullStoichiometryMatrix()
    return [stoich,antimony_code, tex_equations, species_to_index_mapping ]

def create_figure(session ):
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

    antimony_code = crn2antimony(session, select)  #   tellurium output !!!

    print(select)
    print(end_time)

    # Am modificat aici !!! ------------------------------------------------
    import matplotlib
    matplotlib.use('agg') #agg e un backend cu care poti sa plotuiesti in fisiere direct
    te.setDefaultPlottingEngine('matplotlib') #o sa foloseasca backendu acela bun din matplot

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

    number_of_points = 1000
    road_runner.simulate(start = float(start_time), end = float(end_time), points=number_of_points) #da return la rezultate

    print(select)
    print(start_time)
    print(end_time)
    print(titlu)
    print(x_titlu)
    print(y_titlu)

    road_runner.plot(xlabel = x_titlu , ylabel = y_titlu, figsize = (9,6), title = str(titlu), savefig = 'open_control/static/graphic.svg')

    #zici ca-i naming convention TJ Miles
    listaToShowEcuatii = antimony_code.split("\n")

    stoicm = road_runner.getFullStoichiometryMatrix()
    print('asta stoichiometrica')
    print(stoicm)
    print(type(stoicm))

    # "template not found" error keeps popping up for some reason (it works lol)
    return [render_template("home.html"), listaToShowEcuatii, stoichiometry_in_tex(stoicm)]

#TODO dati seama cate are asta in comun cu get_reaction_meta sa nu mai fie atatea functii
def crn2antimony(session , filename:str):
    """
    :param session: the global object session for the current user
    :param filename:
        Name of the file whose contents will be transformed in a full Antimony syntax
         network with species, constants and everything, as opposed to
         "reactions_to_tellurium_format" which only does that for the reactions
    :return:
    """
    ## filename = 'crn_a_b_c.txt'
    #  filename = 'crn.txt'

    reactii_individuale = reactions_to_tellurium_format(filename)

    kcont = 0  # cate reactii sunt
    krates = []  # lista cu vitezele de reactie

    for reactie in reactii_individuale:  # gaseste vitezele de reactie
        kcont = kcont + 1  # de la 1 la cate reactii sunt
        krate = 'k' + str(kcont) #incepe cu 1:  k1 k2 k3

        reactii_stanga = reactie.split('->')[0].split('+')
        #scoate coeficientul din fata de la fiecare specie

        #scoate coeficientul din fata de la fiecare specie

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
                    krate = krate + '\dot' + subtanta  # adauga *A*A*A de cata ori era, ex: A3. edit viktorashi: darr astsa face daca e 3A nu A3
                    #daca e 3ABC devine k1*ABC*ABC*ABC
                    #daca e ABC3 devine k1*ABC3
                    #daca e 3ABC + 3C -> 2C
                    #       3C -> 2A devine [ k1*ABC*ABC*ABC*3C , k2*C*C*C ]
        krates.append(krate)

    print('krates: ')
    print(krates)
    specii, reacts = get_reaction_meta(session, reactii_individuale)

    ## --- creeaza stringul de Tellurium

    tel = ''
    ii = 0
    for reactie in reacts:
        tel = tel + reactie + '; ' + krates[ii] + '\n'
        ii = ii + 1

    tel = tel + '\n'

    # THE VALUE FOR THE CONSTANTS REACTIONS!!!
    reaction_constants = session.get('react_constants')
    val_k = reaction_constants
    print('constArrayu cu cate kuri adica reactii sunt')
    print(reaction_constants, kcont)
    #pt fiecare reactie face k1 = valoarea;
    #                k2 = valoarea;
    for k in range(kcont):
        tel = tel + 'k' + str(k + 1) + ' = ' + str(val_k[k]) + ';\n'  # era: str(valk[k-1])

    tel = tel + '\n'

    # THE VALUE FOR THE INITIAL CONDITIONS!!!
    init_vals = session.get('init_vals')
    for i in range(len(specii)):
        tel = tel + specii[i] + ' = ' + str(init_vals[i]) + ';\n'
        #aici pune A = ce valoare a dat useru in UI

    tel = tel + '\n'

    print('aici stringu final')
    return tel

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

    no_species , no_equations = stoichiometric_matrix.shape

    #begin
    tex = ("$$\n"
            "\matrix{ \n")

    #append the equation names on the first (header) line
    # for i in range(no_equations):
    #     tex = tex + '& J_' + str(i+1)

    #new matrix row
    tex = tex + '\cr '

    #now completing each line, with the name of the species as the headers for the lines
    species_names = stoichiometric_matrix.rownames
    for species in species_names:
        #the header of the line
        tex = tex + species
        values_in_each_eq = stoichiometric_matrix[species]
        #the value that species has in each equation
        for value in values_in_each_eq:
            if value >= 0:
                tex = tex + '&\ ' + str(value)
            else :
                tex = tex + '& ' + str(value)
        #new row in matrix
        tex = tex + '\cr '

    #aaand end it
    tex = tex + '} \n $$'

    return tex

