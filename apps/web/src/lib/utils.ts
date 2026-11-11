import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function duration(minutes: number | null): string {
  if (!minutes) return "";
  if (minutes < 60) return `${minutes} minutes`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h >= 20) return "Full day";
  return m ? `${h} hr ${m} min` : `${h} ${h === 1 ? "hour" : "hours"}`;
}

//: "lodge" -> "Lodge". The catalogue's category is free text by design, so it
//: is presented as typed rather than mapped through a list this app would have
//: to keep in step with the data.
export function titleCase(value: string): string {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : "";
}
