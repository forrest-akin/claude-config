export function score(x: number): number {
  let t = 0;
  if (x === 0) { t += 1; }
  if (x === 1) { t += 1; }
  if (x === 2) { t += 1; }
  if (x === 3) { t += 1; }
  if (x === 4) { t += 1; }
  if (x === 5) { t += 1; }
  if (x === 6) { t += 1; }
  if (x === 7) { t += 1; }
  return t;
}
