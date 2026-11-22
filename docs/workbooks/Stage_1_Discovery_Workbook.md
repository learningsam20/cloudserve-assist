# Stage 1 — Discovery Workbook: CloudServe Assistant

| Field | Value |
|-------|-------|
| Author | Sameer J (sameer_j) |
| Date | 2026-11-22 |
| Client | CloudServe Solutions (fictional) |
| Template | Capstone Pack `Stage_1_Discovery_Workbook.docx` (same section and table order) |
| Interview evidence | `Stakeholder_Interviews.docx` — five transcripts (Marcus, Sofia, Daniel, Ines, Ravi) |
| Ticket evidence | `development_tickets.json` (500 tickets), aggregated only by `scripts/discovery_stats.py` |

**How the ticket figures were produced.** Run from `submission/`:

```bash
python -m scripts.discovery_stats --input ../capstone_guide/Capstone_Pack/05_Datasets/development_tickets.json
```

The script prints counts, rates and per-segment means from the `labels` and `history` fields. No ticket text was read to produce any figure in this workbook, and no figure below is estimated by hand. Where a figure is simple arithmetic on script output (for example a percentage of 500), the sum is shown. The full script output is reproduced in Appendix A.

**Row-reference convention.** Citations such as `§2.8` mean section 2, table row 8 (data rows numbered from 1 in the order shown). `§1a` is the interview table, `§1b` the disagreement table, `§1c` the "never mentioned" table.

**Caveat on timing fields.** The ticket data carries `resolution_time_minutes` (elapsed time to resolution). It has no first-response timestamp, so first-reply time cannot be measured from the data (open question OQ-1 in section 6).

## 1 Section one: what the interviews tell you

### 1a Interview summary

<!-- docx-table: 2 -->
| Who | What they told you | What they appear not to know | What you want to verify in the data |
|-----|--------------------|------------------------------|-------------------------------------|
| Marcus Adeyemi, Head of Support | About 500+ tickets a week for six agents; first response averages 8–12 hours against a 2-hour agreement; two hires and a canned-response library did not fix it (agents found searching it slower than writing); outsourcing quotes exceeded the team's cost.<br>He asked for a chatbot but really wants the response-time number down without more headcount.<br>Cares most about first contact resolution (42% now, 65% quoted benchmark) because each escalation costs about four times a resolved ticket.<br>Failure means a wrong customer-facing answer ("rather it said nothing") or more agent work than it saves.<br>Worries: enterprise customers will notice worse service; a compliance review in the autumn needs explainability. | What the tickets are actually about ("I would be guessing").<br>What is inside the escalations: he sees the rate, not the content (Daniel).<br>That the answers already exist and the real obstacle is finding them (Sofia, Ines).<br>That urgency matters differently for different tickets (Ravi). | Intent mix and whether any single topic dominates.<br>True first-contact-resolution rate (his 42%).<br>Share of escalations that were answerable from documentation.<br>Outcomes by customer tier (enterprise).<br>Whether first-response time can be computed at all. |
| Sofia Restrepo, Tier One Agent | Queue is 40–70 tickets a day, sorted by age. Familiar tickets take 4–5 minutes; unusual ones up to 40 minutes and are then escalated anyway.<br>About seven in ten could be answered without looking anything up (lockouts, rate limits, invoices, rollbacks).<br>The time goes on finding and writing the answer: documentation is good but search is painful, so each agent keeps a private file of past answers.<br>Escalates when she does not know, is not confident, or the ticket is security-related (always escalate).<br>Nervous about a wrong automated answer that she must apologise for; a draft plus the relevant page would save "half of every ticket".<br>Non-fluent English customers take longer, she sometimes answers the wrong question, and she believes they have the worst satisfaction scores. | That Ines read "I cannot find things" as "the documentation is bad".<br>Whether her seven-in-ten estimate matches the whole queue (it is her own experience).<br>Whether the non-fluent satisfaction gap is real (she says nobody has checked). | Share of tickets answerable from documentation (her 70%).<br>Whether specific topics she names (rate limits, invoices, rollbacks) are in fact the most frequent.<br>Non-fluent segment volume, resolution time, satisfaction and escalation versus fluent. |
| Daniel Okonkwo, Tier Two Engineer | About half of what reaches him is something tier one could have resolved with confidence or the right page; the other half is genuinely hard.<br>Escalations arrive as a bare forwarded ticket with no summary, so he rereads the thread and re-asks the customer things they were already asked: that causes more frustration than waiting.<br>Wants context: what the ticket is about, relevant documentation, what the agent was unsure about. "I do not need it to be right. I need it to show its working."<br>Concern: personal snippet files contain answers that were right two years ago and are not now, so training on current behaviour would scale up mistakes.<br>Would not automate security or account compromise, billing disputes (contractual), or data location. | The size of the problem across the whole escalation queue (his evidence is "tickets I closed last week").<br>Which personal-file answers are stale (he knows they exist, not which). | Share of escalations that are answerable from documentation (his "about half").<br>Share of tickets in his do-not-automate categories.<br>Resolution time and satisfaction for escalated versus first-contact tickets. |
| Ines Varga, Technical Writer | 29 support knowledge-base articles, reviewed on rotation, accurate within the review cycle, covering authentication, deployment, API, billing, data, security and account management.<br>Externally used heavily; internally she believes support does not use them at all and takes answers from memory.<br>Cause is search: keyword matching on titles, so "my deployment keeps dying" never reaches "resolving container health check failures".<br>Worried about unreviewed private answer files (asked twice for consolidation).<br>Wants every answer to name its source article so she can tell whether the article or the system's reading is wrong.<br>Not covered: feature requests, roadmap or timing, genuinely novel incidents (where a wrong answer does the most damage). | That agents see the documentation as fine and the search as the problem (Sofia's framing).<br>How much of the ticket volume the 29 articles actually cover.<br>What the private snippet files contain. | Share of tickets answerable from the 29 articles.<br>Share of tickets with no article (feature requests, unclear requests) and how they were handled.<br>That citations can be traced to a `doc_id`. |
| Ravi Menon, Customer | Support is "slow but decent once you get there". Waiting matters unequally: how pagination works can wait; a deployment failing at 9am cannot. Same queue, different cost.<br>Searches the documentation first and finds the answer about half the time; the reply that arrives later is usually the same thing.<br>Would accept an automated first response if honest: what the system thinks, the source page, a person will confirm. Confidently wrong is unacceptable.<br>Wants to know a reply was automated so he can calibrate trust.<br>A business-plan customer, he notes enterprise customers get answers in about an hour and a larger gap will come up at renewal. | How the queue is ordered internally (age, not urgency).<br>That the support team's own documentation search fails the same way his does.<br>Whether the enterprise "about an hour" is a general pattern or one colleague's experience. | Whether high-urgency tickets are resolved faster or slower than low-urgency ones.<br>Enterprise versus business versus standard resolution time and first-contact outcomes.<br>Share of tickets that are high urgency. |

