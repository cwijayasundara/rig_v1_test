## Amendments
- A1 (B15, B18): a body Python's JSON limits cannot parse (for example an integer of 4301+ digits) is also answered 400 validation_error naming body. Found by the security review.
- A2 (B18): a validation error on a path or query parameter is answered 400 validation_error "<param> is invalid", not with a body message. Found by the code review.
