# Task 1: Find and Select a Dataset

**Intended use:** Given the text of a newly arrived support ticket, route it to the appropriate support team.

## 1.1 Candidates

| Candidate | Version / retrieved | Usage terms | Ticket text · Routing label | Optional context | Usable records |
|---|---|---|---|---|---|
| [Customer Support Tickets (Tobi-Bueck)](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) | Commit `ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb`; retrieved 2026-09-30 | CC-BY-NC-4.0; non-commercial use only; attribution required | `body` (optionally `subject` prefixed) · `queue` (10 classes) | `priority`, `type`, `tag_1`–`tag_8`, `language`; exclude `answer` and `version` | 16,338 English of 28,587 total |
| [IT Support Ticket Data (parthpatil256)](https://www.kaggle.com/datasets/parthpatil256/it-support-ticket-data) | Kaggle v1 (last updated 2025-06-14); retrieved 2026-09-30 | MIT as stated on Kaggle; content appears derived from CC-BY-NC-4.0 without attribution | `Body` · `Department` (10 classes) | `Priority` (low/medium/high), `Tags`; no subject, timestamp, channel, customer context, or language field | 27,252 confirmed English rows; 11 ambiguous and 2,387 unmatched/unknown |
| [Synthetic IT Support Tickets (alexandermeau)](https://www.kaggle.com/datasets/alexandermeau/synthetic-it-support-tickets) | Kaggle v13 (last updated 2026-06-15); retrieved 2026-09-30 | MIT; no educational-analysis restriction | `submitted_title` + `submitted_description` inside `ticket` JSON · **routing label not found** | `submitted_at`, `priority`, `sla_plan`, `environment`, `applications`; exclude post-outcome fields such as `correspondence`, `diagnostics`, `root_cause`, `resolution` | 0 usable for routing: 745 rows but no routing label |

### Notes on the candidates
- **Candidate 1:** The file used is `aa_dataset-tickets-multi-lang-5-2-50-version.csv`. The Hugging Face viewer merges three CSVs into a 61,765-row, 52-queue view, but this task uses the specified file and the English subset. The older v4 file shares at least 42% (8,399/20,000) of ticket bodies exactly with v5. For the routing input, `body` is the reliable field because `subject` is empty in 2,607 of 16,338 English rows (16%); `answer` is excluded because it is the agent's post-outcome reply, and `version` is an internal generator number.
- **Candidate 2:** The file used is `IT Support Ticket Data.csv`. 20,181 of 29,650 non-empty bodies (68.06%) match Tobi-Bueck v5 after normalisation, and 27,263 of 29,650 (91.95%) match v4+v5 combined; 11 matched rows are ambiguous across languages and 2,387 are unmatched. Its `Department` values are the same 10 queues as Tobi-Bueck's `queue`, with near-identical counts, supporting that it is derived from candidate 1. The card's claims of real-world data, 6 departments, and 5 priority levels do not match the file; the actual priority values printed by the script are only low, medium, and high.
- **Candidate 3:** The routing-label search covered the top-level columns and the JSON-encoded `ticket` object; no team, queue, or assignment-group field was found. The 14 issue families described in the card are not a routing-label column. All 745 records have `status = closed`, so `correspondence`, `diagnostics`, `root_cause`, and `resolution` are post-outcome fields and would be leakage even if a routing label were available.

Evidence scripts: `compare_files.py`, `overlap_check.py`, `inspect_kaggle.py` (run from `homework-01/`).

## 1.2 Selection

**Selected:** [Customer Support Tickets (Tobi-Bueck)](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) — `aa_dataset-tickets-multi-lang-5-2-50-version.csv`

Candidates 1 and 2 contain both required fields (ticket text and routing label); candidate 3 does not because no routing-label column was found. Candidate 1 is preferred because it is the original, documented source with a clear commit, 10-class routing taxonomy, and a known English subset, whereas candidate 2 appears to be a derived copy with substantial overlap and attribution/provenance concerns. Its main weakness is that it is synthetic and its routing labels may overlap semantically—for example, Technical Support, IT Support, and Product Support can be difficult to distinguish, and the labels reflect the generator rather than real routing decisions. I accept this because it is the independent candidate with an explicit routing label, while candidate 2 appears derived from it and candidate 3 has no routing label.
