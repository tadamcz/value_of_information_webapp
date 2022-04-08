import scipy
from value_of_information import Simulation

prior = scipy.stats.norm(1, 1)
study_sample_size = 100
population_std_dev = 20
bar = 5
simulation = Simulation(
    prior=prior,
    study_sample_size=study_sample_size,
    population_std_dev=population_std_dev,
    bar=bar)
