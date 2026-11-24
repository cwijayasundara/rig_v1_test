# Requirements: view-item

<!-- Copied by rig from .rig/product/sprints/sprint-0/requirements.md, the PRD's own words: never edit it; a behaviour must not contradict it. -->

- AC-2.1 [rule] prd.md:59 "Given an item was added, when GET /items/{id} is called with its id, then the response is 200 with exactly the item returned at creation"
- AC-2.2 [rule] prd.md:60 "WHEN GET /items/{id} is called with an id that is not in the cart THE SYSTEM SHALL respond 404 not_found with the message "Item <id> not found""
- DR-1 [rule] prd.md:73 "An item has exactly four fields: id (string), name (string), price (number), quantity (integer)."
