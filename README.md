# Forward-Deployed AI Engineer | Customer Agent Rollout

An intermediate Python practice project built from how four postings describe forward-deployed and deployed AI engineering. Palantir's Forward Deployed Software Engineer, New Grad posting asks for "custom applications, LLM workflows, and production solutions engineered for a specific customer's reality". Baseten's Forward Deployed Engineer (Training) posting asks you to take customer objectives "from vague to shipped", design the evals and benchmarks that show where quality falls short, and be first responder to production failures, including triage. LangChain's Deployed Engineer posting asks you to "co-architect and co-build production AI agents with customer engineering teams" and lists failure handling and LLM evaluation. Sierra's APX posting asks you to "build and ship AI agents with Sierra's customers" in production. This project is the rollout loop those lines share, on a fictional customer, Tidewater Appliance Co. You index the customer's help articles with SQLite FTS5, answer a ticket with one quoted passage and a citation, reject any answer whose quote is not word for word in the section it cites, and hand safety, legal and large-refund tickets to a person with a deterministic guard that no model can talk past. You then run a 16-ticket eval set that honestly fails (0.81, three retrieval misses), triage the failing traces into buckets, fix the top bucket with a customer-vocabulary alias list, and see the eval reach 1.00. Because that fix was written while looking at those same tickets, you add a held-out set that scores 0.88 with one visible miss, and a rollout gate that lets the agent into shadow mode but not into ten percent traffic, with a runbook that says why. This is a practice project built from the four postings' description of the work; it does not describe any of those companies' own systems. The postings do not name a stack for this work, so Python's standard library and SQLite, and a rule-based answer step you could later swap for a language model, are this project's own choice. Nothing here calls a model or needs an API key.

Built step-by-step with [KhwajaLabs Build](https://khwajalabs.com).

## Stack
- Python
- SQLite
- FTS5
- BM25
- unittest
- JSON
