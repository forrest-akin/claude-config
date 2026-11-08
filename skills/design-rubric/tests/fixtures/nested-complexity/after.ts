export function first(a: number, b: number): number {
  if (a > 0) {
    for (let i = 0; i < b; i++) {
      if (i > a) {
        return i;
      }
    }
  }
  return 0;
}
