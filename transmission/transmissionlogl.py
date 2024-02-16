import numpy as np
import pandas as pd
from dataclasses import dataclass

@dataclass(frozen=True)
class SimpleBirthDeathModel():
    c_pest: float

    def p_inf(self, dose):
        return 1 - np.exp(-1 * self.c_pest * dose)

@dataclass(frozen=True)
class BirthDeathFractionUnproductiveModel():
    proportion: float
    c_pest: float

    def p_inf(self, dose):
        return self.proportion * (1 - np.exp(-1 * self.c_pest * dose))

@dataclass(frozen=True)
class GammaModel():
    mean: float
    variance: float

    def p_inf(self, dose):
        # see Noecker 2015
        return 1 - (self.mean / (self.mean + self.variance * dose))**(self.mean**2/self.variance)

class Fitter:
    @staticmethod
    def logl(data, model):
        p_inf = model.p_inf(data.dose)
        p_trans = 1 - (1 - p_inf) ** (data.duration * data.dose_frequency)
        nlogl = -1 * np.sum(data.success * np.log(p_trans)) - np.sum((data.number - data.success) * data.duration * data.dose_frequency * np.log(1 - p_inf))

        return nlogl

model_klasses = {
    'bdsim': SimpleBirthDeathModel,
    'bdmax': BirthDeathFractionUnproductiveModel,
    'gamma': GammaModel,
}