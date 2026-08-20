# Idempotency foundations are distinguished from response equality and success

The learner can judge idempotency by repeated intended side effects rather than
response equality, distinguish one logical operation from multiple request
attempts, preserve an idempotency key across retries, and require a new key for
a genuinely new operation. The learner also recognizes that operation scope is
part of the identity and that reusing the same scoped key with different
payload content is a caller conflict rather than a valid retry.

## Evidence

On 2026-08-19, the learner correctly classified incrementing a balance as
non-idempotent, identified Job creation rather than the returned Job ID as the
side effect, reused the original key after a lost response, assigned a new key
to a genuinely new Job, and rejected treating different payloads under the same
scoped key as one logical operation. After a focused correction, the learner
also stated that a stable error proves idempotency only when retries do not
repeat external state changes, and that idempotency does not prove success.
