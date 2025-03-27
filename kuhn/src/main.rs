use rand::distributions::WeightedIndex;
use rand::prelude::*;
use itertools::{enumerate, Itertools};
use std::time::Instant;

const WINNER: [[f64; 3]; 3] = [[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]];
// const DECK: 
struct Node {
    strategy: [f64; 2],
    strategy_p: Vec<f64>,
    strategy_sum: [f64; 2]
}

struct Kuhn{
    node_map: Vec<Node>,
    history: Vec<char>,
    pot: [usize; 2],
}

impl Kuhn {

    fn train(&mut self, iterations: usize) -> Vec<f64> {
        for _ in 1..iterations {
            for (c1, c2) in (0..3).permutations(2).map(|v|(v[0], v[1])) {
                self.reset();
                self.cfr(0, c1, c2);
            }
        }
        vec![0.0]
    }

    fn reset(&mut self) {
        self.history = vec![];
        self.pot = [0; 2];
    }
    
    fn is_terminal(&self) -> bool{
        true
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
    fn cfr(&mut self, cpi: usize, c1: usize, c2: usize) -> isize{

        if self.is_terminal() {
            return self.get_reward(cpi, c1, c2);
        }

        let node = self.get_node();
        let mut curr_regrets = [0; 2];
        for (i, act) in enumerate(['p', 'q']) {
            self.history.push(act);
            curr_regrets[i] += -self.cfr((cpi + 1) % 2, c2, c1);
            //negative because it will get the reward of the other player (cards and cpi switch)

            self.history.pop(); //think to check
        }
        0 
    }
}

impl Node {
    fn get_move(&self, rng: &mut ThreadRng) -> usize {
        let d = WeightedIndex::new(&self.strategy_p).unwrap();
        d.sample(rng)
    }

    fn other_action(c: usize) -> [usize; 1] {
        [(c + 1) % 2]
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

fn make_node() -> Node {
    Node {
        strategy: [1.0; 2],
        strategy_sum: [1.0 / 3.0; 2],
        strategy_p: vec![1.0 / 3.0; 2],
    }
}

fn make_new() -> Kuhn {
    Kuhn { node_map: vec![], history: vec![], pot: [0; 2]}
}

fn main() {
    let start = Instant::now();
    let mut a = make_new();

    println!("{:?}", a.train(100_000));
    println!("Elapsed: {:.2?}", start.elapsed());
}
