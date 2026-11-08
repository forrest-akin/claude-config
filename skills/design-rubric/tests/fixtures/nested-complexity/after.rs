fn first(a: i32, b: i32) -> i32 {
    if a > 0 {
        for i in 0..b {
            if i > a {
                return i;
            }
        }
    }
    0
}
