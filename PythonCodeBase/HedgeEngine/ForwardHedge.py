from numpy import *

# Enum for the type of hedge to be used in the simulation
class SimulatiionType:
    Triangle = 1
    Factor = 2
    NoHedge = 3

class ForwardHedge(object):
    """
    class fpr Forward hedging
    """

    def __init__(self, spot = 1., q = 0.03, T1 = 0.25, T2 = 1., sigma1 = 0.01
                 ,sigma2 = 0.008, beta1 = 0.5, beta2 = 0.1, rho = -0.4):
        """
        Constructor of the class

        :param spot: The beginning spot rate
        :param q: The interest rate of the asset currency
        :param T1: The first benchmark date
        :param T2: The second benchmark date
        :param sigma1: The sigma of the first factor
        :param sigma2: The sigma of the second factor
        :param beta1: The beta of the first factor
        :param beta2: The beta of the second factor
        :param rho: The correlation between factors
        :return:
        """

        self._spot = spot

        self._q = q

        self._T1 = T1

        self._T2 = T2

        self._sigma1 = sigma1

        self._sigma2 = sigma2

        self._beta1 = beta1

        self._beta2 = beta2

        self._rho = rho


    def run_simulation(self, T, hedge_type, d_t = 0.001, num_of_runs = 10000):
        """

        :param T:
        :param SimulatiionType:
        :param d_t:
        :param num_of_runs:
        :return:
        """

        current_step = d_t

        tot_pnl = array([0.] * num_of_runs)

        # The beginning fair forward price
        K = self._spot * exp(-1. * self._q * T)

        # Keep track of the interest rate of the asset currency
        Q = array([self._q] * num_of_runs)

        cnt = 0

        while (current_step < T + d_t / 2.):
            z1 = random.standard_normal(size = num_of_runs)

            z2 = random.standard_normal(size = num_of_runs)

            z2 =  z1 * self._rho +  z2 * sqrt(1 - self._rho ** 2)

            d_q = self._sigma1 * exp(-1. * self._beta1 * T) * sqrt(d_t) * z1 + \
                  self._sigma2 * exp(-1. * self._beta2 * T) * sqrt(d_t) * z2

            Q += d_q

            F = self._spot * exp(-1. * Q * (T - current_step))

            current_step += d_t

            cnt += 1

        current_step -= d_t

        print cnt

        print current_step

        print T

        print current_step - T

        print self._spot

        print -1. * Q * (T - current_step)

        print exp(-1. * Q * (T - current_step))

        tot_pnl += F - K

        std = tot_pnl.std()

        mean = tot_pnl.mean()

        print 'Mean is {0}'.format(mean)

        print 'Standard deviation is {0}'.format(std)

        print 'Sharpe ratio is {0}'.format(mean / std)

        print tot_pnl[tot_pnl <= 0]



if __name__ == '__main__':
    engine = ForwardHedge()

    T = 1.

    engine.run_simulation(T, SimulatiionType.NoHedge)