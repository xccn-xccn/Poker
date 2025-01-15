struct RpsBot {
    strategy: [i32; 3],
}

impl RpsBot {
    fn make_start() -> RpsBot {
        RpsBot{strategy: [1, 1, 1]}
    }
}


fn main() {
    println!("Hello, world!");
    let a = make_start();
}
