# Authentication, authorization, confused deputy, and sandboxing are distinguished

The learner can now keep caller authentication, principal-to-resource
authorization, privileged-service behavior, and execution isolation separate.
An authenticated user A and a correctly identified Dataset owned by B still
require denial because the `A -> B Dataset` authorization is absent.

The learner also understands that a backend becomes a confused deputy when it
uses its own broader Dataset authority to satisfy that unauthorized request,
while a sandbox may simultaneously work exactly as designed because it governs
execution rather than business authorization.

## Evidence

In a fresh deterministic-client scenario on 2026-08-18, the learner identified
the bad identity-to-resource binding, named the backend as the confused deputy
when it used its own authority, and correctly stated that the sandbox could
still succeed.
