use rand::distributions::WeightedIndex;
use rand::prelude::*;
use itertools::Itertools;
use std::time::Instant;

const WINNER: [[f64; 3]; 3] = [[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]];
// const DECK: 
struct Node {
    strategy: [f64; 2],
    strategy_p: Vec<f64>,
    strategy_sum: [f64; 2]
}

struct Kuhn{
    node_map: Vec<Node>
}

impl Kuhn {
    fn get_reward(player_card: &str, opp_card: &str) -> isize {
        0
    }

    fn train(&self, iterations: usize) -> Vec<f64> {
        for _ in 1..iterations {
            for (c1, c2) in (0..3).permutations(2) {
                self.cfr(c1, c2)
            }
        }
        vec![0.0]
    }
    fn cfr(&self) -> isize{
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

    fn get_strategy(&mut self, opp_move: &str) -> Vec<f64> {
        let mut rng = thread_rng();
  
        self.strategy_p = self.convert_percentage(false);
        
        for (i, p) in self.strategy_p.iter().enumerate() {
            self.strategy_sum[i] += p
        }

        let (a, b) = (self.get_move(&mut rng), (if r < 10_000 {2} else {0}) as usize);

        let rr1 = Node::reward(a, b);

        for o in Node::other_action(a) {
            self.strategy[o] +=  Node::reward(o, b) - rr1
        }

        
        println!("{:?}", self.strategy_sum);

        self.convert_percentage(true)

    }
}

fn make_start() -> Node {
    Node {
        strategy: [1.0; 2],
        strategy_sum: [1.0 / 3.0 ; 2],
        strategy_p: vec![1.0 / 3.0 ; 2],
    }
}

fn main() {
    let start = Instant::now();
    let mut a = make_start();

    println!("{:?}", a.get_strategy(100_000));
    println!("Elapsed: {:.2?}", start.elapsed());
}
