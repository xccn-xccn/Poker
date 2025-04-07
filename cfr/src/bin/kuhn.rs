use itertools::Itertools;
// use rand::distributions::WeightedIndex;
// use rand::prelude::*;
use std::collections::HashMap;
use std::time::Instant;

// Output:
// 0 [0.7799834412423152, 0.22001655875768475] 
// 0b [0.9999974999749998, 2.5000250002500025e-6] 
// 0p [0.668248515106399, 0.33175148489360085] 0.
// 0pb [0.9999983973858495, 1.6026141505440668e-6] 
// 1 [0.9999881248812488, 1.1875118751187512e-5] 
// 1b [0.6641445170761001, 0.3358554829239] 
// 1p [0.9999808331416647, 1.9166858335250016e-5] 
// 1pb [0.444743509072289, 0.555256490927711] 
// 2 [0.336977839243968, 0.6630221607560319] 
// 2b [2.5000250002500025e-6, 0.9999974999749998] 
// 2p [1.000010000100001e-5, 0.999989999899999] 
// 2pb [3.709479836803149e-6, 0.9999962905201631]

#[derive(Clone)]
struct Node {
    regrets: [f64; 2],      //current regrets to create strategy
    strategy: [f64; 2],     //current strategy
    // strategy_p: Vec<f64>,   //strategy normalised
    strategy_sum: [f64; 2], //sum of the strategies to work out average strategy
    reach_pr: f64,          //reach probability of this node on the current iteration
    // reach_pr_sum: f64,      //sum of reach probability to normalise strategy_sum but not actually needed
}

struct Kuhn {
    node_map: HashMap<String, Node>,
    history: String,
    pot: [usize; 2],
    cards: [usize; 2],
}

fn make_new() -> Kuhn {
    Kuhn {
        node_map: HashMap::new(),
        history: String::new(),
        pot: [0; 2],
        cards: [0, 0],
    }
}

impl Kuhn {
    fn train(&mut self, iterations: usize) -> HashMap<String, Node> {
        for _ in 1..iterations {
            for (c1, c2) in (0..3).permutations(2).map(|v| (v[0], v[1])) {
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
    fn cfr(&mut self, cpi: usize, r_pr: [f64; 2]) -> f64 {
        let opi = (cpi + 1) % 2;
        let (c1, c2) = (self.cards[cpi], self.cards[opi]);

        if self.is_terminal() {
            return self.get_reward(c1, c2) as f64;
        }

        let mut curr_regrets = [0.0; 2];
        let node_strategy = self.get_node(cpi).strategy;
        for (i, act) in ['p', 'b'].iter().enumerate(){
            self.history.push(*act);
            let mut n_pr = r_pr; // array of f64 has copy trait
            n_pr[cpi] *= node_strategy[i];

            curr_regrets[i] -= self.cfr(opi, n_pr);
            //negative because it will get the reward of the other player (cards and cpi switch)

            self.history.pop(); //think to check
        }

        let node: &mut Node = self.get_node(cpi);

        let mut average_regret = 0f64;
        for (r, s) in curr_regrets.iter().zip(node.strategy.iter()) {
            average_regret += r * s; //normalised by s
        }

        node.reach_pr += r_pr[cpi];

        for i in 0..node.regrets.len() {
            node.regrets[i] += (curr_regrets[i] - average_regret) * r_pr[opi]
            //update regrets by (regret from this action - average regret) * probabilty of opponent making moves to reach this round
        }
        average_regret
    }
}

impl Node {
    fn new() -> Self {
        Node {
            regrets: [0.0, 0.0],
            strategy: [0.5; 2],
            strategy_sum: [0.0; 2],
            // strategy_p: vec![1.0 / 3.0; 2],
            reach_pr: 0.0,
            // reach_pr_sum: 0.0,
        }
    }
    fn update(&mut self) {
        for i in 0..self.strategy_sum.len() {
            self.strategy_sum[i] += self.reach_pr * self.strategy[i];
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
        // println!("strategy sum {:?} {:?}", self.strategy_sum, self.strategy);
        // self.strategy_sum.map(|s| s / self.reach_pr_sum)
        // let strategy: [f64; 2] = self.strategy_sum;
        let s_sum: f64 = self.strategy_sum.iter().sum();
        self.strategy_sum.map(|s| s / s_sum)
    }
}

fn main() {
    let start = Instant::now();
    let mut a = make_new();
    // println!("{:?}", a.train(100_000));
    let mut strategy: Vec<(String, Node)> = a.train(100_000)
    .iter()
    .map(|(k, v)| (k.clone(), v.clone()))
    .collect();

    strategy.sort_by_key(|(k, _)| k.clone());
    for (k, node) in strategy {
        let fs: [f64; 2] = node.get_final_strategy();
        println!("{} {:?} {}", k, fs, fs.iter().sum::<f64>())
    }
    println!("Elapsed: {:.2?}", start.elapsed());
}
