use itertools::Itertools;
// use rand::distributions::WeightedIndex;
// use rand::prelude::*;
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::time::Instant;

#[derive(Clone)]
struct Node {
    regrets: [f64; 2],  //current regrets to create strategy
    strategy: [f64; 2], //current strategy
    // strategy_p: Vec<f64>,   //strategy normalised
    strategy_sum: [f64; 2], //sum of the strategies to work out average strategy
    reach_pr: f64,          //reach probability of this node on the current iteration
}

struct Kuhn {
    node_map: HashMap<String, Node>,
    history: String,
    pot: [usize; 2],
    cards: [usize; 2],
    deck_size: usize,
}

fn make_new(n: usize) -> Kuhn {
    Kuhn {
        node_map: HashMap::new(),
        history: String::new(),
        pot: [0; 2],
        cards: [0, 0],
        deck_size: n,
    }
}

impl Kuhn {
    fn train(&mut self, iterations: usize) -> HashMap<String, Node> {
        for _ in 1..iterations {
            //0 - n non-inclusive where n is the number of cards in the deck
            for (c1, c2) in (0..self.deck_size).permutations(2).map(|v| (v[0], v[1])) {
                self.reset();
                self.cards = [c1, c2];
                self.cfr(0, [1.0, 1.0]);

                for node in self.node_map.values_mut() {
                    node.update();
                }
            }
        }
        self.node_map.clone()
    }

    fn reset(&mut self) {
        self.history = String::new();
        self.pot = [0; 2];
    }

    fn is_terminal(&self) -> bool {
        if self.history.len() > 3 {
            panic!("Invalid history {:?}", self.history)
        }

        self.history.len() >= 2 && &self.history[self.history.len() - 2..] != "pb"
    }

    fn get_reward(&self, c1: usize, c2: usize) -> isize {
        if &self.history[self.history.len() - 2..] == "bp" {
            return 1;
        }
        let reward = self.history[self.history.len() - 2..]
            .chars()
            .filter(|&c| c == 'b')
            .count()
            / 2
            + 1;
        if c1 > c2 {
            reward as isize
        } else {
            -(reward as isize)
        }
    }

    fn get_node(&mut self, cpi: usize) -> &mut Node {
        let key = self.cards[cpi].to_string() + &self.history;
        self.node_map.entry(key).or_insert(Node::new())
    }

    fn get_cards(&self, curr_player: usize) -> (usize, usize) {
        (self.cards[curr_player], self.cards[(curr_player + 1) % 2])
    }

    fn cfr(&mut self, curr_player: usize, reach_prob: [f64; 2]) -> f64 {
        let other_player = (curr_player + 1) % 2;
        let (card1, card2) = self.get_cards(curr_player);

        if self.is_terminal() {
            return self.get_reward(card1, card2) as f64;
        }

        let mut curr_regrets = [0.0; 2];
        let node_strategy = self.get_node(curr_player).strategy;
        for (i, act) in ['p', 'b'].iter().enumerate() {
            self.history.push(*act);
            // array of f64 has copy so no loss of ownership
            let mut new_prob = reach_prob; 
            new_prob[curr_player] *= node_strategy[i];

            curr_regrets[i] -= self.cfr(other_player, new_prob);
            //negative because it will get the reward of the other player (cards and cpi switch)

            self.history.pop(); 
        }

        let node: &mut Node = self.get_node(curr_player);

        let mut average_regret = 0f64;
        for (r, s) in curr_regrets.iter().zip(node.strategy.iter()) {
            average_regret += r * s; //normalised by s
        }

        node.reach_pr += reach_prob[curr_player];

        for i in 0..node.regrets.len() {
            node.regrets[i] += (curr_regrets[i] - average_regret) * reach_prob[other_player]
            //update regrets by (regret from this action - average regret) * probabilty of opponent making moves to reach this round
        }
        average_regret
    }

