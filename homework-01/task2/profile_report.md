# Profile report: selected support-ticket dataset
Source: `aa_dataset-tickets-multi-lang-5-2-50-version.csv` (commit `ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb`)

## Overview

The raw file has **28,587 rows** and **16 columns** (not counting the added `record_id`).

Columns: `subject`, `body`, `answer`, `type`, `queue`, `priority`, `language`, `version`, `tag_1`, `tag_2`, `tag_3`, `tag_4`, `tag_5`, `tag_6`, `tag_7`, `tag_8`.

Rows remaining after each filter step:

| Step | Rows remaining | Rows removed |
|---|---|---|
| Raw CSV | 28,587 | – |
| `language` not missing | 28,587 | 0 |
| `language` = `en` | 16,338 | 12,249 |

Rows with a missing language are dropped because they cannot be confirmed as English. All statistics below refer to the English rows only.

**Record grain:** one row represents one customer support ticket (its subject and body), together with the queue, priority and type it was assigned. There is no ticket ID, so this is inferred: the columns contain no thread, message or sequence ID that would link rows into conversations, and almost every row (all but 3 of 16,338) has its own single `answer`, so each row looks like one self-contained ticket and reply.Caveat: there are no exact duplicates, but 8 near-duplicates appear after normalising (see Duplicate ticket texts).

`record_id` is the 1-based row position in the raw CSV (e.g. `R00001`). It is assigned before any filtering, so the same ticket has the same ID in the 20-record sample and in this report.

## Text and label fields

- **Ticket text:** `body`, the customer's message.
- **Routing label:** `queue`, the queue assigned to the ticket by the dataset's generator (the data is synthetic, so these are not real routing decisions). This is what a routing model would predict. `priority` and `type` are kept for context but are not the routing label.

`subject` is not used as the text field because it is missing in 2,607 of 16,338 English rows (16.0%), while `body` is missing in 0 (0.0%). Combining subject and body is a possible later step; it is not done here, so every text statistic below refers to `body` alone.

## Missing values

Empty strings and whitespace-only strings count as missing, in addition to true nulls. The last column shows how many of the missing values were blank strings rather than nulls.

| Field | Missing | % of English rows | Of which blank strings |
|---|---|---|---|
| `subject` | 2,607 | 16.0% | 0 |
| `body` | 0 | 0.0% | 0 |
| `queue` | 0 | 0.0% | 0 |
| `priority` | 0 | 0.0% | 0 |
| `type` | 0 | 0.0% | 0 |
| `answer` (post-outcome; not a model input) | 3 | 0.0% | 0 |

## Routing-label distribution

There are 10 distinct queues, sorted largest first. The largest (`Technical Support`) is 20.1× the size of the smallest (`General Inquiry`).

| Queue | Tickets | % of English rows |
|---|---|---|
| `Technical Support` | 4,737 | 29.0% |
| `Product Support` | 3,073 | 18.8% |
| `Customer Service` | 2,410 | 14.8% |
| `IT Support` | 1,942 | 11.9% |
| `Billing and Payments` | 1,595 | 9.8% |
| `Returns and Exchanges` | 820 | 5.0% |
| `Service Outages and Maintenance` | 664 | 4.1% |
| `Sales and Pre-Sales` | 513 | 3.1% |
| `Human Resources` | 348 | 2.1% |
| `General Inquiry` | 236 | 1.4% |
| **Total** | **16,338** | **100.0%** |

## Ticket-text length

Length is measured in **words** (whitespace-separated tokens), because word count is closer to how much information a ticket gives a person routing it. Character counts are shown alongside for reference. 0 rows with a missing `body` are excluded here.

| Statistic | Words | Characters |
|---|---|---|
| Min | 1 | 6 |
| 5th percentile | 10.0 | 72.0 |
| 25th percentile | 31.0 | 214.0 |
| 50th percentile | 55.0 | 377.0 |
| 75th percentile | 78.0 | 533.0 |
| 95th percentile | 90.0 | 604.0 |
| Max | 168 | 1,147 |
| Mean (for reference only) | 53.9 | 367.9 |

**Suspiciously short texts:** 753 tickets (4.6%) have fewer than 10 words, so the threshold flags roughly the shortest 4.6% of tickets. Of the 5 shortest examples, 4 (R07608, R00872, R01104, R01548) cannot be routed: they contain no product or problem. The fifth (R25288) is a full sentence with its spaces removed, so it is a formatting defect rather than a short ticket, and word counts undercount texts like it.

The 5 shortest:

| record_id | Words | Queue | Text |
|---|---|---|---|
| R07608 | 1 | Technical Support | System |
| R25288 | 1 | Technical Support | Thecompanyisincapableofaccessinginvestmentanalyticsduetosystemunavailability. |
| R00872 | 2 | Product Support | Requesting Assistance |
| R01104 | 2 | Technical Support | Our system |
| R01548 | 2 | Technical Support | Assistance Needed |

## Duplicate ticket texts

"Exact" means the `body` values are identical character for character (no trimming, case-folding or whitespace changes). Rows with a missing text are excluded.

- Rows whose text exactly duplicates another row's: **0**, in 0 groups.
- Redundant copies (rows that would be removed if only the first of each group were kept): **0**.
- Duplicate groups whose rows have different queues: **0**. These are label conflicts: the same text was assigned different queues.

Reported separately, and **not** part of the exact count: after normalising (lower-casing and collapsing whitespace) there are 8 redundant copies in 8 groups. This differs from the Task 1 check, which removed whitespace entirely and covered all languages, so the two counts are not directly comparable.

No exact duplicate groups found.

## Formatting artifacts in ticket text

The 20-record inspection found literal `\n` sequences and HTML `<br>` tags inside `body`. This section counts how often they occur across all English rows. A row can match more than one pattern.

| Artifact | Rows | % of English rows | First record_ids |
|---|---|---|---|
| Literal `\n` (backslash + n) | 740 | 4.5% | R00002, R00003, R00004 |
| HTML tags (e.g. `<br>`) | 520 | 3.2% | R00980, R00991, R01241 |
