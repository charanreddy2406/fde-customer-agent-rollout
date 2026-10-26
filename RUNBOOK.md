# Rollout runbook: Tidewater support agent

Run before every stage change
1. python -m rollout.evals
2. python -m rollout.gate     (a stage is allowed only if it is listed)

Stages
- shadow: the agent drafts an answer for every ticket, a person sends their own.
  Nobody outside support sees a draft. Compare drafts to what the person sent.
- ten_percent: one ticket in ten gets the agent's answer directly. Every
  escalation and every refusal still lands in the support queue.
- full: all tickets. Keep the daily review of 20 sampled answers.

Rollback, any one of these, no discussion
- one answer that quotes text not in the cited help article
- one safety or legal ticket that was answered instead of escalated
- held-out pass rate below the stage threshold on the weekly re-run

Watch daily
- share of tickets the agent refuses (a jump means the help articles changed)
- share escalated (a jump means a new wording, or the guard is too wide)
- the five newest wrong answers, pasted into data/holdout.jsonl with the right answer

Known gap
- "Does the warranty cover a broken motor?" retrieves What is not covered,
  because "cover" matches that heading. Two fixes work: a Coverage sentence
  that says a broken motor is covered, or an alias motor -> coverage. The docs
  fix needs the customer and also helps people reading the article; the alias
  is ours to ship but only helps the agent. Either way h8 has now shaped a fix,
  so add fresh held-out tickets before asking for ten_percent.

Owner: the support lead signs each stage change. The engineer on the rollout
is on call for the first week at each stage.