### 1b Where the accounts disagree

<!-- docx-table: 3 -->
| The disagreement | Who says what | How the data settles it | What follows from the answer |
|------------------|---------------|-------------------------|------------------------------|
| 1. How many escalations tier one could have resolved | Daniel: "about half" of what reaches tier two is resolvable with confidence or the right page.<br>Marcus: reports the escalation rate and the cost of a bounce to tier two, without a view of what is inside the escalations (Daniel: he "sees the escalation rate, not what is inside"). | 281 of 500 tickets were escalated (56.2%). Of those, 138 (49.1%) were labelled answerable from documentation, and 107 (38.1%) were answerable and not in a policy do-not-automate class (`escalation_composition`). Daniel is right to within a point.<br>Source: §2.13. | A large part of the escalation load is a findability and confidence problem, not a knowledge problem. Automation can legitimately lift first-contact resolution without touching the genuinely hard tickets. The ≤30% escalation target is reachable only by routing the answerable, non-policy share. |
| 2. How repetitive the work is | Sofia: seven in ten are questions she has answered that month ("the same ones over and over", e.g. rate limits, invoices).<br>Marcus: can only name broad themes; "if you asked me for a breakdown I would be guessing". | 71.4% of tickets are answerable from documentation (357 of 500), which supports Sofia's seven in ten.<br>But the intent mix is flat: 22 intents, the largest at 5.8% (data_export, data_residency) and the smallest 2.6% (rate_limit). Sofia's own example, rate limits, is the rarest intent.<br>Source: §2.3, §2.7, §2.8. | Repetition is at the article level (29 articles cover most work), not at the topic level. A canned-response library by topic (which failed for Marcus) would need 22+ topic buckets; retrieval over the 29 articles with citations is the right shape. |
| 3. Is the documentation the problem? | Sofia: "The documentation is fine. I cannot find things in it."<br>Ines: believes she may have been heard as "the docs are bad"; says the articles are accurate and unused internally because keyword search does not match customer wording. | The data cannot grade article quality directly. It does show answers exist for 71.4% of tickets (§2.8) while 38.1% of escalations were answerable and non-policy (§2.13): the answers were available and were not used. That is consistent with a findability failure rather than a content failure. Article accuracy itself rests on Ines's review claim and will be tested by citation checks in evaluation.<br>Source: §2.8, §2.13. | Build retrieval (meaning-based, with citations) rather than rewrite content. Keep the corpus to the 29 reviewed articles, not the private snippet files. Citations let Ines tell an article error from a misreading. |
| 4. Do non-fluent customers have the worst satisfaction? | Sofia: non-fluent customers take longer and have "our worst satisfaction scores"; nobody has noticed. | 120 tickets (24.0%) are non-fluent. Satisfaction is 3.04 versus 2.95 for fluent customers (no deficit); first-contact resolution is 45.8% versus 43.2%; repeat contact 19.2% versus 22.4%. Resolution takes longer: 466.1 versus 407.7 minutes (+14%).<br>Sofia is right about extra effort and wrong about satisfaction in this sample.<br>Source: §2.9. | Do not claim a historical satisfaction gap. Keep a segment-quality check (fluency and tier) in the evaluation because the risk is the new system misreading non-fluent wording, which human history cannot show. |
| 5. One response-time number versus urgency-dependent pain | Marcus: reports a single first-response time against a 2-hour agreement.<br>Ravi: four hours is fine for a pagination question and serious for a failed deployment; "same queue, completely different cost". | High-urgency tickets are 29.2% of volume (146). They fare worse, not better: first-contact resolution 39.7% versus 48.4% for low urgency, mean resolution 478.5 versus 390.6 minutes, satisfaction 2.86 versus 3.06. Nothing in the outcomes suggests urgent tickets are prioritised.<br>Source: §2.4, §2.14. | Urgency must be an explicit output of classification and visible on escalations, and response-time reporting should be split by urgency, not averaged. |
| 6. Do enterprise customers get faster service? | Ravi: a colleague on the enterprise plan gets answers in about an hour.<br>Marcus: enterprise has a different agreement and will notice any worsening. | Enterprise customers (83 tickets, 16.6%) have the lowest first-contact resolution (37.3% versus 43.1% standard and 48.2% business), the highest escalation rate (62.7%) and the longest mean resolution (483.7 minutes). This is resolution time, not first-reply time, so the "about an hour" claim is neither confirmed nor refuted.<br>Source: §2.10. | Do not assume enterprise is already well served. Report outcomes by tier; the evaluation keeps a tier fairness check. First-reply time by tier stays an open question (OQ-1). |

