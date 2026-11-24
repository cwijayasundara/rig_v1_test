---
sprint: 0
status: accepted
---
# ADR-0001: Item ids are server-generated UUID version 4 strings

Decides: DR-2 (also DR-1, AC-1.2, AC-1.7).

## Context

The item id is the public handle of an item: clients keep it and send it back in `GET /items/{id}`. Once a client holds an id, its format cannot change without breaking that client, so this is a one-way door. The PRD marks the choice "proposed at chart" and gives no other constraint: the cart is in memory, single process, and ids must be unique within the process and never reused (DR-2).

## Decision

`CartStore.add` generates `str(uuid.uuid4())`: a UUID version 4 in canonical lowercase hyphenated form (for example `3f2b8c1e-6d1a-4c53-9a7e-0b5d2f6c8e11`). The store draws again if the id is already held, inside the same lock as the append. A client-supplied `id` in the body is ignored (AC-1.7). (proposed at chart)

## Consequences

- Ids are unguessable and unique without a counter, so concurrent adds never need to coordinate on a sequence beyond the store lock.
- Ids are opaque 36-character strings: the cart's order comes from the list, not from the id.
- A later persistent store keeps the same ids; moving to another format would break every client that kept one.

## Alternatives

- Integer counter starting at 1: shorter, but guessable, and it needs a counter that must survive a restart if persistence arrives.
- UUID v7 or ULID: time-ordered, but the PRD asks for nothing beyond uniqueness and insertion order is already kept by the list.
