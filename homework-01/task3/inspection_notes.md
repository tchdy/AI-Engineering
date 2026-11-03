# Task 3.3: Inspection of generated records

## How the 10 records were chosen

`inspect_synthetic.py` does two things:

- It draws **5 records at random** (seed 7): SYN-RET-004, 010, 021, 026, 042.
- It prints warning signals for all 50 records: the most similar other record (word-set Jaccard similarity), a/an slips, title-case errors, a mix of "I" and "we" in one ticket, and a plural list described as "it".

I read the flagged records and picked the **5 most suspicious** by hand (none of them among the random 5): SYN-RET-008, 013, 034, 046, 048.

## Verdicts

| record_id | Why chosen | Scenario | Acceptable? | Issue observed |
|---|---|---|---|---|
| SYN-RET-004 | random | defective_items | yes, minor issue | Two items (wireless router, portable SSD) and one shared defect: "Each item has a problem: it arrived with visible damage to the casing." Shipping damage to both items is plausible, but the closing "Please let me know if you need any further information." repeats the request sentence before it. |
| SYN-RET-010 | random | policy_inquiry | no, until fixed | Grammar: "I bought **a external** hard drive". Otherwise a clear, realistic return-policy question. |
| SYN-RET-021 | random | refund_delay | yes | Returned a design software bundle; refund overdue against a "7 to 10 business days" policy. Coherent, specific, routable. Its 6-word overlap with the seed is the joint highest in the batch but is only a stock phrase. |
| SYN-RET-026 | random | digital_return | yes, minor issue | Written in the third person ("A customer wants to return…"), as an agent passing on a request, but it closes with "Thank you in advance for your assistance." It is unclear who is writing. The seed (R28384) has the same ambiguity, so the generator reproduced it. |
| SYN-RET-042 | random | digital_return | yes, minor issue | Same third-person voice as 026, and almost the same structure: only the product and one sentence differ. Fine on its own, but repetitive alongside 026, 031 and 050. |
| SYN-RET-008 | most similar pair (0.95) | bulk_compat_return | **no** | Every sentence matches SYN-RET-007 except "four" versus "several". It adds no new information, effectively a duplicate. The bulk_compat_return scenario has too few variants. |
| SYN-RET-013 | plural/it flag | defective_items | **no** | Three different items (USB-C hub, graphics tablet, external hard drive) are given one shared fault, described in the singular: "After setting them up, I found that **it** disconnects repeatedly." Ungrammatical and implausible. |
| SYN-RET-034 | a/an flag | policy_inquiry | **no** | "I bought **a antivirus subscription** from your store", then asks whether the **original packaging** is required. A subscription has no packaging and is not bought "from your store". A software slot was dropped into a hardware sentence. |
| SYN-RET-046 | read while checking exchanges | exchange_inquiry | **no** | "exchange the portable SSD … for **the wireless version**". A wireless SSD is not a sensible product. The exchange target is chosen without regard to the product. |
| SYN-RET-048 | mixed-voice flag; longest record (78 words) | portal_fault | yes, minor issue | An organisation writes "Several customers have told **us**…" and then closes "Please let **me** know…". The content is coherent and routable. The same mixed voice appears in 005, 018, 024 and 025. |

**Result:** 5 of 10 acceptable (4 of those with minor issues), 5 not acceptable. Among the 5 random records, 4 are acceptable. The failures cluster in the hand-picked suspicious set, as expected.

## Batch-level observations

- **Low variety within scenarios.** The six most similar pairs all have similarity ≥ 0.84 (007/008, 028/043, 001/037, 039/049, 019/030, 031/050). Nine scenarios with two or three variants per sentence are not enough for 50 records.
- **Cleaner than the source.** All 50 records have a subject (16% of real English tickets have none). None has `\n`, `<br>` or placeholders, and lengths run from 39 to 78 words (the source runs from 1 to 168). Mixed into training data, a model could learn "tidy, mid-length text means Returns and Exchanges", a spurious cue unrelated to the topic.
- **Every record is on topic.** No record drifted into another queue's subject matter, which was the main goal of the augmentation.
- **The inspection helper had a false positive.** It flagged "a USB-C hub" (SYN-RET-003, 039) as an a/an error, but "a USB" is correct because USB starts with a "you" sound. The check needs an exception list, and so does the fix in the generator.

## Proposed generator changes

1. **Correct articles.** Add an `a_or_an()` helper with exceptions for acronyms that start with a consonant sound ("a USB-C hub", "an SSD").
2. **Keep acronyms in subjects.** Replace `.title()` with a function that leaves "USB-C", "SSD" and "27-inch" unchanged ("Usb-C Hub" in 003 and 039).
3. **Make slots compatible.** Attach allowed defects and exchange targets to each product (no "wireless version" of an SSD). Use separate sentence variants for software, with no packaging and no "from your store".
4. **One defect per item, or plural grammar.** For several items, give each item its own fault, or use "two of them stop responding" instead of "it".
5. **Keep one voice per record.** Give each record a persona (customer "I", organisation "we", or agent "a customer"), and draw the greeting and closing from that persona's bank.
6. **Reject near-duplicates.** After generating a record, regenerate it if its similarity to any earlier record is above 0.80. Add more variants to bulk_compat_return and policy_change, the two weakest scenarios.
7. **Match the source where the difference is a give-away.** Leave the subject empty in about 16% of records, and widen the length range with optional detail sentences. Do *not* copy the formatting junk: that is a defect, not a feature to imitate.
8. **Check the output automatically.** Run the a/an, mixed-voice and plural checks inside `generate_synthetic.py`, so these errors stop generation the same way the copy check does.
