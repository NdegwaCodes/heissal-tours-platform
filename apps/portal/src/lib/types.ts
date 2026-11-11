// Mirrors app/modules/portal/schemas.py. Money arrives as a string, because
// it is NUMERIC in the database and Decimal in the service, and putting it
// through a JavaScript number is how a total ends in .00000000001.

export type Movement = { label: string; minutes: number | null };

export type Day = {
  number: number;
  date: string | null;
  destination: string;
  property_name: string;
  board: string;
  movements: Movement[];
  excursions: string[];
  is_arrival: boolean;
  is_departure: boolean;
  has_night: boolean;
};

export type Stay = {
  sequence: number;
  destination: string;
  property_name: string;
  room_type: string;
  board: string;
  rooms: number;
  nights: number;
};

export type Trip = {
  reference: string;
  status: string;
  arrival_date: string | null;
  departure_date: string | null;
  pax_count: number;
  total: string;
  currency: string;
  property_name: string;
  room_type: string;
  board: string;
  nights: number;
  description: string | null;
  stays: Stay[];
  days: Day[];
  included: string[];
};

export type Instalment = {
  label: string;
  due_on: string;
  amount: string;
  currency: string;
};

export type Payment = {
  amount: string;
  currency: string;
  paid_on: string;
  method: string;
  reference: string | null;
};

export type Statement = {
  reference: string;
  currency: string;
  total: string;
  paid: string;
  balance: string;
  overpaid: string;
  is_settled: boolean;
  schedule: Instalment[];
  payments: Payment[];
  overdue: Instalment[];
  next_due: Instalment | null;
};

// The API's error envelope, which for this app is also its content: a dead
// link's message is written for the client to read (7.2), so the page shows
// it rather than substituting one of its own.
export type ApiError = { code: string; message: string };
