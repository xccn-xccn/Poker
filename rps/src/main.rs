use rand::distributions::WeightedIndex;
use rand::prelude::*;
use std::time::Instant;

const WINNER: [[f64; 3]; 3] = [[0.0, -1.0, 1.0], [1.0, 0.0, -1.0], [-1.0, 1.0, 0.0]];

struct RpsBot {
    strategy: [f64; 3],
    strategy_p: Vec<f64>,
    strategy_sum: [f64; 3]
}

impl RpsBot {
    fn get_move(&self, rng: &mut ThreadRng) -> usize {
        let d = WeightedIndex::new(&self.strategy_p).unwrap();
        d.sample(rng)
    }

    fn reward(n1: usize, n2: usize) -> f64 {
        WINNER[n1][n2]
    }

    fn other(c: usize) -> [usize; 2] {
        [(c + 1) % 3, (c + 2) % 3]
    }

    fn convert_percentage(&self, last: bool) -> Vec<f64>{
        let c = if !last {self.strategy} else {self.strategy_sum};
        let s_sum: f64 = c.iter().filter(|&&x| x > 0.0).sum();
        c.iter().map(|&x| if x > 0.0 {x / s_sum} else {1.0 / 3.0}).collect::<Vec<f64>>()
    }

    fn get_strategy(&mut self, n: u32) -> Vec<f64> {
        let mut rng = thread_rng();
        for _ in 0..n {
            self.strategy_p = self.convert_percentage(false);
            
            for (i, p) in self.strategy_p.iter().enumerate() {
                self.strategy_sum[i] += p
            }

            let (a, b) = (self.get_move(&mut rng), self.get_move(&mut rng));

            let rr1 = RpsBot::reward(a, b);
            let rr2 = -rr1;

            for o in RpsBot::other(a) {
                self.strategy[o] +=  RpsBot::reward(o, b) - rr1
            }

            for o in RpsBot::other(b) {
                self.strategy[o] += RpsBot::reward(o, a) - rr2
            }

        }
        println!("{:?}", self.strategy_sum);

        self.convert_percentage(true)

    }
}

fn make_start() -> RpsBot {
    RpsBot {
        strategy: [1.0; 3],
        strategy_sum: [1.0 / 3.0 ; 3],
        strategy_p: vec![1.0 / 3.0 ; 3],
    }
}

fn main() {
    let start = Instant::now();
    let mut a = make_start();

    println!("{:?}", a.get_strategy(100_000));
    println!("Elapsed: {:.2?}", start.elapsed());
}
