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

    def run_simulation(self, is_partial_hedge, num_of_runs = 10000):
        """
        Tick off the Monte Carlos simulation

        :param is_partial_hedge: boolean value, whether to use a partial hedge
        :param num_of_runs: The number of simulation to run
        :return:
        """

        # compute the vol for each time step
        step_vol = self._annual_vol / sqrt(self._trading_days_per_year * 24 * 3600 / self._simulate_interval)

        pnl_list = []

        # loop through all paths
        for i in range(0, num_of_runs):
            # Keep track of total PnL of the current simulation path
            tot_pnl = 0

            # Keep track of total position of the current simulation path
            tot_pos = 0

            # keep track of the current spot rate
            spot_rate = self._spot_rate

            for i in range(0, self._tot_steps):
                # generate a uniform random number in (0,1)
                p = random.uniform()

                if i > 0:
                    # simulate a standard normal variable
                    z = random.normal()

                    # compute the change in spot rate
                    # we assume spot has the process: ds = sigma * dw
                    d_spot_rate = step_vol * z * sqrt(self._simulate_interval)

                    tot_pnl += d_spot_rate * tot_pos

                if (p < self._trade_prob):
                    tot_pos += self._simulate_client_trade()

                    tot_pnl += self._client_spread / 2.

                    # Check if the total position exceed the delta limit
                    if abs(tot_pos) > self._delta_limit_abs:
                        tot_pnl += self._simulate_dealer_trade(tot_pos, is_partial_hedge)

                        if is_partial_hedge:
                            tot_pos = sign(tot_pos) * self._delta_limit_abs
                        else:
                            tot_pos = 0

            pnl_list.append(tot_pnl)

        pnl_arr = array(pnl_list)

        std = pnl_arr.std()

        mean = pnl_arr.mean()

        print 'Sharpe ratio is {0}'.format(mean / std)

        #print pnl_arr[:20]

    def _simulate_dealer_trade(self, tot_pos, is_partial_hedge):
        """
        Compute the pnl of the dealer trade

        :param tot_pos:
        :return:
        """

        if is_partial_hedge:
            pnl = -0.5 * (abs(tot_pos) - self._delta_limit_abs) * self._dealer_spread
        else:
            pnl = -0.5 * abs(tot_pos) * self._dealer_spread

        return pnl


    def _simulate_client_trade(self):
        """

        Compute the PnL of the current trade
        :return:
        """

        # generate a uniform random number in (0,1) to determine the trade size
        p = random.uniform()

        trade_size = self._unit_size

        if p <= 0.5:
            trade_size *= -1

        return trade_size


def main():
    """

    Test for FX Hedge engine

    First two runs are for the normal version

    The last two runs are for the vectoried version
    :return:
    """
    engine = hedging_engine()

    is_partial_hedge = False

    engine.run_simulation(is_partial_hedge)

    is_partial_hedge = True

    engine.run_simulation(is_partial_hedge)

if __name__ == '__main__':
    main()
