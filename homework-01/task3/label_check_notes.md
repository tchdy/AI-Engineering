# Task 3 prep: label checks on two small queues

Before choosing seed records, I read 40 random English tickets (seed 42) from each of two small queues, using `review_hr.py`. For each ticket I asked: *would I route this ticket to this queue?* As in Task 2, this is judged against my reading of the queue name. The dataset does not define the queues.

## Human Resources (40 of 348 read)

| Verdict | Count | record_ids |
|---|---|---|
| Clearly HR | 3 | R04509, R06419, R14358 |
| Borderline | 2 | R06022, R08789 |
| Not HR | 35 | all others |

- The clear HR tickets are about employee training programmes (R04509, R06419) and onboarding training for new hires (R14358).
- The borderline tickets ask about a SaaS product's onboarding *features*: product questions that mention employees.
- The other 35 are security incidents, marketing, data-analytics platforms, and integration or access problems.
- Two pairs are reworded near-duplicates: R04509/R06419 and R06022/R08789.
- R17059 is an agent reply, not a customer ticket. R00792 ends with an unfilled `[Your Name]`.

## Returns and Exchanges (40 of 820 read)

| Verdict | Count | record_ids |
|---|---|---|
| Clearly returns | 3 | R12297, R17537, R27450 |
| Borderline | 2 | R14729, R28242 |
| Not returns | 35 | all others |

- **Clearly returns:** customers struggling with returns and exchanges because of a system fault (R12297, R17537), and a request to start a return of several products (R27450).
- **Borderline:** unexpected subscription charges and a failed cancellation (R14729), which is closer to Billing. Returns increasing because of customer dissatisfaction (R28242), which is a business observation rather than a return request.
- **Not returns (35):** medical-data security (8), digital marketing and brand growth (13), investment analytics (7), and SaaS integration, login and features (7).
- R12297 and R17537 are reworded near-duplicates. R17709 mentions "the Returns and Exchanges category" but is an investment-analytics request.
- PII placeholders appear: `<tel_num>` (R01672, R19128) and `<name>` (R01672). R23184 reads like an agent reply.

## Conclusion

Both queues look the same: about 3 of 40 tickets (8%) clearly match the queue name, and the 3 clear ones include a near-duplicate pair. Switching queues does not escape the label noise. It appears to be a property of the dataset's small queues, not of one queue.

Seeding a generator from all tickets with a given label would therefore reproduce mostly off-topic content. Instead, `find_seeds.py` shortlists Returns tickets that use returns vocabulary (return, refund, exchange, replacement, defective…), and I pick seeds from that shortlist by hand. R00556 from the Task 2 sample (a detailed product-swap request labelled Returns and Exchanges) is a known good seed.
