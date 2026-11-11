// Money is grouped and never rounded further: a figure that already came off
// build_up() is shown to the cent it produced, not to whatever a JavaScript
// number would coerce it to. The currency code is printed rather than a
// symbol, because KES and USD both appear across this business's rates and
// "$" for one of them would be a real mistake rather than a typographic one.
export function money(amount: string | number, currency: string): string {
  const text = typeof amount === "number" ? amount.toFixed(2) : amount;
  const negative = text.trim().startsWith("-");
  const [whole = "0", cents] = text.replace("-", "").trim().split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const trimmed = cents && /[1-9]/.test(cents) ? `.${cents.slice(0, 2)}` : "";
  return `${negative ? "-" : ""}${currency} ${grouped}${trimmed}`;
}