### 1c What nobody said

<!-- docx-table: 4 -->
| What was never mentioned | Why you would have expected it | How you will check it |
|--------------------------|--------------------------------|-----------------------|
| Repeat contacts (the same customer returning on the same issue) | Marcus's first-contact-resolution worry implies repeats, and Daniel describes customers being re-asked; nobody cited repeat rate as a measure. | `history_overall.repeat_contact`: 21.6% of tickets are repeat contacts (§2.11). Highest on docs_comment (33.3%) and policy-restricted tickets (37.9%). |
| Which channels tickets arrive on | Marcus counts "tickets" and Sofia works "the queue", but the system must ingest email, chat, docs comments and forum posts, and each behaves differently. | Channel split (§2.2): email 42.4%, chat 31.0%, docs_comment 15.6%, forum 11.0%. docs_comment tickets have the lowest first-contact resolution (34.6%) and chat the lowest satisfaction (2.72). |
| Tickets that cannot be understood at all | Sofia describes working out what non-fluent customers mean, but nobody described what to do when intent cannot be determined. | `unclear_request` is 3.0% of tickets (15 of 500) and all were escalated (§2.3, appendix `history_by_intent`). The system must treat low-confidence classification as escalate, not guess. |
| How first-response time is measured | Marcus quotes "eight to twelve hours" and the 2-hour agreement as the reported number, but gave no definition or source. | The data has no first-response field, so this cannot be verified from tickets. Recorded as OQ-1; the evaluation will report the system's own reply latency (mean, median, p95) instead. |
| Customer region and time zone | Ravi mentions raising a ticket at 4pm and waiting until the next day; support coverage by region was never discussed. | `customer_region` exists in the ticket schema but is not in the discovery aggregates. Recorded as OQ-2; fairness checks run on tier and fluency, and region can be added to the segment report if a gap is suspected. |
| Who owns the knowledge base after launch | Ines wants source traceability, but nobody said who updates articles when a cited answer is found wrong. | No transcript answers this. The decision log records `sources_used` so Ines can trace an answer to an article; who updates articles is a client process question outside the build. |

## 2 Section two: what the ticket data shows

