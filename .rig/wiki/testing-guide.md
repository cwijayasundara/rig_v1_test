# Testing Guide

> How the test suite is organized, shared fixtures, and how to run and extend tests.

## Layout

The suite has five files under `tests/`. [tests/conftest.py]
`tests/conftest.py` holds the shared `client` fixture. [tests/conftest.py#client]
`tests/test_api.py` holds a single smoke test of the empty cart. [tests/test_api.py#test_smoke_empty_cart_lists_nothing]
`tests/test_add_item.py` tests `POST /items` end to end. [tests/test_add_item.py]
`tests/test_store.py` tests `CartStore` directly, with no HTTP layer. [tests/test_store.py]
`tests/test_view_item.py` tests `GET /items/{id}` and the C1 cleanup. [tests/test_view_item.py]

## Shared fixture

The `client` fixture replaces `cart.main.store` with a new, empty `CartStore` through `monkeypatch`. [tests/conftest.py#client]
It then yields a `TestClient` wrapped around `cart.main.app`. [tests/conftest.py#client]
Each test that uses `client` therefore starts with an empty cart. [tests/conftest.py#client]
`tests/test_api.py` does not use the fixture and builds its own module-level `TestClient`. [tests/test_api.py]

## Test naming and traceability

Test names and docstrings carry behaviour ids such as `B1`, `B16`, `AC-1.8`, `DR-4` and `NFR-1`. [tests/test_add_item.py#test_b16_ac_1_8_exact_message]
Store tests that need no HTTP call use the same naming scheme. [tests/test_store.py#test_b4_dr_2_id_is_canonical_uuid4]

## Helpers in the add-item tests

`post_raw` posts a string as the raw request body with a JSON content type. [tests/test_add_item.py#post_raw]
`stored` returns the items currently held by the module store. [tests/test_add_item.py#stored]
`valid` builds a valid request body and lets a test override individual fields. [tests/test_add_item.py#valid]
`without` builds a valid body with one field removed. [tests/test_add_item.py#without]
`assert_rejected` checks for a 400, the `validation_error` code, the field name in the message and an empty store. [tests/test_add_item.py#assert_rejected]
`assert_exact` checks for a 400, the full error body and an empty store. [tests/test_add_item.py#assert_exact]
The exact validation messages live in module-level constants in the same file. [tests/test_add_item.py]

## What the add-item tests cover

A successful add returns 201 with exactly the keys `id`, `name`, `price` and `quantity`. [tests/test_add_item.py#test_b1_ac_1_1_adds_item_and_returns_201]
The response id is a canonical uuid4, and a client-supplied id is ignored. [tests/test_add_item.py#test_b8_ac_1_7_client_id_is_ignored]
Names are trimmed at the ends only. [tests/test_add_item.py#test_b5_inner_whitespace_is_kept]
Prices are returned as JSON numbers and stored as `Decimal`. [tests/test_add_item.py#test_b6_dr_4_price_8_5_is_not_rendered_as_string]
Quantities have a minimum of 1 and no upper limit. [tests/test_add_item.py#test_b7_dr_5_quantity_accepted_without_upper_limit]
Bad names, prices, quantities and bodies each return a 400 with a fixed message. [tests/test_add_item.py#test_b18_ac_1_3_failures_are_400_never_422]
When several fields are invalid, the message names the first one in the order name, price, quantity. [tests/test_add_item.py#test_b17_ac_1_8_first_invalid_field_is_named]
Oversized integers are reported as a body error. [tests/test_add_item.py#test_b15_b18_oversized_integer_quantity_is_a_body_error]
Unknown paths and wrong methods keep the framework's default 404 and 405 bodies. [tests/test_add_item.py#test_b18_unknown_path_keeps_the_framework_404_shape]
`_probe_client` builds a throwaway app with `register_error_handlers` to test path and query parameter failures. [tests/test_add_item.py#_probe_client]
One test uses a plain `TestClient` without the fixture and removes its added item from the module store afterwards. [tests/test_add_item.py#test_b1_module_store_is_a_cart_store_and_receives_posts]

## What the store tests cover

Item ids are canonical uuid4 values and are distinct across adds. [tests/test_store.py#test_b4_dr_2_ids_are_distinct_across_adds]
`CartStore.add` takes only `name`, `price` and `quantity`, so a caller cannot supply an id. [tests/test_store.py#test_b4_dr_2_client_cannot_supply_an_id]
`list_all` returns items oldest first. [tests/test_store.py#test_list_all_is_oldest_first]
`list_all` returns a copy, so changing the result does not change the store. [tests/test_store.py#test_b10_nfr_1_list_all_returns_a_copy]
One hundred threads released together by a barrier lose no items. [tests/test_store.py#test_b9_nfr_1_hundred_concurrent_adds_lose_nothing]
Concurrent readers only ever see complete items. [tests/test_store.py#test_b10_nfr_1_readers_never_see_a_half_added_item]
`RecordingLock` is a stand-in lock that records the store size on every enter and exit. [tests/test_store.py#RecordingLock]
It records the size on entry. [tests/test_store.py#RecordingLock.__enter__]
It records the size on exit. [tests/test_store.py#RecordingLock.__exit__]
Tests use it to check that `add` and `list_all` each take the lock once. [tests/test_store.py#test_b10_nfr_1_add_holds_the_lock_around_draw_and_append]
Another test holds the lock from outside and checks that `add` and `list_all` block until it is released. [tests/test_store.py#test_b10_nfr_1_add_and_list_all_block_while_the_lock_is_held]

## What the view-item tests cover

`create` posts a valid item and returns the response body. [tests/test_view_item.py#create]
`GET /items/{id}` returns exactly the body that `POST /items` returned. [tests/test_view_item.py#test_b1_ac_2_1_get_returns_the_created_item]
An unknown id returns 404 with the `not_found` error and a message naming the id. [tests/test_view_item.py#test_b2_ac_2_2_unknown_id_is_404_not_found]
The expected 404 body is held in a module-level constant. [tests/test_view_item.py]
`CartStore.get` raises `ItemNotFoundError` for an unknown id and never returns `None`. [tests/test_view_item.py#test_b3_ac_2_2_store_get_raises_for_unknown_id]
Id lookup is case-sensitive. [tests/test_view_item.py#test_b4_ac_2_1_lookup_is_case_sensitive]
`get` leaves the cart unchanged. [tests/test_view_item.py#test_b5_ac_2_1_get_returns_added_item_and_leaves_cart_unchanged]
`get` waits for the store lock. [tests/test_view_item.py#test_b5_ac_2_1_get_waits_for_the_store_lock]
Ids that are not UUIDs still return 404, not 400 or 500. [tests/test_view_item.py#test_b6_ac_2_2_non_uuid_id_is_404_not_found]
A test parses `cart/errors.py` with `ast` and asserts it contains no `assert` statement. [tests/test_view_item.py#test_b7_c1_errors_module_has_no_assert_statement]
An invalid POST body still returns 400 with `validation_error`. [tests/test_view_item.py#test_b7_c1_invalid_post_body_still_400_validation_error]

## Extending the suite

New HTTP tests take the `client` fixture so each one starts with an empty store. [tests/conftest.py#client]
Parametrized rejection cases can call `assert_rejected` or `assert_exact` instead of repeating the checks. [tests/test_add_item.py#assert_exact]
Tests that need the store alone build a `CartStore` directly. [tests/test_store.py#test_b4_returned_item_is_the_stored_item]
Tests that need a custom app use a probe app with `register_error_handlers`. [tests/test_add_item.py#_probe_client]
