// The wordmark, and nothing else.
//
// Deliberately no telephone number, no address, no consultant's name: those
// live in the API's DocumentConfig (3.6), which is where the quotation
// document reads them from, and a second copy here would be the one that goes
// stale. When this app needs them it fetches them; it does not learn them.
export const WORDMARK = "HEISSAL";
export const WORDMARK_SUB = "Tours & Travel";
