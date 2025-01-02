import tellurium as te
rr = te.loada('''
    A -> B; k1*A
    B -> C; k2*B
    A = 10; B = 0; C = 20;
    k1 = 0.1; k2 = 0.2;
''')
rr.simulate(0, 10, 100, ['A', 'B'])
rr.plot(xlabel='A', ylabel = 'B', savefig='phase-portr.svg')