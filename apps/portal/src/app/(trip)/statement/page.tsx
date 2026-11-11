"use client";

import { Eyebrow } from "@/components/eyebrow";
import { Refused } from "@/components/refused";
import { longDate, money, shortDate } from "@/lib/format";
import { useRead } from "@/lib/read";
import type { Instalment, Payment, Statement } from "@/lib/types";

// What is paid, what is due, and when.
//
// The same arithmetic as the operator's view, from the same endpoint (7.1):
// two implementations would eventually disagree, and the client's copy is the
// one sitting in somebody's inbox being read out down the telephone.
//
// Nothing here takes a payment. When the M-Pesa integration lands behind the
// `payments` rows this is the page it appears on; until then offering a
// button that does not work would be worse than the honest absence.

export default function StatementPage() {
  const read = useRead<Statement>("statement");

  if (read.state === "loading") {
    return <p className="text-sm text-ink-soft">Loading your statement...</p>;
  }
  if (read.state === "failed") return <Refused error={read.error} />;

  const s = read.data;
  const overdueKeys = new Set(s.overdue.map(key));

  return (
    <div className="space-y-12">
      <section>
        <Eyebrow>Payments</Eyebrow>
        {s.is_settled ? (
          <>
            <h1 className="mt-3 font-display text-4xl">Paid in full</h1>
            <p className="oldstyle mt-3 text-[14px] text-ink-soft">
              {money(s.paid, s.currency)} received against a total of{" "}
              {money(s.total, s.currency)}.
            </p>
          </>
        ) : (
          <>
            <h1 className="mt-3 text-[13px] uppercase tracking-eyebrow text-ink-soft">
              Still to pay
            </h1>
            <p className="oldstyle mt-2 font-display text-5xl">
              {money(s.balance, s.currency)}
            </p>
            <p className="oldstyle mt-3 text-[14px] text-ink-soft">
              {money(s.paid, s.currency)} received of{" "}
              {money(s.total, s.currency)}.
            </p>
          </>
        )}

        {/* Kept apart from the balance on purpose (7.1): "you owe minus four
            thousand shillings" is not a sentence a client should read. */}
        {Number(s.overpaid) > 0 ? (
          <p className="oldstyle mt-3 text-[13px] text-gold">
            {money(s.overpaid, s.currency)} paid above the total. Your
            consultant will sort this out with you.
          </p>
        ) : null}
      </section>

      {s.overdue.length ? (
        <section className="border border-gold bg-cream px-6 py-5">
          <p className="text-[13px] font-medium">
            {s.overdue.length === 1
              ? "One payment is past its due date"
              : `${s.overdue.length} payments are past their due date`}
          </p>
          <ul className="oldstyle mt-2 space-y-1 text-[13px] text-ink-soft">
            {s.overdue.map((row) => (
              <li key={key(row)}>
                {row.label} - {money(row.amount, row.currency)}, due{" "}
                {longDate(row.due_on)}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[12px] leading-relaxed text-ink-soft">
            If one of these has already been paid it may not have reached us
            yet. Your consultant can check.
          </p>
        </section>
      ) : s.next_due ? (
        <section className="border border-hairline bg-cream-tint px-6 py-5">
          <Eyebrow>Next payment</Eyebrow>
          <p className="oldstyle mt-2 font-display text-2xl">
            {money(s.next_due.amount, s.next_due.currency)}
          </p>
          <p className="oldstyle mt-1 text-[13px] text-ink-soft">
            {s.next_due.label}, due {longDate(s.next_due.due_on)}
          </p>
        </section>
      ) : null}

      {s.schedule.length ? (
        <section>
          <Eyebrow>Your payment schedule</Eyebrow>
          <table className="mt-5 w-full text-[13px]">
            <thead>
              <tr className="border-b border-hairline text-left">
                <Th>Payment</Th>
                <Th>Due</Th>
                <Th className="text-right">Amount</Th>
              </tr>
            </thead>
            <tbody>
              {s.schedule.map((row) => (
                <tr key={key(row)} className="border-b border-hairline">
                  <Td>{row.label}</Td>
                  <Td className="oldstyle">
                    {shortDate(row.due_on)}
                    {overdueKeys.has(key(row)) ? (
                      <span className="ml-2 text-[11px] uppercase tracking-eyebrow text-gold">
                        Overdue
                      </span>
                    ) : null}
                  </Td>
                  <Td className="oldstyle text-right">
                    {money(row.amount, row.currency)}
                  </Td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-3 text-[12px] leading-relaxed text-ink-soft">
            {/* Payments are applied oldest first rather than matched to a
                line (7.1), so a schedule row is not marked "paid": real
                payments do not line up with invoices, and a tick against the
                wrong line is worse than no tick. */}
            Payments are applied to the earliest amount outstanding, so what
            you have paid may not line up line-for-line with this schedule.
            The figures above are the ones that count.
          </p>
        </section>
      ) : null}

      {s.payments.length ? (
        <section>
          <Eyebrow>Payments received</Eyebrow>
          <table className="mt-5 w-full text-[13px]">
            <thead>
              <tr className="border-b border-hairline text-left">
                <Th>Received</Th>
                <Th>How</Th>
                <Th>Reference</Th>
                <Th className="text-right">Amount</Th>
              </tr>
            </thead>
            <tbody>
              {s.payments.map((row, i) => (
                <tr key={`${row.paid_on}-${i}`} className="border-b border-hairline">
                  <Td className="oldstyle">{shortDate(row.paid_on)}</Td>
                  <Td>{row.method}</Td>
                  <Td className="oldstyle">{row.reference ?? ""}</Td>
                  <Td className="oldstyle text-right">
                    {money(row.amount, row.currency)}
                  </Td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      <p className="text-[12px] leading-relaxed text-ink-soft">
        This is a record, not a payment page: your consultant will tell you how
        to send each payment. If something here looks wrong, say so before
        paying it.
      </p>
    </div>
  );
}

const key = (row: Instalment | Payment) =>
  "due_on" in row ? `${row.label}-${row.due_on}` : `${row.paid_on}`;

function Th({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <th
      className={`pb-2 text-[10px] font-medium uppercase tracking-eyebrow text-ink-soft ${className}`}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <td className={`py-3 align-top ${className}`}>{children}</td>;
}
