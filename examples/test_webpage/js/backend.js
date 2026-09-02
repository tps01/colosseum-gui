/** In-page stand-in for a shop-floor API (latency + a rolled result). */

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const roll = () => 1 + Math.floor(Math.random() * 10);

export async function startProduction(sku) {
  await sleep(1500);
  return { ok: true, sku, lot: roll() };
}

export async function inspectLot() {
  await sleep(2000);
  return { ok: true, grade: roll() };
}
