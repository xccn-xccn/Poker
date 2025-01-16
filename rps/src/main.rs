use rand::distributions::WeightedIndex;
use rand::prelude::*;
use rand::Rng;

const WINNER: [[i32; 3]; 3] = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]];
struct RpsBot {
    strategy: [i32; 3],
}

impl RpsBot {
    fn get_move(&self) -> usize {
        let d = WeightedIndex::new(self.strategy).unwrap();
        let mut rng = thread_rng();
        d.sample(&mut rng)
    }

    fn reward(n1: usize, n2: usize) -> i32 {
        WINNER[n1][n2]
    }

    fn other(c: usize) -> [usize; 2] {
        [(c+1) % 3, (c+2) % 3]
    }
    fn get_strategy(&mut self, n: u32) -> [i32; 3] {
        for _ in 1..n {
            let a = self.get_move();
            let b = self.get_move();

            let r = RpsBot::reward(a, b);
            self.strategy[a] += r;
            self.strategy[b] += -r;
        }
        self.strategy
    }
}

fn make_start() -> RpsBot {
    RpsBot {
        strategy: [1, 1, 1],
    }
}

fn main() {
    println!("Hello, world!");
    let a = make_start();

    for _ in 1..20 {
        println!("{}", a.get_move())
    }
}
