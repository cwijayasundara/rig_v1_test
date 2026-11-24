# Add Item Tests

> Frozen acceptance tests for the add-item feature and the behaviors they pin down.

## Scope

The module covers POST /items end to end through a FastAPI TestClient. [tests/test_add_item.py]
The helper `post_raw` sends a raw string body with a JSON content type. [tests/test_add_item.py#post_raw]
The helper `stored` reads every item from the module-level store. [tests/test_add_item.py#stored]
The helper `valid` builds a good body of name Tea, price 3 and quantity 1, with overrides. [tests/test_add_item.py#valid]
The helper `without` returns a valid body with one field removed. [tests/test_add_item.py#without]

## Successful adds

A valid post returns 201 with exactly the keys id, name, price and quantity. [tests/test_add_item.py#test_b1_ac_1_1_adds_item_and_returns_201]
The response price is a float and the quantity is an int. [tests/test_add_item.py#test_b1_ac_1_1_adds_item_and_returns_201]
Two identical posts are both kept and get different ids. [tests/test_add_item.py#test_b3_ac_1_2_identical_adds_get_different_ids]
The response id is a canonical uuid4 string. [tests/test_add_item.py#test_b4_response_id_is_uuid4]
Leading and trailing whitespace in the name is trimmed. [tests/test_add_item.py#test_b5_name_is_trimmed]
Inner whitespace in the name is kept. [tests/test_add_item.py#test_b5_inner_whitespace_is_kept]
A one-character name is accepted, and a padded one is trimmed to it. [tests/test_add_item.py#test_b5_single_character_name_is_accepted]
A price of 0 and prices with up to two decimals are accepted and returned as JSON numbers. [tests/test_add_item.py#test_b6_dr_4_price_is_returned_as_json_number]
A raw price of 8.50 is returned as the number 8.5 and stored as `Decimal("8.5")`. [tests/test_add_item.py#test_b6_dr_4_price_8_5_is_not_rendered_as_string]
A price with two decimals passes and one with three decimals is rejected. [tests/test_add_item.py#test_b6_two_decimals_accepted_three_rejected]
A quantity of 1 is the minimum and there is no upper limit. [tests/test_add_item.py#test_b7_dr_5_quantity_accepted_without_upper_limit]
Unknown fields are ignored and do not appear in the response. [tests/test_add_item.py#test_b8_ac_1_7_extra_fields_are_ignored]
A client-supplied id is ignored and the server generates a uuid4. [tests/test_add_item.py#test_b8_ac_1_7_client_id_is_ignored]
Extra fields do not change the message of a real validation error. [tests/test_add_item.py#test_b8_extra_fields_ignored_with_every_field_stored_exactly]

## Rejections

Every rejection is a 400 with the error `validation_error`, and nothing is stored. [tests/test_add_item.py#assert_rejected]
A name that is not a string, is empty or is whitespace only is rejected, as is a missing name. [tests/test_add_item.py#test_b12_ac_1_3_bad_name_is_rejected]
A price that is a string, null, a boolean, negative or over two decimals is rejected. [tests/test_add_item.py#test_b13_ac_1_4_bad_price_is_rejected]
A missing price is rejected. [tests/test_add_item.py#test_b13_ac_1_4_missing_price_is_rejected]
NaN, Infinity and -Infinity sent as raw content are rejected as a bad price. [tests/test_add_item.py#test_b13_ac_1_4_non_finite_price_is_rejected]
A quantity that is a float, string, boolean, below 1 or null is rejected. [tests/test_add_item.py#test_b14_ac_1_5_bad_quantity_is_rejected]
A missing quantity is rejected. [tests/test_add_item.py#test_b14_ac_1_5_missing_quantity_is_rejected]
Invalid JSON, an empty body and non-object JSON are rejected as a bad body. [tests/test_add_item.py#test_b15_ac_1_6_bad_body_is_rejected]
A POST with no body at all is also a body error. [tests/test_add_item.py#test_b15_ac_1_6_request_without_body]
An oversized 5000-digit integer is treated as a body error. [tests/test_add_item.py#test_b15_b18_oversized_integer_quantity_is_a_body_error]
The same holds when the oversized integer sits in an ignored extra field. [tests/test_add_item.py#test_b15_b18_oversized_integer_in_ignored_field_is_a_body_error]

## Error messages

The helper `assert_exact` requires a 400 whose JSON is exactly the error and message pair, with nothing stored. [tests/test_add_item.py#assert_exact]
The message for a quantity of 0 is "quantity must be an integer of at least 1". [tests/test_add_item.py#test_b16_ac_1_8_exact_message]
Each message starts with the field name followed by "must be". [tests/test_add_item.py#test_b16_ac_1_8_message_follows_field_must_be_form]
Every body rejection carries the message "body must be a JSON object". [tests/test_add_item.py#test_b16_ac_1_8_body_message_is_exact]
A request with no body gets the same body message. [tests/test_add_item.py#test_b16_ac_1_8_request_without_body_message_is_exact]
Every bad name gets the message "name must be a non-empty string". [tests/test_add_item.py#test_b16_ac_1_8_name_message_is_exact]
A missing name gets the same name message. [tests/test_add_item.py#test_b16_ac_1_8_missing_name_message_is_exact]
Every bad price gets the message "price must be a number of at least 0 with at most 2 decimal places". [tests/test_add_item.py#test_b16_ac_1_8_price_message_is_exact]
A missing price gets the same price message. [tests/test_add_item.py#test_b16_ac_1_8_missing_price_message_is_exact]
Non-finite prices get the same price message. [tests/test_add_item.py#test_b16_ac_1_8_non_finite_price_message_is_exact]
Every bad quantity gets the message "quantity must be an integer of at least 1". [tests/test_add_item.py#test_b16_ac_1_8_quantity_message_is_exact]
A missing quantity gets the same quantity message. [tests/test_add_item.py#test_b16_ac_1_8_missing_quantity_message_is_exact]
When several fields are invalid, only the first is named, in the order name, price, quantity. [tests/test_add_item.py#test_b17_ac_1_8_first_invalid_field_is_named]

## Error shape and framework behavior

Validation failures are 400, never 422, with exactly the keys error and message. [tests/test_add_item.py#test_b18_ac_1_3_failures_are_400_never_422]
The module app is a FastAPI app titled "Shopping Cart API" that answers 400 for an empty object. [tests/test_add_item.py#test_b18_app_is_a_fastapi_app_with_title_and_error_handler]
The module store is a real `CartStore` that receives posts when the fixture swap is not used. [tests/test_add_item.py#test_b1_module_store_is_a_cart_store_and_receives_posts]
An unknown path keeps the default FastAPI 404 body. [tests/test_add_item.py#test_b18_unknown_path_keeps_the_framework_404_shape]
A wrong method keeps the default FastAPI 405 body. [tests/test_add_item.py#test_b18_wrong_method_keeps_the_framework_405_shape]
The helper `_probe_client` builds a separate app that uses `register_error_handlers` with path and query routes. [tests/test_add_item.py#_probe_client]
A path parameter failure returns 400 with the message "n is invalid". [tests/test_add_item.py#test_b18_path_parameter_failure_names_the_parameter]
A query parameter failure returns 400 with the message "name is invalid". [tests/test_add_item.py#test_b18_query_parameter_failure_names_the_parameter]

## Validation order

```mermaid
flowchart TD
    A[POST /items] --> B{body is JSON object}  %% [tests/test_add_item.py#test_b16_ac_1_8_body_message_is_exact]
    B -- no --> E1[400 body message]  %% [tests/test_add_item.py#test_b16_ac_1_8_body_message_is_exact]
    B -- yes --> C{name valid}  %% [tests/test_add_item.py#test_b16_ac_1_8_name_message_is_exact]
    C -- no --> E2[400 name message]  %% [tests/test_add_item.py#test_b16_ac_1_8_name_message_is_exact]
    C -- yes --> D{price valid}  %% [tests/test_add_item.py#test_b16_ac_1_8_price_message_is_exact]
    D -- no --> E3[400 price message]  %% [tests/test_add_item.py#test_b16_ac_1_8_price_message_is_exact]
    D -- yes --> F{quantity valid}  %% [tests/test_add_item.py#test_b16_ac_1_8_quantity_message_is_exact]
    F -- no --> E4[400 quantity message]  %% [tests/test_add_item.py#test_b16_ac_1_8_quantity_message_is_exact]
    F -- yes --> G[201 item stored]  %% [tests/test_add_item.py#test_b1_ac_1_1_adds_item_and_returns_201]
```
