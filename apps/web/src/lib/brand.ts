export const WORDMARK = "HEISSAL";
export const WORDMARK_SUB = "Tours & Travel";

// No telephone number, no address, no email. They live in the API's
// DocumentConfig, which is where the quotation document reads them from; a
// second copy in a footer is the one that goes stale and the one a client
// rings. When this site needs them it fetches them -- and until there is a
// public endpoint that exposes them, the enquiry form is the way to make
// contact, which is also the way that produces a lead.
