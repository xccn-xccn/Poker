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
        [(c + 1) % 3, (c + 2) % 3]
    }
    fn get_strategy(&mut self, n: u32) -> Vec<i32> {
        for _ in 1..n {
            let a = self.get_move();
            let b = self.get_move();

            let cr1 = RpsBot::reward(a, b);
            let cr2 = -cr1;
            self.strategy[a] += cr1;
            self.strategy[b] += cr2;

            for o in RpsBot::other(a) {
                self.strategy[o] += cr1 - RpsBot::reward(o, b)
            }

            for o in RpsBot::other(b) {
                self.strategy[o] += cr1 - RpsBot::reward(o, a)
            }
        }
        let mut f_strategy = Vec::new();
        let s_sum: i32 = self.strategy.iter().sum();
        for s in self.strategy {
            f_strategy.push(s / s_sum);
        }

        println!("{:?}", self.strategy);
        f_strategy
    }
}

fn make_start() -> RpsBot {
    RpsBot {
        strategy: [1, 1, 1],
    }
}

fn main() {
    println!("Hello, world!");
    let mut a = make_start();

    println!("{:?}", a.get_strategy(4));
    // for _ in 1..20 {
    //     println!("{}", a.get_move())
    // }
}