<!-- docx-table: 5 -->
| What to measure | Your figure | Where the figure came from | What surprised you about it |
|-----------------|-------------|----------------------------|-----------------------------|
| Total tickets in the sample | 500 | `total_tickets` (development set; the validation set has 80, not used for discovery) | Matches the order of Marcus's "north of five hundred tickets a week", so this sample is roughly one week of volume. |
| Split by channel | Email 212 (42.4%), chat 155 (31.0%), docs_comment 78 (15.6%), forum 55 (11.0%) | `channel_counts` | More than a quarter of tickets (26.6%) come from docs comments and forum posts, which nobody mentioned. |
| Split by intent category | 22 intents. Largest: data_export 29 and data_residency 29 (5.8% each), rollback_request 28, deployment_failure 27, then compliance_request, sso_configuration, security_incident and database_issue at 26 each (5.2%). Smallest: rate_limit 13 (2.6%). | `intent_counts` | The mix is nearly flat: no intent exceeds 5.8%. Sofia's examples (rate limits, invoices) are not the biggest topics. |
| Split by urgency | High 146 (29.2%), medium 226 (45.2%), low 128 (25.6%) | `urgency_counts` | Almost three in ten tickets are high urgency, yet high-urgency tickets resolve worse than low (§2.14). |
| Proportion marked resolved on first contact | 43.8% (219 of 500); escalated 56.2% (281) | `history_fcr_rate`, `history_escalated_rate` | Very close to Marcus's quoted 42%. First contact resolution and escalation are exact complements in this data. |
| Average satisfaction rating | 2.97 (mean of `csat_rating`) | `history_overall.mean_csat` | Lower than the 3.2 / 5 baseline printed in the Stage 2 template, and the gap to the ≥4.0 target is larger than the brief suggests. |
| Most frequent single question | No dominant question. Top intents are data_export and data_residency (29 each, 5.8%). | `intent_counts` (intent is the closest field to "question") | Expected a head topic. The repetition Sofia describes is at the article level, not the intent level (see §1b.2). |
| Proportion answerable from existing documentation | 71.4% (357 of 500). The other 143 (28.6%) are not answerable from documentation and were all escalated. | `answerable_from_docs_rate`; `history_by_answerable` | Confirms Sofia's seven in ten. The 143 unanswerable tickets had a first-contact resolution of exactly 0%. |
| Proportion marked non-fluent, and their outcomes | 120 tickets (24.0%). First-contact resolution 45.8% (fluent 43.2%); escalated 54.2% (56.8%); repeat contact 19.2% (22.4%); mean satisfaction 3.04 (2.95); mean resolution 466.1 min (407.7). | `fluency_counts`; `history_by_fluency` | No satisfaction deficit, contrary to Sofia. The only visible cost is 14% longer resolution. |
| Outcomes by customer tier | Standard 253 (50.6%): FCR 43.1%, escalated 56.9%, CSAT 2.98, 442.1 min. Business 164 (32.8%): FCR 48.2%, escalated 51.8%, CSAT 2.91, 358.8 min. Enterprise 83 (16.6%): FCR 37.3%, escalated 62.7%, CSAT 3.05, 483.7 min. | `tier_counts`; `history_by_tier` | Enterprise is worst on first contact and speed, which cuts against the expectation that the premium tier is better served. |
| Proportion that are repeat contacts | 21.6% | `history_overall.repeat_contact` | One in five tickets is a repeat, and repeats rise to 35.0% on tickets with no documentation answer. |
| Share that must never be auto-answered (policy) | 17.4% (87 of 500). All 87 were escalated; first-contact resolution 0%; mean resolution 693.2 min; mean satisfaction 2.63. | `must_not_auto_respond_rate`; `history_by_must_not_auto` | Matches the categories Daniel listed (security, billing disputes, data location); it is a hard ceiling on automation. |
| Composition of escalations | Of 281 escalations, 138 (49.1%) were answerable from documentation and 107 (38.1%) were answerable and not policy-restricted. | `escalation_composition` | Daniel's "about half" is confirmed. |
| Outcomes by urgency | High: FCR 39.7%, mean resolution 478.5 min, CSAT 2.86. Medium: 43.8%, 402.7 min, 2.99. Low: 48.4%, 390.6 min, 3.06. | `history_by_urgency` | Urgent tickets are slower and less satisfied. |
| Outcomes by channel | Email: FCR 44.8%, CSAT 3.08, 381.7 min. Chat: 44.5%, 2.72, 426.7 min. Docs_comment: 34.6%, 3.17, 514.7 min, repeat 33.3%. Forum: 50.9%, 2.98, 430.1 min. | `history_by_channel` | Docs comments are the slowest and most repeated; chat has the lowest satisfaction. |

The two rows the template highlights:

- **Answerable from documentation: 71.4%.** CloudServe do not lack answers; they lack a way of reaching them (§1b.3).
- **Non-fluent segment: 24.0% of volume.** Sofia's claim about satisfaction is not supported, but resolution takes 14% longer (§1b.4).

## 3 Section three: where the time actually goes

Effort is proxied by `resolution_time_minutes` summed per category (total across the 500 tickets: 210,849 minutes). This is elapsed time to resolution, not measured agent hours, so it overstates effort on tickets that waited in queue. The ranking is still informative.

