# External integrations (load only when applicable)

[Español](../integraciones.md).

Read this reference **only** if the artifact touches payments, marketplaces, shipping or external APIs. Examples use generic providers (“payment gateway”, “marketplace”, “carrier”); they neither recommend nor describe any real provider.

Apply each check with the undeclared-case matrix in [method.md](method.md) §3 (declared / neighbor / boundary / failure). A case without evidence is “not checked”.

| Code | Check | Typical failure it looks for | Expected evidence |
|---|---|---|---|
| **C1** | **Permanent vs transient.** Does it distinguish permanent errors (rejection, invalid data) from transient ones (timeout, 5xx, rate limit)? | Retrying a definitive rejection, or giving up on a transient failure | Explicit classification of codes/states and a retry policy with a cap and increasing backoff |
| **C2** | **Attempt vs final outcome.** Does it separate “the request was sent” from “the provider confirmed the final outcome”? | Marking something paid/shipped/published that was only attempted | An intermediate state (e.g. `pending`) and a transition only on confirmation of the final outcome |
| **C3** | **Pending items with expiry.** Does every pending state have a deadline and an action on expiry? | Eternal pending items nobody reviews | Declared expiry, a reconciliation task and an alert on expiry |
| **C4** | **Unverified notification.** Does an incoming notification (webhook, callback, email) only trigger an **authenticated query** to the provider, instead of changing state by itself? | Accepting a forged or replayed notification as truth | Signature verification where available **and** an authenticated status query before acting; idempotency on replays |
| **C5** | **Amount never inferred.** Do amount, currency and quantity come from an authoritative source, never from the notification, the client or an implicit calculation? | Charging or refunding a tampered or misrounded amount | Amount read from the own record or the authenticated query; exact comparison before confirming |
| **C6** | **Common concerns in the common layer.** Do retries, idempotency, signatures, reconciliation and logging live in a shared layer rather than being reimplemented per provider? | Each integration with its own retry bug | One common module used by all adapters; adapters only translate |
| **C7** | **Beyond the declared case.** Is anything tested beyond the happy path the author declared? | “Works” only for the demo example | Neighbor, boundary and failure tests (duplicate, partial, out of order, expired) in addition to the declared case |

How to report: cite the code (C1…C7) in the objection, with the exact location and the missing matrix case. If the artifact declares **only** the happy path of an integration, it is a C7 finding of at least `major` severity, and `blocker` if real money or shipments are involved.

Neutral examples:

- A payment gateway confirms by webhook: if the code marks the order as paid upon receiving the webhook, without querying the authenticated status or comparing the amount, C4 and C5 apply.
- A carrier returns `timeout` when creating a label: retrying without an idempotency key can duplicate the shipment (C1, C6).
- A marketplace leaves a listing “under review”: without expiry or reconciliation it stays pending forever (C3), and showing it as published violates C2.
