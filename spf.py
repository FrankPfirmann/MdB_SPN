from spn.structure.leaves.parametric.Parametric import Categorical
from spn.structure.Base import Sum, Product
from spn.structure.Base import assign_ids, rebuild_scopes_bottom_up
from spn.io.Graphics import plot_spn
import os
from spn.algorithms.Marginalization import marginalize
import numpy as np
from spn.algorithms.Inference import log_likelihood
from spn.gpu.TensorFlow import optimize_tf
from numpy.random.mtrand import RandomState
from spn.algorithms.Sampling import sample_instances
from spn.algorithms.LearningWrappers import learn_parametric, learn_classifier
from spn.structure.leaves.parametric.Parametric import Categorical, Gaussian
from spn.structure.Base import Context
from spn.algorithms.MPE import mpe

test_data = np.array([1.0, 0.0]).reshape(-1, 2)
print(test_data)

os.environ["PATH"] += os.pathsep + 'C:/Programme/Graphviz/bin/'

p0 = Product(children=[Categorical(p=[0.9, 0.1], scope=0), Categorical(p=[0.2, 0.8], scope=1)])
p1 = Product(children=[Categorical(p=[0.7, 0.3], scope=0), Categorical(p=[0.1, 0.9], scope=1)])
spn = Sum(weights=[0.2, 0.8], children=[p0, p1])
assign_ids(spn)
rebuild_scopes_bottom_up(spn)
spn_marg = marginalize(spn, [1])

plot_spn(spn, 'basicspn.png')
ll = log_likelihood(spn, test_data)
optimized_spn = optimize_tf(spn, test_data)
lloptimized = log_likelihood(optimized_spn, test_data)

np.random.seed(123)
train_data = np.c_[np.r_[np.random.normal(5, 1, (500, 2)), np.random.normal(10, 1, (500, 2))],
                   np.r_[np.zeros((500, 1)), np.ones((500, 1))]]
print(train_data)
exit()
spn_classification = learn_classifier(train_data,
                       Context(parametric_types=[Gaussian, Categorical]).add_domains(train_data),
                       learn_parametric, 1)
test_classification = np.array([4.0, np.nan, 14.0, np.nan]).reshape(-1, 2)

print(sample_instances(spn, np.array([1, np.nan] *10).reshape(-1, 2), RandomState(123)))
print(mpe(spn_classification, test_classification))
print(ll, np.exp(ll))
print(lloptimized, np.exp(lloptimized))