    fn best_response(
        &mut self,
        br_player: usize,
        curr_player: usize,
        br_card: usize,
        opp_reach: &[f64],
    ) -> f64 {
        //! Calculates the average chip gain per hand the best response player can achieve against the currrent strategy.
        //!
        //! br_player: Best response player.
        //! br_card: The best response player's card.
        //! opp_reach: A vector holding the probability of the opponnent having
        //! Each card at the current node (reach probability).

        // let n = self.deck_size;
        let other_player = (curr_player + 1) % 2;

        if self.is_terminal() {
            let mut ev = 0.0;
            for opp_card in 0..self.deck_size {
                if opp_reach[opp_card] == 0.0 {
                    continue;
                }
                // Set cards so get_cards/get_reward work correctly for curr_player's perspective
                if br_player == 0 {
                    self.cards = [br_card, opp_card];
                } else {
                    self.cards = [opp_card, br_card];
                }
                let (card1, card2) = self.get_cards(curr_player);
                ev += opp_reach[opp_card] * self.get_reward(card1, card2) as f64;
            }
            return ev;
        }

        let actions = ['p', 'b'];

        if curr_player == br_player {
            // BR player picks the single best action across ALL opponent cards simultaneously
            let mut best = f64::NEG_INFINITY;
            for a in actions {
                self.history.push(a);
                let v = -self.best_response(br_player, other_player, br_card, opp_reach);
                self.history.pop();
                best = best.max(v);
            }
            best
        } else {
            // opponent uses Nash strategy; update reach weight per opp_card per action
            let mut ev = 0.0;
            for (a_idx, &a) in actions.iter().enumerate() {
                let mut new_reach = opp_reach.to_vec();
                for opp_card in 0..self.deck_size {
                    if new_reach[opp_card] == 0.0 {
                        continue;
                    }
                    let key = opp_card.to_string() + &self.history;
                    let strat = self
                        .node_map
                        .get(&key)
                        .map(|nd| nd.get_final_strategy())
                        .unwrap_or([0.5, 0.5]);
                    new_reach[opp_card] *= strat[a_idx];
                }
                self.history.push(a);
                ev += -self.best_response(br_player, other_player, br_card, &new_reach);
                self.history.pop();
            }
            ev
        }
    }

    fn calc_exploit(&mut self) -> f64 {
        let n = self.deck_size;
        let mut br0 = 0.0;
        let mut br1 = 0.0;

        for br_card in 0..n {
            let mut opp_reach = vec![1.0; n];
            opp_reach[br_card] = 0.0; // opponent can't hold the same card

            self.reset();
            br0 += self.best_response(0, 0, br_card, &opp_reach.clone());

            self.reset();
            //subtract because this is taken from player 2's perspective
            br1 -= self.best_response(1, 0, br_card, &opp_reach.clone());
        }

        let norm = (n * (n - 1)) as f64;
        br0 /= norm;
        br1 /= norm;

        println!("{br0:.6}, {br1:.6}");
        (br0 + br1) / 2.0
    }
}

impl Node {
    fn new() -> Self {
        Node {
            regrets: [0.0, 0.0],
            strategy: [0.5; 2],
            strategy_sum: [0.0; 2],
            reach_pr: 0.0,
            // strategy_p: vec![1.0 / 3.0; 2],
            // reach_pr_sum: 0.0,
        }
    }
    fn update(&mut self) {
        for i in 0..self.strategy_sum.len() {
            self.strategy_sum[i] += self.reach_pr * self.strategy[i];
            //multiply by reach prob so when less likely to reach lower impact on strategy
        } //get the sum of strategies for the average strategy

        // self.reach_pr_sum += self.reach_pr;
        self.reach_pr = 0.0;

        self.strategy = self.get_strategy();
    }

    fn get_strategy(&self) -> [f64; 2] {
        let pos_regrets: [f64; 2] = self.regrets.map(|n| n.max(0.0));
        let regret_sum: f64 = pos_regrets.iter().sum();
        if regret_sum <= 0.0 {
            [0.5; 2]
        } else {
            pos_regrets.map(|n| n / regret_sum)
        }
    }

    fn get_final_strategy(&self) -> [f64; 2] {
        let s_sum: f64 = self.strategy_sum.iter().sum();

        let _decimal_places = 6;
        let _factor = 10_f64.powi(_decimal_places);

        // let bet_prob = (self.strategy_sum[0] / s_sum * factor).round() / factor;
        let call_prob = self.strategy_sum[0] / s_sum;

        // [bet_prob, ((1.0 - bet_prob) * factor).round() / factor]
        [call_prob, 1.0 - call_prob]
    }
}
fn split_key(s: &str) -> (u32, String) {
    let i = s.find(|c: char| !c.is_ascii_digit()).unwrap_or(s.len());
    let (num, rest) = s.split_at(i);
    (num.parse::<u32>().unwrap(), rest.to_string())
}

fn main() {
    let start = Instant::now();
    let mut kuhn = make_new(13);
    let mut strategy_file = File::create("strategy.txt").unwrap();

    let _ = strategy_file.write_all(b"{");
    let mut strategy: Vec<(String, Node)> = kuhn
        .train(500_000)
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();

    strategy.sort_by_key(|(k, _)| split_key(k));
    for (k, node) in strategy {
        let fs: [f64; 2] = node.get_final_strategy();
        // println!("{} {:?} {}", k, fs, fs.iter().sum::<f64>());
        let _ = strategy_file.write_all(format!("'{}': {:?}, \n", k, fs).as_bytes());
        println!("'{}': {:?}", k, fs);
    }

    let _ = strategy_file.write_all(b"}");

    println!("Exploitability: {}", kuhn.calc_exploit());

    println!("Time taken: {:.2?}", start.elapsed());
}
