use rand::distributions::WeightedIndex;
use rand::prelude::*;
use itertools::{enumerate, Itertools};
use std::time::Instant;


// TODO update pot, not allow pb (return False)
const WINNER: [[f64; 3]; 3] = [[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]];
// const DECK: 
struct Node {
    regrets: [f64; 2], //current regrets to create strategy
    strategy: [f64; 2], //current strategy 
    strategy_p: Vec<f64>, //strategy normalised
    strategy_sum: [f64; 2], //sum of the strategies to work out average strategy
    reach_pr: f64, //reach probability of this node on the current iteration
    reach_pr_sum: f64, //sum of reach probability to normalise strategy_sum
}

struct Kuhn{
    node_map: Vec<Node>,
    history: Vec<char>,
    pot: [usize; 2],
    cards: [usize; 2]
}

fn make_node() -> Node {
    Node {
        regrets: [0.0, 0.0],
        strategy: [1.0; 2],
        strategy_sum: [1.0 / 3.0; 2],
        strategy_p: vec![1.0 / 3.0; 2],
        reach_pr: 0.0,
        reach_pr_sum: 0.0,
    }
}

fn make_new() -> Kuhn {
    Kuhn { node_map: vec![], history: vec![], pot: [0; 2], cards: [0, 0]}
}

impl Kuhn {

    fn train(&mut self, iterations: usize) -> Vec<f64> {
        for _ in 1..iterations {
            for (c1, c2) in (0..3).permutations(2).map(|v|(v[0], v[1])) {
                self.reset();
                self.cards = [c1, c2];
                self.cfr(0, [1.0, 1.0]);
            }
        }
        vec![0.0]
    }

    fn reset(&mut self) {
        self.history = vec![];
        self.pot = [0; 2];
    }
    
    fn is_terminal(&self) -> bool{
        return self.history.len() >= 2
    }

    fn get_reward(&self, cpi: usize, c1: usize, c2: usize) -> isize {
        if c1 > c2 || self.history[self.history.len() - 1] == 'p' {
            self.pot[(cpi + 1) % 2] as isize
        }
        else if c2 > c1{
            self.pot[cpi] as isize
        } else {
            0
        }
    }

    fn get_node(&mut self) -> &mut Node {
        &mut self.node_map[0]
    }
    fn cfr(&mut self, cpi: usize, r_pr: [f64; 2]) -> f64{
        let opi = (cpi + 1) % 2;
        let (c1, c2) = (self.cards[cpi], self.cards[opi]);

        if self.is_terminal() {
            return self.get_reward(cpi, c1, c2) as f64;
        }

        let mut curr_regrets = [0.0; 2];
        let node_strategy = self.get_node().strategy;
        for (i, act) in enumerate(['p', 'q']) {
            self.history.push(act);
            let mut n_pr = r_pr.clone();
            n_pr[cpi] *= node_strategy[i];
            
            curr_regrets[i] -= self.cfr(opi, n_pr);
            //negative because it will get the reward of the other player (cards and cpi switch)
            
            self.history.pop(); //think to check
        }
        
        let node: &mut Node = self.get_node();

        let mut average_regret = 0f64;
        for (r ,s) in curr_regrets.iter().zip(node.strategy.iter()) {
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
    fn update(&mut self) {
        for i in 0..self.strategy_sum.len() {
            self.strategy_sum[i] += self.reach_pr * self.strategy[i];
        }

        self.reach_pr_sum += self.reach_pr;
        self.reach_pr = 0.0;

        self.strategy = self.get_strategy();
    }

    fn get_strategy(&self) -> [f64; 2] {
        [0.5, 0.5]
    }
    fn convert_percentage(&self, last: bool) -> Vec<f64>{
        let c = if !last {self.strategy} else {self.strategy_sum};
        let s_sum: f64 = c.iter().filter(|&&x| x > 0.0).sum();
        c.iter().map(|&x| if x > 0.0 {x / s_sum} else {0.0}).collect::<Vec<f64>>()
    }

    // fn get_strategy(&mut self, opp_move: &str) -> Vec<f64> {
    //     let mut rng = thread_rng();
  
    //     self.strategy_p = self.convert_percentage(false);
        
    //     for (i, p) in self.strategy_p.iter().enumerate() {
    //         self.strategy_sum[i] += p
    //     }

    //     let (a, b) = (self.get_move(&mut rng), (if r < 10_000 {2} else {0}) as usize);

    //     let rr1 = Node::reward(a, b);

    //     for o in Node::other_action(a) {
    //         self.strategy[o] +=  Node::reward(o, b) - rr1
    //     }

        
    //     println!("{:?}", self.strategy_sum);

    //     self.convert_percentage(true)

    // }
}



fn main() {
    let start = Instant::now();
    let mut a = make_new();

    println!("{:?}", a.train(100_000));
    println!("Elapsed: {:.2?}", start.elapsed());
}
