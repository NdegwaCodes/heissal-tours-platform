// Mirrors app/modules/public/schemas.py.
//
// Note what is not here, and cannot be: no rate, no cost, no supplier, no
// availability. The API's allow-list decides that, so no edit in this app can
// put a price on a page by accident -- there is no field to read.

export type Image = {
  id: string;
  url: string;
  alt_text: string | null;
  width: number | null;
  height: number | null;
  is_lead: boolean;
};

export type Place = {
  name: string;
  slug: string;
  type: string;
  country: string;
  region: string | null;
  latitude: string | null;
  longitude: string | null;
  description: string | null;
  images: Image[];
  stays: string[];
  activities: string[];
};

export type Property = {
  name: string;
  slug: string;
  category: string;
  star_rating: number | null;
  latitude: string | null;
  longitude: string | null;
  check_in_time: string | null;
  check_out_time: string | null;
  description: string | null;
  destination: string;
  destination_slug: string;
  rooms: string[];
  images: Image[];
};

export type Experience = {
  name: string;
  slug: string;
  description: string | null;
  duration_minutes: number | null;
  destination: string;
  destination_slug: string;
};

// Mirrors app/modules/public/schemas.py:ContactRead — the same source the
// quotation document prints (DocumentConfig, §3.6), so the website never
// carries its own, separately-stale copy of a phone number.
export type Contact = {
  company_name: string;
  contact_email: string;
  contact_phone: string;
  social_line: string;
};

// Mirrors app/modules/public/schemas.py:EstimateRead / LegEstimateRead.
// Money is a string for the same reason it is everywhere else in this
// app -- it is NUMERIC in the database and Decimal in the service.
export type LegEstimate = {
  destination: string;
  tier: string;
  nights: number;
  property_name: string | null;
  room_type: string | null;
  meal_plan: string | null;
  currency: string | null;
  per_person: string | null;
  group_total: string | null;
  refused: string | null;
};

export type Estimate = {
  legs: LegEstimate[];
  currency: string | null;
  per_person: string | null;
  group_total: string | null;
  note: string;
};
