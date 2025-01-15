use rand::Rng;
use rand::prelude::*;
use rand::distributions::WeightedIndex;

struct RpsBot {
    strategy: [i32; 3],
}

impl RpsBot {
    fn get_move(&self) -> i32 {
        // [0, 1, 2][self.sample(&mut )]
        0
    }
}

fn make_start() -> RpsBot {
    RpsBot{strategy: [1, 1, 1]}
}

fn main() {
    println!("Hello, world!");
    let a = make_start();
    let weights = [1, 2, 3];
    let d = WeightedIndex::new(&weights).unwrap();
    let mut rng = thread_rng();
    println!("{:?}", d.sample(&mut rng));
}
