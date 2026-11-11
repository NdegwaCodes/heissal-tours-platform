import { TZ } from "@/lib/tz";

// Dates arrive as plain YYYY-MM-DD -- a travel date, not an instant -- so
// they are formatted by splitting the string. Passing one through `new Date()`
// reads it as UTC midnight, and a client west of Greenwich is then shown the
// day before their own arrival.
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function parts(value: string | null | undefined) {
  if (!value) return null;
  const [y, m, d] = value.split("-").map(Number);
  if (!y || !m || !d || m < 1 || m > 12) return null;
  return { y, m, d };
}

export function longDate(value: string | null | undefined): string {
  const p = parts(value);
  if (!p) return value ?? "";
  return `${p.d} ${MONTHS[p.m - 1]} ${p.y}`;
}

export function shortDate(value: string | null | undefined): string {
  const p = parts(value);
  if (!p) return value ?? "";
  return `${p.d} ${MONTHS[p.m - 1]!.slice(0, 3)} ${p.y}`;
}

export function weekday(value: string | null | undefined): string {
  const p = parts(value);
  if (!p) return "";
  return new Date(Date.UTC(p.y, p.m - 1, p.d)).toLocaleDateString("en-GB", {
    weekday: "long",
    timeZone: "UTC",
  });
}

// Money is grouped and never rounded: the figure shown is the figure frozen
// onto the booking, to the cent. The currency code is printed rather than a
// symbol, because KES and USD both appear in this business and "$" for one of
// them would be a real mistake rather than a typographic one.
export function money(amount: string | number, currency: string): string {
  const text = typeof amount === "number" ? amount.toFixed(2) : amount;
  const negative = text.trim().startsWith("-");
  const [whole = "0", cents] = text.replace("-", "").trim().split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const trimmed = cents && /[1-9]/.test(cents) ? `.${cents.slice(0, 2)}` : "";
  return `${negative ? "-" : ""}${currency} ${grouped}${trimmed}`;
}

// The business's own day, not the reader's: an instalment falls due in
// Nairobi. A client reading this at midnight in Sydney is not a day ahead of
// their own payment schedule.
export function today(): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: TZ }).format(new Date());
}

export function isPast(value: string): boolean {
  return value < today();
}

export function nights(count: number): string {
  return `${count} ${count === 1 ? "night" : "nights"}`;
}
