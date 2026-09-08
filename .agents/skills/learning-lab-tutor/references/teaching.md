# Teaching and example review

Read before composing or repairing an explanation. Seek connected understanding,
not compliance with a visible sequence of headings.

## Build the bridge

Introduce the complete problem and its place in the map in familiar language.
Explain through an example whose actors and operations are known or explained
here. Name ideas when there is enough context to attach meaning to them.
Integrate required syntax instead of opening an endless prerequisite curriculum.

Match the explanation to the question's level. For an overview, give the central
idea and what it makes easier; an execution pipeline is not a substitute. Use a
learner-supplied analogy when it preserves that idea, correcting only misleading
parts. Do not infer broad proficiency from the analogy or broad ignorance from
unfamiliarity with a tool. Add a detail when omitting it blocks the current
explanation or causes a consequential misconception; defer other internals and
caveats. Choose examples that actually exhibit the claimed benefit: an alternate
construction syntax alone does not demonstrate update management.

Review critical dependencies before presenting code: expand unfamiliar shorthand,
teach it before use, or explicitly bracket internals only when they are genuinely
unnecessary. Short code may carry more prerequisite burden than explicit code.

## Contrasting examples

Bad React opening: "A component receives props, returns JSX, and React reconciles
it during render/commit." Appending definitions does not explain why it exists.

Better opening: start from a familiar document whose displayed value must change
with data. Show who changes it today, then explain describing the desired display
and allowing a library to manage document updates. Introduce names when useful.
This is a contextual example, not a universal required React script.

Bad repair: increasingly small fill-in-the-blank questions until the learner
matches an answer, followed by recording independent transfer.

Better repair: identify missing syntax, mechanism or context; explain differently,
then let the learner try related work with less help. Preserve assistance history.

## Dialogue and evidence

Answer direct questions. A substantial branch needs a purpose and return point;
short clarifications can stay inline. On return, explain how the branch resolves
the original problem. Do not require the learner to operate navigation files.

Use the unit organizer to choose what follows a clarification. For example,
explaining which value an API returns can unblock a larger account of why that
API was introduced; it need not initiate a sequence of similar button exercises.
Reconnect through the unresolved problem and then advance it. Do not merely add
a history paragraph before resuming an unrelated drill. If the learner asks to
stay with code or changes the topic, honor that scope instead of forcing return.

Move from demonstration through supported modification toward independent use.
Prediction is optional and requires background. Do not interrupt each paragraph
or require a quiz after clarification. For explicitly chosen retrieval, withhold
the answer before the first attempt; this does not prohibit teaching new material.

Fresh transfer requires a new application, not replay of the just-demonstrated
answer. Agreement, assisted success and delayed independent use are different
evidence. Code tests prove checked behavior, not learning or scientific truth.

## Review without self-certification

Use `docs/evaluations/20260830-coherent-tutoring-cases.md` for bounded content
review. These are review prompts, not model-quality certificates. Separate
experience from independent performance. Ask for feedback at natural boundaries,
not ratings after every turn. Repeated requests for omitted background are a
review signal; ordinary curiosity is not a defect.
Also review unnecessary explanation: can the learner identify the main idea and
benefit, and did each detour help the current question? After "too complicated",
repair the abstraction and example, not merely the word count. Preserve needed
scaffolding; do not replace over-explanation with unexplained shorthand.
Review a multi-turn trajectory as well as individual explanations: does a direct
question get answered, do compatible preferences survive the correction, and does
"continue" advance the agreed unit rather than only the last example? Check the
opposite failure too: no unsolicited full history replay or forced return after
an explicit redirection. Static wording checks cannot establish these behaviors.
