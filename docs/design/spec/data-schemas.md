# Data schemas (structure only)

No ticket bodies, article text, or ground-truth answer text are reproduced here. Field names and enums come from `Dataset_Guide` and confirmed key presence on the JSON arrays.

## Files

| File | Records | Role |
|------|---------|------|
| `development_tickets.json` | 500 | Build + tune freely |
| `validation_tickets.json` | 80 | Self-check; same schema |
| `ground_truth_responses.json` | 200 | Reference quality checks |
| `documentation.json` | 29 | Retrieval corpus |
| Hidden set (not in pack) | ~100–120 | Grader-only; same ticket schema |

## Ticket object (dev + val)

Top-level: `ticket_id`, `channel`, `subject`, `body`, `received_at`, `customer_id`, `customer_name`, `customer_tier`, `customer_region`, `language_fluency`, `labels`, `history`.

- `channel`: `email` | `chat` | `docs_comment` | `forum` (`subject` empty for chat per guide).
- `customer_tier`: `enterprise` | `business` | `standard`.
- `customer_region`: `north_america` | `europe` | `asia_pacific` | `latin_america`.
- `language_fluency`: `fluent` | `non_fluent`.

`labels`: `intent`, `urgency` (`high`|`medium`|`low`), `expected_route` (`auto_respond`|`escalate`), `answerable_from_docs` (bool), `expected_doc_ids` (list[str]), `must_not_auto_respond` (bool).

`history` (human baseline, not a target to clone): `first_contact_resolution`, `resolution_time_minutes`, `csat_rating`, `escalated`, `repeat_contact`.

## Documentation object

`doc_id`, `title`, `category`, `applies_to`, `content`, `related_docs`, `last_reviewed_days_ago`.

Note: Setup Guide snippets may say `id`; Dataset Guide field is `doc_id`. Use `doc_id`.

## Ground-truth object

`ticket_id`, `intent`, `expected_doc_ids`, `reference_response`, `must_mention`, `must_not_claim`, `written_by`.

## Fairness segment fields

Compare quality on `customer_tier`, `customer_region`, `language_fluency` (and complexity proxies defined in the fairness audit method).

## Discovery rule

Aggregates for Stage-1 workbooks are produced by project scripts (CAP-10), not by pasting observations from interactive JSON inspection.
