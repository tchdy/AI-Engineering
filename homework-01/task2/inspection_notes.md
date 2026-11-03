# Task 2.1: 20-record inspection

## Selection method

The 20 records were selected by `sample_records.py` from the English rows only (16,338 rows, `language` = `en`), using seed 42. The output is `sample_20.csv`, sorted by `record_id`.

The sample combines two methods (Lesson 2, slides 21–27):

- **Targeted picks (3).** These are edge cases a small random sample would probably miss: the shortest ticket text (R07608), a ticket with no subject (R08314), and a ticket from the rarest queue, `General Inquiry` (R06686). The script also tries to pick an exact-duplicate text. It found none, because the English rows contain no exact duplicates, so it took 3 targeted picks instead of 4.
- **Random core (17).** A plain random sample (seed 42) drawn from all remaining English rows.

The `selection_method` column records which method chose each row. **All prevalence judgements below ("X of 17") use only the 17 random rows.** The targeted rows were chosen *because* they are unusual, so counting them would overstate how common problems are.

## Observations

| record_id | Method | Queue | Label fits text? | Observations |
|---|---|---|---|---|
| R00226 | random | Technical Support | yes | Asks about data integration, APIs and Python ML environments. Subject is just "Question", which tells you nothing. The body contains literal `\n\n` characters (formatting junk). No PII. Routable from the body: Technical Support. |
| R00556 | random | Returns and Exchanges | yes | Product swap request. **Junk:** halfway through, the text switches into what reads like the support agent's reply ("could you please provide the product name, serial number…"), so customer and agent text are mixed. Literal `\n\n`. No PII. Routable. |
| R02641 | random | Product Support | unclear | "Integration difficulties with various tools": no product, no detail. Could equally be Technical or IT Support. Exactly 11 words, just above the short threshold. Hard to route with confidence. |
| R02698 | random | Product Support | unclear | Reports data breaches, which sounds like a security incident for IT/Technical Support rather than Product Support. Only 8 words (below the 10-word threshold). Routable only roughly. |
| R05255 | random | Product Support | yes | Asks for documentation on "Canvas TensorFlow" for digital marketing. That product combination doesn't really exist, a sign of synthetic data. A documentation request fits Product Support. Routable. |
| R06686 | targeted: rarest queue | General Inquiry | **no** | A detailed, urgent technical problem (data integration failing due to incompatible versions, patches already tried). This is clearly Technical/Product Support, not a general inquiry. The only rare-queue example I looked at is mislabelled. |
| R06988 | random | Product Support | unclear | Patient-data security using "Django 3.2 and Kaspersky" (odd combination). Mentions patient data but contains no actual PII. Security advice would more naturally go to IT or Technical Support. |
| R07608 | targeted: shortest text | Technical Support | yes (via subject) | The body is just "System", which can't be routed. But the subject ("Experiencing Downtime on Multiple Platforms") makes it routable (Technical Support or Service Outages). **Shows the subject can rescue tickets whose body is empty of content.** |
| R08314 | targeted: missing subject | Technical Support | yes | RapidMiner integration request. No subject, but the body is clear enough to route. The body is all lower-case and its sentences have no subject ("interested in integrating…"), as if the opening words were stripped. |
| R12854 | random | Product Support | unclear | Request to improve security for hospital medical data. Same topic as R06988, also labelled Product Support; IT Support seems a better fit. No PII. |
| R16872 | random | Product Support | unclear | Digital-engagement metrics have dropped and the customer wants marketing advice. None of the 10 queues clearly covers marketing advice. Hard to route. |
| R18365 | random | Product Support | unclear | General question about digital strategies for brand growth. Reads more like General Inquiry or Sales. Labelled **high** priority, which seems odd for a general question. |
| R21512 | random | Technical Support | yes | SaaS outage blocking user logins; restarts and diagnostics already tried. Fits Technical Support, though Service Outages and Maintenance would fit equally well (the queues overlap). Routable. |
| R22722 | random | Technical Support | yes | Unauthorised access attempt on a healthcare data system. Fits Technical Support. No PII. |
| R23977 | random | Service Outages and Maintenance | **no** | Body is only "Offer guidance on securing medical data" (6 words, below threshold). Nothing about an outage, so the label doesn't fit. Subject ("Windows Security Guidelines") adds a little context. |
| R24236 | random | Technical Support | **no** | Marketing strategy isn't producing brand growth. This is not a technical problem. **Junk:** contains HTML `<br><br>` tags. |
| R24799 | random | Product Support | yes | Documentation request for integrating Adobe Sign, which the text wrongly calls a "project management SaaS" (it is an e-signature product), another synthetic-data sign. Label fits. Routable. |
| R26698 | random | IT Support | yes | Hospital data breach, asks for investigation and notification of affected parties. Fits IT Support. Mentions sensitive patient data but contains no actual PII. |
| R26828 | random | Customer Service | **no** | A technical integration problem (compatibility with software updates, restarts tried). Should be Technical or Product Support, not Customer Service. |
| R27448 | random | Technical Support | yes | Clear request for PostgreSQL 13 integration documentation. Fits. Routable. |

## Summary

- **Labels are often questionable.** In this small sample, 8 of the 17 random labels fit, 3 clearly don't (R23977, R24236, R26828) and 6 are unclear. The one rare-queue ticket (R06686) also looks mislabelled. If that pattern holds across the dataset, label noise would limit routing accuracy. These judgements rest on my own reading of the queue names: the dataset does not define what each queue covers (for example, Product Support versus Technical Support), so "doesn't fit" means "doesn't fit my reading of the queue name".
- **Similar tickets get different queues.** Five random tickets are about healthcare data security (R06988, R12854, R22722, R23977, R26698), and they are spread across four queues (Product Support ×2, Technical Support, Service Outages and Maintenance, IT Support). The queues, especially Product vs Technical Support, overlap heavily.
- **Formatting junk appears in 3 of 17** random bodies: literal `\n\n` (R00226, R00556) and HTML `<br>` (R24236). One body (R00556) also mixes in agent-reply text.
- **No personal data found** in any of the 20 rows: no names, emails, phone numbers or account numbers. Several tickets *mention* patient data without containing any. The text is clearly synthetic (invented product combinations in R05255, R06988, R24799).
- **Short bodies:** 2 of 17 random rows are under 10 words (R02698, R23977), and the shortest overall (R07608, "System") is only routable via its subject. None of the 17 random rows lacks a subject (against 16% in the full data), which is plausible for a sample this small.

**Questions this raised for 2.2:**
1. How common are literal `\n` and `<br>` artifacts across the whole dataset? Count them.
2. Should the text field be subject + body, given cases like R07608?
3. How consistent are queue labels for similar text? This sample suggests a lot of overlap between Product Support, Technical Support and IT Support.
4. What does `priority` mean here, given "high" on general questions like R18365?
