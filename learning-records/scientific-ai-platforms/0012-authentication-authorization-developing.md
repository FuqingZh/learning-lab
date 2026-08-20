---
Status: superseded by [authentication and confused-deputy mastery](0013-authentication-authorization-mastered.md)
---

# Authentication and confused-deputy boundaries are developing

The learner correctly identifies that user identity must come from a
system-controlled channel rather than a model-declared request field. The
learner also recognizes that generated code requires sandboxing and that
progress, ownership, and user isolation must remain platform-controlled.

Three distinctions remain active. “Do not trust model input” means treating it
as an untrusted proposal that may be accepted after validation, not refusing to
use every field. A sandbox constrains code execution but does not authenticate
the caller or authorize a dataset. Finally, the boundary is not specific to
probabilistic models: a confused deputy arises whenever a more privileged
service combines a caller-controlled designation with the service's own
authority and acts for the wrong principal or purpose.

The learner now understands that sandboxed execution can succeed even when the
larger request is insecure, and that platform boundaries must perform the
checks before execution. The remaining gap is locating the failure precisely:
the Dataset's identity may be perfectly known, while the principal-to-resource
authorization binding is wrong. A handle is a designator used within that
binding, not a “Dataset identity card” that replaces authentication and
authorization.

## Evidence

In the initial authorization explanation on 2026-08-17, the learner placed
identity and workflow control outside the model and connected sandboxing to
model untrustworthiness, but did not yet separate input validation,
authentication, authorization, execution isolation, and the deputy's ambient
authority.

In the first retry on 2026-08-18, the learner correctly said that the sandbox
had not failed and separated generation from execution, but attributed the
failure to the handle providing an incorrect Dataset identity rather than to
the missing authorization between authenticated user A and user B's Dataset.
