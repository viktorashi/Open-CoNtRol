import tellurium as te

r = te.loada("""
    S1 -> S5; k1*S1;
    k1 = 0.1; S1 = 40; S2 = 0.0;
""")
try:
    import pygraphviz

    r.draw(savefig='file.png')
except ImportError:
    pass
