# import tellurium as te


# r = te.loada('''
# model feedback()
#    // Reactions:http://localhost:8888/notebooks/core/tellurium_export.ipynb#
#    J0: $X0 -> S1; (VM1 * (X0 - S1/Keq1))/(1 + X0 + S1 +   S4^h);
#    J1: S1 -> S2; (10 * S1 - 2 * S2) / (1 + S1 + S2);
#    J2: S2 -> S3; (10 * S2 - 2 * S3) / (1 + S2 + S3);
#    J3: S3 -> S4; (10 * S3 - 2 * S4) / (1 + S3 + S4);
#    J4: S4 -> $X1; (V4 * S4) / (KS4 + S4);

#   // Species initializations:
#   S1 = 0; S2 = 0; S3 = 0;
#   S4 = 0; X0 = 10; X1 = 0;

#   // Variable initialization:
#   VM1 = 10; Keq1 = 10; h = 10; V4 = 2.5; KS4 = 0.5;
# end''')

# # simulate using variable step size
# r.integrator.setValue('variable_step_size', True)
# s = r.simulate(0, 50)
# # draw the diagram
# r.draw(width=200)
# # # and the plot
# # r.plot(s, title="Feedback Oscillations", ylabel="concentration", alpha=0.9);
from IPython.display import display, Image

path1 = 'fig.png'

display(Image(filename=path1))

