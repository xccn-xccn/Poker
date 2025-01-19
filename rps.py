import numpy as np
from numpy.random import choice
from time import time


class RPSTrainer:
    def __init__(self):

        self.NUM_ACTIONS = 3
        self.possible_actions = np.arange(self.NUM_ACTIONS)
        # Order left to right, and up to down is Rock, Paper, Scissors
        self.actionUtility = np.array([
                    [0, -1, 1],
                    [1, 0, -1],
                    [-1, 1, 0]
                ])
        self.regret_sum = np.zeros(self.NUM_ACTIONS)
        self.strategy_sum = np.zeros(self.NUM_ACTIONS)

        self.opponent_regret_sum = np.zeros(self.NUM_ACTIONS)
        self.opponent_strategy_sum = np.zeros(self.NUM_ACTIONS)

    def get_strategy(self, regret_sum, i):
        new_sum = np.clip(regret_sum, a_min=0, a_max=None)
        normalizing_sum = np.sum(new_sum)

        # if i % 500 == 0:
            # print(new_sum, normalizing_sum)
        if normalizing_sum > 0:
            new_sum /= normalizing_sum
        else:
            new_sum = np.repeat(1/self.NUM_ACTIONS, self.NUM_ACTIONS)

        # if i % 500 == 0:

            print(new_sum)
        return new_sum

    def get_average_strategy(self, strategy_sum):
        # print(strategy_sum)
        average_strategy = [0, 0, 0]
        normalizing_sum = sum(strategy_sum)
        for a in range(self.NUM_ACTIONS):
            if normalizing_sum > 0:
                average_strategy[a] = strategy_sum[a] / normalizing_sum
            else:
                average_strategy[a] = 1.0 / self.NUM_ACTIONS
        return average_strategy

    def get_action(self, strategy):
        return choice(self.possible_actions, p=strategy)

    def get_reward(self, my_action, opponent_action):
        return self.actionUtility[my_action, opponent_action]

    def train(self, iterations):

        for i in range(iterations):
            strategy = self.get_strategy(self.regret_sum, i)
            opp_strategy = self.get_strategy(self.opponent_regret_sum, i)
            self.strategy_sum += strategy
            self.opponent_strategy_sum += opp_strategy

            opponent_action = self.get_action(opp_strategy)
            my_action = self.get_action(strategy)

            my_reward = self.get_reward(my_action, opponent_action)
            opp_reward = self.get_reward(opponent_action, my_action)

            for a in range(self.NUM_ACTIONS):
                my_regret = self.get_reward(a, opponent_action) - my_reward
                opp_regret = self.get_reward(a, my_action) - opp_reward
                self.regret_sum[a] += my_regret
                self.opponent_regret_sum[a] += opp_regret

            # if i % 500 == 0:
                # print('info', self.regret_sum, strategy, self.strategy_sum)
        

def main():
    start = time()
    trainer = RPSTrainer()
    trainer.train(100_000)
    target_policy = trainer.get_average_strategy(trainer.strategy_sum)
    opp_target_policy = trainer.get_average_strategy(trainer.opponent_strategy_sum)
    print('player 1 policy: %s' % target_policy)
    print('player 2 policy: %s' % opp_target_policy)
    print(f"Time {(time() - start) * 1000} ms")


if __name__ == "__main__":
    main()