<!-- docx-table: 7 -->
| Ticket category | Share of volume | Estimated share of effort | Why the two differ | Evidence for your estimate |
|-----------------|-----------------|---------------------------|--------------------|----------------------------|
| security_incident | 5.2% (26) | 9.7% | Policy forces escalation every time (Sofia, Daniel); first contact resolution 0%; mean resolution 785.9 min, the longest of all intents. | `effort_share_by_intent`; `history_by_intent` |
| compliance_request | 5.2% (26) | 8.4% | Always escalated (FCR 0%); mean resolution 679.3 min; repeat contact 42.3%; lowest satisfaction (2.35). | `effort_share_by_intent`; `history_by_intent` |
| data_residency | 5.8% (29) | 7.1% | Daniel names data location as error-prone; 69% escalated; mean resolution 515.0 min. | `effort_share_by_intent`; `history_by_intent` |
| feature_request | 4.0% (20) | 6.9% | Ines: no answer exists to retrieve; always escalated; mean resolution 723.9 min; repeat contact 50%. | `effort_share_by_intent`; `history_by_intent` |
| sso_configuration | 5.2% (26) | 2.4% | Documented procedure; 73.1% resolved at first contact; mean resolution 191.0 min; best satisfaction (3.73). | `effort_share_by_intent`; `history_by_intent` |
| onboarding | 4.4% (22) | 2.1% | Documented how-to; 72.7% first-contact resolution; mean resolution 202.1 min. | `effort_share_by_intent`; `history_by_intent` |
| rate_limit | 2.6% (13) | 0.8% | Shortest handling time (122.2 min); 76.9% first-contact resolution. | `effort_share_by_intent`; `history_by_intent` |
| All tickets not answerable from documentation | 28.6% (143) | 50.6% | Nothing to retrieve, so every one is escalated; mean resolution 746.8 min versus 291.5 min for answerable tickets. | `history_by_answerable` (sum 106,786 of 210,849 min) |
| Policy must-not-auto-respond tickets | 17.4% (87) | 28.6% | Always escalated; mean resolution 693.2 min. | `history_by_must_not_auto` (sum 60,309 of 210,849 min) |

Reading across: the four categories security_incident, compliance_request, data_residency and feature_request are 20.2% of volume and 32.0% of effort (sum of the four effort sums, 67,510 of 210,849 minutes). They are exactly the categories automation should not handle, so the bulk of the time saving must come from the 71.4% answerable tickets, which carry 49.4% of effort (104,063 of 210,849 minutes).

### The steps an agent takes on a typical ticket

Reconstructed from Sofia's interview. Only the durations she stated are recorded; others are marked as not stated rather than guessed.

