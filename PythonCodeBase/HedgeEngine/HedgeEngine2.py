from numpy import *

class hedging_engine(object):
    """
    Class for hedging engine

    Interesting to determine what the best hedging approach is:
    hedge to the hedge of the delta limit, or hedge all the way to zero,
    or something in between?
    """

    def __init__(self, spot_rate = 1, annual_vol = 0.1, poisson_freq = 1.,
                 client_spread = 0.0001, dealer_spread = 0.0002,
                  unit_size = 1., delta_limit_abs = 3., tot_steps = 500):
        """

        :param spot_rate: The beginning spot rate of each simuation path
        :param annual_vol: The annualized vol of the spot rate
        :param client_spread: The bid ask spread of the client
        :param dealer_spread: The bid ask spread of the dealer
        :param poisson_freq: the lambda in the Poisson distribution. The unit is in second.
        :param simulate_interval: The time interval of the simulation
        :param tot_steps: The total length of time of the simulation
        :param unit_size: The unit size of each trade
        :param delta_limit_abs: the threshold of the delta, which is used as the threshold for hedging
        :return:
        """

        # Total number of trading days per year
        self._trading_days_per_year = 260

        self._spot_rate = spot_rate

        self._annual_vol = annual_vol

        self._client_spread = client_spread

        self._dealer_spread = dealer_spread

        self._simulate_interval = 0.1 / poisson_freq

        self._tot_steps = tot_steps

        # Probability of (at least one) trade during a time interval
        self._trade_prob = 1 - exp(-1. * poisson_freq * self._simulate_interval)

        self._unit_size = unit_size

        # store the total PnL of the whole simulation
        self._tot_pnl = 0

        self._delta_limit_abs = delta_limit_abs

    def run_simulation_vectorized(self, is_partial_hedge, num_of_runs = 10000):
        """
        Tick off the Monte Carlos simulation

        :param is_partial_hedge: boolean value, whether to use a partial hedge
        :param num_of_runs: The number of simulation to run
        :return:
        """

        # compute the vol for each time step
        step_vol = self._annual_vol / sqrt(self._trading_days_per_year * 24 * 3600 / self._simulate_interval)

        # Keep track of total PnL of the current simulation path
        tot_pnl = array([0.] * num_of_runs)

        # Keep track of total position of the current simulation path
        tot_pos = array([0.] * num_of_runs)

        # keep track of the current spot rate
        spot_rate = array([self._spot_rate] * num_of_runs)

        for i in range(0, self._tot_steps):
            # generate a uniform random number in (0,1)
            p = random.uniform(size = num_of_runs)

            if i > 0:
                # simulate a standard normal variable
                z = random.normal(size = num_of_runs)

                # compute the change in spot rate
                # we assume spot has the process: ds = sigma * dw
                d_spot_rate = step_vol * z #* sqrt(self._simulate_interval)

                tot_pnl += d_spot_rate * tot_pos

            tot_pos[p < self._trade_prob] += self._simulate_client_trade_vectorized(num_of_runs)[p < self._trade_prob]

            tot_pnl[p < self._trade_prob] += self._client_spread / 2.

            tot_pnl += self._simulate_dealer_trade_vectorized(tot_pos, is_partial_hedge, num_of_runs)

            # Check if the total position exceed the delta limit and update the position accordingly
            if is_partial_hedge:
                tot_pos[abs(tot_pos) > self._delta_limit_abs] = \
                    sign(tot_pos[abs(tot_pos) > self._delta_limit_abs]) * self._delta_limit_abs
            else:
                tot_pos[abs(tot_pos) > self._delta_limit_abs] = 0

        std = tot_pnl.std()

        mean = tot_pnl.mean()

        print 'Sharpe ratio is {0}'.format(mean / std)

        #print tot_pnl[:20]

        #print tot_pos[:50]


    def _simulate_client_trade_vectorized(self, num_of_paths):
        trade_sign = random.uniform(size = num_of_paths)

        trade_size = array([self._unit_size] * num_of_paths)

        trade_size[trade_sign < 0.5] = -1 * self._unit_size

        return trade_size

    def _simulate_dealer_trade_vectorized(self, tot_pos, is_partial_hedge, num_of_paths):
        """
        Compute the pnl of the dealer trade

        :param tot_pos:
        :return:
        """

        # Intialize array
        pnl = array([0.] * num_of_paths)

        if is_partial_hedge:
            pnl[abs(tot_pos) > self._delta_limit_abs] = -0.5 * (abs(tot_pos[abs(tot_pos) > self._delta_limit_abs])
                        - self._delta_limit_abs) * self._dealer_spread
        else:
            pnl[abs(tot_pos) > self._delta_limit_abs] = -0.5 * abs(tot_pos[abs(tot_pos) > self._delta_limit_abs])\
                                                        * self._dealer_spread

        return pnl


def main():
    """

    Test for FX Hedge engine

    First two runs are for the normal version

    The last two runs are for the vectoried version
    :return:
    """
    engine = hedging_engine()

    is_partial_hedge = False

    engine.run_simulation_vectorized(is_partial_hedge, num_of_runs = 10000)

    is_partial_hedge = True

    engine.run_simulation_vectorized(is_partial_hedge)

if __name__ == '__main__':
    main()

