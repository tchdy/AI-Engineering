# Task 3.1: Augmentation plan

## The gap

**Returns and Exchanges is a small queue, and most of it is not about returns.**

- The queue holds 820 of 16,338 English tickets (5.0%). Technical Support alone holds 4,737 (29.0%).
- In a random sample of 40 Returns tickets, only 3 were clearly about returning or exchanging a product. The rest were medical-data security, digital marketing, investment analytics and SaaS integration (see `label_check_notes.md`).
- A keyword shortlist (`find_seeds.py`) found 100 Returns tickets that use returns vocabulary. When I read them, 20 were genuine customer returns and 13 were business-side discussions of returns (for example "our return rates are high"). The other 67 used "returns" in the investment sense, or "exchange" in the data-exchange sense.

The same keyword filter run across all English tickets shows the vocabulary is not concentrated in this queue:

| Queue | Tickets using returns vocabulary |
|---|---|
| Returns and Exchanges | 100 of 820 (12.2%) |
| Technical Support | 32 of 4,737 (0.7%) |
| Billing and Payments | 28 of 1,595 (1.8%) |
| Customer Service | 24 of 2,410 (1.0%) |
| Product Support | 20 of 3,073 (0.7%) |
| IT Support | 14 of 1,942 (0.7%) |
| Human Resources | 2 of 348 (0.6%) |
| Service Outages and Maintenance | 1 of 664 (0.2%) |
| Sales and Pre-Sales | 1 of 513 (0.2%) |

More keyword matches sit *outside* the queue (122) than inside it (100). Many will be the same investment and data-exchange false positives, which I did not read, so this is an upper bound, not a count of misrouted returns tickets. It still shows that returns vocabulary is not a reliable signal for this label in the current data.

So a model trained on this queue sees perhaps a few dozen genuine returns tickets. Most of what it learns about "Returns and Exchanges" comes from tickets that are about something else.

As in Task 2, "genuine" means genuine by my reading of the queue name. The dataset does not define its queues.

**Gaps I am not addressing, and why.** Synthetic records cannot fix problems inside the existing records:

- label noise (similar text spread across different queues);
- formatting junk (literal `\n`, `<br>`, unfilled `[Your Name]`);
- near-duplicates.

These need cleaning or relabelling, not more data. I also checked Human Resources first and found the same problem (3 of 40 clearly HR), so the label noise looks dataset-wide rather than specific to one queue.

## Slice to add

50 English tickets in the `Returns and Exchanges` queue that are clearly about returning, exchanging or getting a refund for a product. They cover 9 situations, one per hand-picked seed:

| Scenario | Seed | What the customer wants | Records |
|---|---|---|---|
| policy_inquiry | R00081 | Return eligibility and time limits | 6 |
| defective_items | R00127 | Return one or more faulty hardware items | 6 |
| refund_delay | R00350 | A refund that is overdue under the stated policy | 6 |
| status_unclear | R00616 | Confirmation that a return was received | 6 |
| exchange_inquiry | R00460 | How to exchange an item for another version | 6 |
| portal_fault | R12297 | Fix for a returns system that customers cannot use | 5 |
| bulk_compat_return | R15558 | Start a return of several incompatible products | 5 |
| policy_change | R16249 | A more flexible return policy | 5 |
| digital_return | R28384 | Refund for software that will not install | 5 |

**How the seeds were chosen.** From the 20 genuine returns tickets on the shortlist, I kept one clean ticket per distinct situation. I excluded:

- near-duplicate copies (I used R00350, not R00717; R00616, not R00441; R15558, not R22884 or R27450; R12297, not R17537; and one ticket from the R00081/R00258/R00496/R00797 policy-question family);
- tickets with an unfilled placeholder or confused text (R00246 with `[Your Name]`; R00441, which says the item "met expectations" but is being returned; R00687);
- R00556. It is a good returns ticket but has agent reply text mixed into the customer's message.

## Generation approach

**Seed-derived templates with slot filling** (`generate_synthetic.py`):

1. Each seed defines one scenario. I wrote that scenario's sentences by hand, following the seed's structure (context → problem → what was tried → request) but in my own words. No sentence is copied.
2. Slots are filled from small invented lists: products, defects, time since purchase, refund window, return channel, product line. Greeting and closing lines are also chosen at random, and some records have neither.
3. The ticket `type` follows the seed's type. `priority` is drawn from per-scenario weights (for example, an overdue refund leans medium/high; a policy question leans low), because the dataset's own priority labels looked inconsistent in Task 2.
4. One seeded `random.Random(20261009)` drives every choice, so the output is identical on every run. No LLM or network is used.
5. Each record gets a `record_id` from `SYN-RET-001` to `SYN-RET-050`, `provenance = synthetic`, the `seed_record_id` and `scenario` it came from, and `max_seed_overlap_words`.

**Why this approach fits the gap.** The gap is a lack of *clean, on-topic* examples, not a lack of volume. Templates give full control over topic and label, so every record is a genuine returns ticket. Seeding from a hand-checked ticket per scenario keeps them grounded in what the dataset's returns tickets actually look like. Paraphrasing instead of copying or recombining source sentences avoids carrying over the source's formatting junk and placeholders.

**Built-in checks (the script stops if any fails):**
- no generated body equals any English source body;
- no generated body shares 12 or more consecutive words with any seed (the actual maximum is 6);
- all 50 bodies are distinct;
- every seed really is labelled `Returns and Exchanges`.

**Known limits, accepted for this exercise:**
- Variety is bounded by the hand-written phrase banks.
- The text is cleaner than the source: every record has a subject and none has formatting junk. A model could learn "clean text means Returns". `inspection_notes.md` returns to this.