<!-- docx-table: 8 -->
| Step | What the agent does | Roughly how long | Could this be automated? Say why or why not |
|------|---------------------|------------------|---------------------------------------------|
| 1 | Opens the queue (40–70 tickets) and sorts by age so the oldest, about to breach the agreement, go first. | Not stated (start-of-day set-up). | Partly. Urgency and age ordering can be shown by the system, but the order of work stays a human decision; the data shows urgency is not currently driving outcomes (§1b.5). |
| 2 | Reads the ticket and recognises whether she has answered it before. | Part of the 4–5 minutes for a familiar ticket. | Yes. Intent and urgency classification with a confidence score (rules first, then a model trained on the labelled history). |
| 3 | Finds the answer. Searching the knowledge base is painful, so she copies from a personal file of earlier answers. | Most of the time on familiar tickets; not separately stated. | Yes, and this is the step that matters. Retrieval over the 29 reviewed articles returns the passage and its `doc_id`; it replaces unreviewed private files (Daniel, Ines). |
| 4 | Writes the reply: adapts or pastes the earlier answer. | 4–5 minutes in total for a ticket she has seen before. | Yes when confident: a grounded draft with citations. Otherwise she receives the draft and the page as a starting point. Never for policy-restricted tickets. |
| 5 | Decides whether to send or escalate: does not know, not confident, or security (always escalate). | Not stated. | Yes. A fixed confidence threshold, the policy list and the kill switch decide in code, with a reason a manager can read. |
| 6 | Escalates by forwarding the original ticket with no summary; tier two rereads the thread and re-asks the customer. | Unusual tickets: up to 40 minutes before escalation. | Yes. The escalation carries a summary, the intent, the retrieved sources and what the system was unsure about (Daniel's "show its working"). |
| 7 | Handles follow-ups: answers the wrong question for non-fluent customers and goes "round again"; picks up angry replies to wrong answers. | Not stated. | No. A human stays accountable. The system's guardrails exist to reduce the number of wrong sends that cause these. |

## 4 Section four: what the client counts as success

<!-- docx-table: 9 -->
| Measure | Who watches it | Current value | What they would call success | How confident are you in this? |
|---------|----------------|---------------|------------------------------|--------------------------------|
| First contact resolution | Marcus (his preferred number) | 42% (Marcus); 43.8% in the development sample | At least 60% (success table, findings D1); the client wish-list figure is 65% | High on the baseline (two sources agree); medium on the target (two target tables in the brief conflict, resolved in D1) |
| Time to first reply | Marcus, executive team (reported against the 2-hour agreement) | 8–12 hours (Marcus, undefined); not in ticket data | Under 5 minutes mean (success table); the agreement says 2 hours | Low on the baseline: no first-response field exists (OQ-1) |
| Customer satisfaction | Marcus; per-ticket ratings | 2.97 mean in the sample (Stage 2 template baseline: 3.2 / 5) | At least 4.0 (success table); wish-list figure 4.2 | Medium: the sample mean and the template baseline disagree, and the sample ratings are from human-handled tickets |
| Escalation rate | Marcus (implicitly, via the cost of tier two) | 56.2% in the sample | No more than 30% (success table) | High on the baseline; the ceiling is bounded by 17.4% policy-restricted and 28.6% unanswerable tickets |
| Wrong or unsafe customer answers | Marcus; Ravi; Ines | Not measured today | Zero private data in replies; hallucination at most 5%; citation accuracy at least 95% (Evaluation Framework) | Medium: Marcus's failure criterion is clear, the thresholds come from the pack |
| Agent time saved per ticket | Sofia (informal) | 4–5 min on familiar tickets, up to 40 on unusual ones | "Half of every ticket" saved by a draft and a page | Low: no time-tracking data exists |
| Quality of escalation context | Daniel (informal) | Bare forwarded ticket | Escalations arrive with summary, sources and uncertainty; "twice as fast" | Low: qualitative; will be checked as a field in every escalation record |
| Fairness across segments | Marcus (enterprise worry); Ravi (renewal) | Not measured for the automated path | Less than 5 percentage points variation across tier and fluency | Medium: threshold from the Evaluation Framework |

### The sentence test

<!-- docx-table: 10 -->
| Prompt | Your answer |
|--------|-------------|
| This project will have been worth doing if, within three months of launch, ... | first contact resolution has risen from 43.8% (Marcus: 42%) to at least 60%, escalations have fallen from 56.2% to no more than 30%, first replies take minutes instead of 8–12 hours, and no customer has received a wrong answer or private data. The gain must come from the 71.4% of tickets that documentation already answers, with the same quality for enterprise and non-fluent customers. |
| We will know it did not work if we see ... | a confident wrong answer reaching a customer; auto-answered volume rising while repeat contacts rise above 21.6%; agents spending more time correcting drafts than writing from their private files (the canned-response failure Marcus described); or a gap of 5 points or more between tiers or between fluent and non-fluent customers. |
| The measure the client will actually be judged on internally is ... | first contact resolution (Marcus names it as the number he cares about), with the contractual first-response time still reported to the executive team and the autumn compliance review needing every automated decision to be explainable. |

## 5 Section five: data, constraints and risk

<!-- docx-table: 11 -->
| Data source | What it contains | Quality and gaps | Access constraints | Private data present? |
|-------------|------------------|------------------|--------------------|-----------------------|
| Support tickets | `development_tickets.json` (500) and `validation_tickets.json` (80). Fields: channel, subject, body, received time, customer id, name, tier, region, language fluency, `labels` (intent, urgency, expected route, answerable from docs, expected doc ids, must-not-auto-respond) and `history` (first contact resolution, resolution minutes, CSAT, escalated, repeat contact). Four channels. | Labels cover 22 intents; the counts show no missing intent or urgency label. History reflects human handling and is a baseline, not a target to copy (Daniel: some current answers are wrong). No first-response timestamp. Ticket text was not read by hand, by project rule; text quality is judged through classifier and evaluation results. | Pack datasets are for this capstone only. A hidden grader set with the same schema is never used for tuning; the harness takes `--input` / `--output` paths and hardcodes none. | Yes: customer id, name, tier and region fields, and free text that can contain personal or account data. Outbound replies must contain none. |
| Documentation | `documentation.json`: 29 reviewed support articles with `doc_id`, title, category, applies-to, content, related docs and last-reviewed age. | Ines reports accuracy within the review cycle. Gaps by design: feature requests, roadmap and timing, novel incidents. Search quality, not content, is the stated failure. The Setup Guide sample uses `id` where the data field is `doc_id` (findings D2). | Retrieval corpus only; replies must cite a `doc_id` from the retrieved set. | No customer data. |
| Past resolutions | Agents' private snippet files (Sofia, Daniel); the pack's `ground_truth_responses.json` (200 reference responses with required and forbidden claims) | Private files: unreviewed, partly stale (Daniel), never provided to this project and never used as a source. Ground truth: reference answers for evaluation only. | Ground truth is used only for quality checks, never retrieved at runtime. | Private files: likely. Ground truth: not expected. |
| Customer records | Customer id, name, tier, region and fluency attached to each ticket; no separate customer database. | Tier and fluency are the segments for the fairness check; region is available but not yet analysed (OQ-2). | Used for segmentation and routing context, not copied into replies. | Yes. Guardrails block outbound patterns resembling keys, card numbers and national identifiers; the evaluation reports a governance check. |
| Model provider | Generated drafts come from a hosted model through LiteLLM and OpenRouter. | Free tier only: low request-per-minute and per-day limits (about 20 per minute and 50 per day for free models). | Free-tier cost constraint; API key kept in `.env`, never committed. | Ticket text and passages leave the building only on auto-respond candidates. |
| Decision log (created by this project) | One row per automated decision with the Governance Framework fields | New data: complete by construction; reconciled against tickets processed in every harness run. | Stored locally in SQLite and exported for submission. | Contains ticket summaries; treat as internal. |

### Initial risk register

<!-- docx-table: 12 -->
| What could go wrong | How likely | How bad | Who it affects | First thought on preventing it |
|---------------------|------------|---------|----------------|--------------------------------|
| The system answers confidently and incorrectly | Medium (no human review on auto-sends) | High: Marcus's stated failure; public screenshot risk | Customers (engineers acting on a wrong answer), Sofia (apologises), Marcus | Answer only from retrieved passages; code-level check that every citation is in the retrieved set; escalate on weak retrieval or low confidence; no LLM labelling. |
| Private information appears in a reply | Low | High: compliance and customer trust | Customers, Marcus (autumn review) | Outbound pattern checks that block rather than warn; never retrieve from private files; governance scan in the evaluation. |
| Some customers get consistently worse answers | Medium | Medium to high: enterprise renewal risk (Ravi), non-fluent concerns (Sofia) | Enterprise and non-fluent customers | Measure quality gaps by tier and fluency in every evaluation run; gap limit below 5 points. |
| The documentation the system relies on goes out of date | Medium | Medium: stale answers scale (Daniel) | Customers; Ines | Retrieve only from the 29 reviewed articles; log the `doc_id` used so Ines can fix the article or the reading. |
| The provider is rate-limited or down during a run | High on the free tier | Medium | Operators; the evaluation | Timeouts, backoff, cached responses; failure becomes escalate and the batch continues. |
| Ticket text tries to instruct the system (injection) | Medium | High | Customers, CloudServe | Delimit ticket text as untrusted data; reject injection-like output; engineered test. |
| Automation keeps answering when it should be stopped | Low | High | Everyone | Kill switch checked at routing and again around generation, with no redeploy needed. |
| Threshold set from a default instead of from data | Medium | High: either mass auto-answers or mass escalations | Marcus (volume), customers (errors) | Measure on development data, freeze before the recorded evaluation, log the value on every decision. |

## 6 Section six: the problem statement

<!-- docx-table: 13 -->
| Element | Your statement | Which section and row supports it |
|---------|----------------|-----------------------------------|
| What the client asked for | A chatbot that answers the easy tickets so the six agents can do the hard ones, and brings first response time down without more headcount (Marcus). | §1a Marcus; §4 row 1–2 |
| What the evidence suggests they actually need | Not a chatbot that replies to everything. Their answers already exist: 71.4% of tickets are answerable from 29 reviewed articles that agents cannot find, and 49.1% of escalations are answerable tickets that tier one could have resolved. They need a safe first reply on the answerable, non-policy tickets, and for every other ticket an escalation that arrives with a summary, the relevant articles and the system's uncertainty. A wrong answer is worse than silence. | §2.8; §2.13; §1b.1; §1b.3; §1a Daniel, Ines, Ravi |
| The gap between those two | The ask assumes a bot that answers. The data says a fixed ceiling applies: 28.6% of tickets have no documentation answer and 17.4% must never be auto-answered, and both are always escalated. The value is in routing correctly and handing over context, not in answering more. | §2.8; §2.12; §3 rows 8–9; §1a Daniel |
| Who is affected and how | Customers wait 8–12 hours for a reply and high-urgency tickets are the worst served (29.2% of volume). Sofia loses most of each ticket to finding and rewriting a known answer. Daniel rereads threads and re-asks customers. Marcus reports a red response time and a first contact resolution of 42–43.8%. Ines cannot see which articles are used. Enterprise customers have the lowest first contact resolution (37.3%). | §2.1; §2.4; §2.10; §2.14; §1a all five |
| What will change if this is solved | First contact resolution moves from 43.8% toward at least 60%, escalations from 56.2% toward at most 30%, first replies from hours to minutes, with cited drafts for agents and context-rich escalations for tier two. Every automated decision can be explained. | §4 rows 1–4; sentence test |
| What is explicitly not in scope | Automated replies on billing disputes, security incidents, account compromise, data location or legal matters; refunds or commitments; feature requests and roadmap answers (no article exists); a consumer chat interface; replacing agents or the review of articles; learning from private snippet files; any tuning on the hidden grader set. | §1a Daniel, Ines; §2.12; §3 rows 1–4 |

### The one paragraph version

<!-- docx-table: 14 -->
| Problem statement |
|-------------------|
| CloudServe's support team already has most of the answers its customers need. Seven in ten tickets are covered by the 29 articles in the support knowledge base, but the agents cannot find them quickly, so each familiar ticket is rewritten from memory or from a personal file, replies take 8 to 12 hours against a 2-hour promise, and fewer than half of tickets are settled at first contact. Almost half of the tickets passed up to tier two are ones that could have been settled at the first line, and they arrive as a bare forwarded message, so the customer is asked the same questions again. Urgent tickets wait in the same queue as simple ones and do slightly worse. The team does not need something that answers everything: security, billing disputes, data location and unclear requests must always go to a person, and about three in ten tickets have no written answer at all. What the team needs is a way to send a short, honest, sourced first reply on the tickets that documentation already answers, and to pass every other ticket to the right person with a summary, the articles that look relevant and a note of what is uncertain. Success is a first contact resolution of at least 60%, no more than 30% of tickets escalated, replies in minutes, and no wrong answer sent. |
| **Open questions and the assumption used meanwhile.** OQ-1: first-response time is not in the ticket data; assume Marcus's 8–12 hours as the baseline and report the system's own reply latency. OQ-2: region effects were not analysed; assume region is not a driver and check if the evaluation shows a segment gap. OQ-3: the satisfaction scale is not stated in the data; assume the 1–5 scale used by the Brief baseline (3.2 / 5). OQ-4: Marcus's "four times the cost" of an escalation is not in the data; it is not used in any target. |
| **Read-back against the five transcripts.** Marcus would recognise the wrong-answer worry and the response-time number, but not the claim that his real lever is findability. Sofia would agree with the findability framing and object that the satisfaction gap for non-fluent customers does not show in the history; the workbook says so. Daniel would agree on context-rich escalation and half the escalations being resolvable, and would object if private snippet files were used as sources; they are not. Ines would recognise the findability diagnosis and want citations to say which article was used. Ravi would accept a labelled automated first reply but would not recognise any claim that enterprise customers are better served, which the data contradicts. |

## Appendix A: script output (aggregates only)

Command: `python -m scripts.discovery_stats --input ../capstone_guide/Capstone_Pack/05_Datasets/development_tickets.json` (run from `submission/`, 2026-11-22). The per-intent and per-segment lines are long; the key lines are shown and the full output is regenerated by re-running the command.

```text
total_tickets=500
channel_counts= {'chat': 155, 'docs_comment': 78, 'email': 212, 'forum': 55}
intent_counts= {'deployment_failure': 27, 'api_key_issue': 18, 'compliance_request': 26, 'rollback_request': 28, 'feature_request': 20, 'configuration_help': 17, 'authentication_failure': 20, 'data_export': 29, 'sso_configuration': 26, 'security_incident': 26, 'account_access': 22, 'api_usage_question': 24, 'database_issue': 26, 'rate_limit': 13, 'billing_query': 24, 'integration_help': 21, 'performance_degradation': 23, 'quota_or_overage': 23, 'data_residency': 29, 'webhook_issue': 21, 'unclear_request': 15, 'onboarding': 22}
urgency_counts= {'high': 146, 'medium': 226, 'low': 128}
tier_counts= {'standard': 253, 'business': 164, 'enterprise': 83}
fluency_counts= {'non_fluent': 120, 'fluent': 380}
answerable_from_docs_rate=0.714
must_not_auto_respond_rate=0.174
history_fcr_rate=0.438
history_escalated_rate=0.562
history_overall= {'n': 500, 'fcr': 0.438, 'escalated': 0.562, 'repeat_contact': 0.216, 'mean_csat': 2.97, 'mean_resolution_min': 421.7, 'sum_resolution_min': 210849}
escalation_composition= {'escalated': 281, 'escalated_and_answerable_from_docs': 138, 'escalated_answerable_and_not_must_not': 107, 'share_answerable_of_escalated': 0.491, 'share_answerable_not_must_not_of_escalated': 0.381}
```

The additional lines `history_by_tier`, `history_by_fluency`, `history_by_urgency`, `history_by_channel`, `history_by_answerable`, `history_by_must_not_auto`, `history_by_intent` and `effort_share_by_intent` supply the segment figures quoted in sections 1b, 2 and 3.
