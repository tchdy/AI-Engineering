"""Task 3.2: generate 50 synthetic Returns and Exchanges tickets.

Approach: seed-derived templates with slot filling.
  - Each of 9 hand-picked seed tickets defines one *scenario* (what the customer
    wants and why). The phrase banks for that scenario were written by hand to
    follow the seed's structure (context -> problem -> what was tried -> request),
    paraphrased rather than copied.
  - Slots (product, defect, time since purchase, ...) are filled from small
    hand-written lists, so the same scenario produces different tickets.
  - Everything is driven by one seeded random.Random, so the output is identical
    on every run. No LLM, no network.

Safety checks run on every generation (the script stops if one fails):
  - no generated body equals any English source body;
  - no generated body shares a run of NO_COPY_WORDS or more words with any seed;
  - all 50 bodies are distinct.

Usage:  python task3/generate_synthetic.py
"""
import random
import re
import sys
from pathlib import Path

import pandas as pd

TASK2_DIR = Path(__file__).resolve().parent.parent / "task2"
sys.path.insert(0, str(TASK2_DIR))

from common import HW_DIR, LABEL_FIELD, TEXT_FIELD, filter_english, load_source  # noqa: E402

SEED = 20261009
N_RECORDS = 50
TARGET_QUEUE = "Returns and Exchanges"
GENERATOR = "template_v1"
NO_COPY_WORDS = 12          # longest allowed shared word run with any seed
OUT_FILE = HW_DIR / "task3/synthetic_returns_50.csv"

# ---------------------------------------------------------------------------
# Seeds: hand-picked from task3/returns_seed_candidates.csv. One per scenario.
# Each was read in full; see augmentation_plan.md for why these and not others.
# ---------------------------------------------------------------------------
SEEDS = {
    "policy_inquiry":     "R00081",  # asks for return eligibility and time limits
    "defective_items":    "R00127",  # returning several hardware items with defects
    "refund_delay":       "R00350",  # item returned, refund overdue against policy
    "status_unclear":     "R00616",  # return started, no confirmation it was received
    "exchange_inquiry":   "R00460",  # how to exchange an item: steps, docs, shipping
    "portal_fault":       "R12297",  # customers blocked by a returns-system fault
    "bulk_compat_return": "R15558",  # start a return of several incompatible products
    "policy_change":      "R16249",  # request to make the return policy more flexible
    "digital_return":     "R28384",  # return of digital products that will not install
}

# Ticket type follows the seed's type. Priority weights are a judgement call per
# scenario (the dataset's own priority labels looked inconsistent in Task 2).
SCENARIO_META = {
    "policy_inquiry":     ("Request", {"low": 5, "medium": 4, "high": 1}),
    "defective_items":    ("Incident", {"low": 2, "medium": 5, "high": 3}),
    "refund_delay":       ("Incident", {"low": 1, "medium": 5, "high": 4}),
    "status_unclear":     ("Incident", {"low": 2, "medium": 5, "high": 3}),
    "exchange_inquiry":   ("Request", {"low": 5, "medium": 4, "high": 1}),
    "portal_fault":       ("Incident", {"low": 1, "medium": 4, "high": 5}),
    "bulk_compat_return": ("Change", {"low": 2, "medium": 6, "high": 2}),
    "policy_change":      ("Change", {"low": 5, "medium": 4, "high": 1}),
    "digital_return":     ("Incident", {"low": 3, "medium": 5, "high": 2}),
}

# ---------------------------------------------------------------------------
# Slot values (invented; no names, addresses or real account numbers)
# ---------------------------------------------------------------------------
HARDWARE = ["wireless mouse", "mechanical keyboard", "USB-C hub", "external hard drive",
            "27-inch monitor", "webcam", "noise-cancelling headset", "docking station",
            "wireless router", "laser printer", "portable SSD", "graphics tablet"]
SOFTWARE = ["project management software licence", "antivirus subscription",
            "photo editing software", "accounting software licence",
            "video conferencing add-on", "design software bundle"]
DEFECTS = ["it stops responding after a few minutes of use",
           "it arrived with visible damage to the casing",
           "it is not recognised when connected to my computer",
           "it does not match the specifications listed on your website",
           "it disconnects repeatedly during normal use",
           "one of the ports does not work"]
EXCHANGE_TARGETS = ["a different model", "the newer version", "a different colour",
                    "the wireless version", "a larger size"]
CHANNELS = ["the online returns portal", "the returns page on your website",
            "the exchange request form"]
PRODUCT_LINES = ["hardware accessories", "software licences", "networking equipment",
                 "office peripherals"]
POLICY_WINDOWS = ["5 to 7 business days", "7 to 10 business days", "10 to 14 business days"]

# ---------------------------------------------------------------------------
# Shared phrase banks
# ---------------------------------------------------------------------------
GREETINGS = ["Dear Customer Support Team,", "Dear Customer Support,", "Hello Customer Support,",
             "Customer Support,", ""]
CLOSINGS = ["Thank you for your help.", "I look forward to your reply.",
            "Thank you in advance for your assistance.",
            "Please let me know if you need any further information.", ""]

# ---------------------------------------------------------------------------
# Scenario builders: each returns (subject, list of body sentences)
# ---------------------------------------------------------------------------

def _days(rng): return rng.randint(4, 25)


def policy_inquiry(rng):
    p = rng.choice(HARDWARE + SOFTWARE)
    subject = rng.choice(["Question About Your Return Policy",
                          f"Return Eligibility for {p.title()}",
                          "How Do I Return a Recent Purchase?"])
    body = [
        rng.choice([f"I bought a {p} from your store {_days(rng)} days ago and I am thinking about returning it.",
                    f"I recently purchased a {p} and would like to know whether it can still be returned."]),
        rng.choice(["Before I start, I want to make sure I meet all the conditions.",
                    "I could not find clear information about this on your website."]),
        rng.choice(["Could you tell me how long I have to request a return, and what condition the item needs to be in?",
                    "Could you explain the time limit for returns and whether the original packaging is required?",
                    "Please let me know the eligibility rules and whether a receipt or order number is needed."]),
    ]
    return subject, body


def defective_items(rng):
    items = rng.sample(HARDWARE, rng.randint(1, 3))
    listed = items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
    plural = len(items) > 1
    subject = rng.choice([f"Return Request for Faulty {'Items' if plural else items[0].title()}",
                          "Defective Hardware Return",
                          f"Request to Return {'Several Products' if plural else 'a Product'}"])
    body = [
        f"I would like to return the {listed} I received recently.",
        rng.choice([f"{'Each item has a problem' if plural else 'The item has a problem'}: {rng.choice(DEFECTS)}.",
                    f"After setting {'them' if plural else 'it'} up, I found that {rng.choice(DEFECTS)}."]),
        rng.choice([f"{'They are' if plural else 'It is'} otherwise in good condition and I still have the original packaging.",
                    "I have tried reconnecting and restarting my computer, but the problem remains."]),
        rng.choice(["Please send me the return instructions and tell me whether a refund or replacement is possible.",
                    "Could you confirm the next steps and how long the return will take?"]),
    ]
    return subject, body


def refund_delay(rng):
    p = rng.choice(HARDWARE + SOFTWARE)
    weeks = rng.choice(["two", "three", "four"])
    window = rng.choice(POLICY_WINDOWS)
    subject = rng.choice(["Refund Not Received After Return", "Delayed Refund for Returned Item",
                          f"Refund Status for Returned {p.title()}"])
    body = [
        f"I returned a {p} {weeks} weeks ago, and the return was accepted.",
        f"Your policy says refunds are processed within {window}, but I have not received anything yet.",
        rng.choice(["I have checked my account and my emails, and there is no update on the refund.",
                    "I contacted the store once already but did not get a clear answer."]),
        rng.choice(["Could you check the status of my refund and tell me when to expect it?",
                    "Please look into this and confirm when the refund will be issued."]),
    ]
    return subject, body


def status_unclear(rng):
    p = rng.choice(HARDWARE)
    ch = rng.choice(CHANNELS)
    subject = rng.choice(["No Update on My Return", "Unclear Return Status",
                          "Return Submitted but Not Confirmed"])
    body = [
        f"I started a return for a {p} through {ch} and followed every step.",
        rng.choice(["Since then I have had no confirmation that the item was received.",
                    "The tracking shows the parcel was delivered, but the return still shows as pending."]),
        "I am not sure whether to expect a refund or a replacement, or when.",
        rng.choice(["Could you confirm whether my return has been received and processed?",
                    "Please let me know the current status and what happens next."]),
    ]
    return subject, body


def exchange_inquiry(rng):
    p = rng.choice(HARDWARE)
    target = rng.choice(EXCHANGE_TARGETS)
    subject = rng.choice([f"Exchanging a {p.title()}", "Question About Product Exchanges",
                          "How to Swap a Recent Purchase"])
    body = [
        f"I would like to exchange the {p} I bought last month for {target}.",
        rng.choice(["The item works, but it is not quite what I need.",
                    "It has not been used beyond a quick test."]),
        rng.choice(["Could you explain how the exchange works and how long it usually takes?",
                    "What documents do I need, and do I have to pay for return shipping?",
                    "Does the item need to be in its original box, and is there a price difference to pay?"]),
    ]
    return subject, body


def portal_fault(rng):
    ch = rng.choice(CHANNELS)
    subject = rng.choice(["Customers Unable to Complete Returns", "Fault in Returns System",
                          f"Error When Using {ch.replace('the ', '', 1).title()}"])
    body = [
        f"Several customers have told us they cannot complete returns or exchanges through {ch}.",
        rng.choice(["The form freezes at the last step and no return label is generated.",
                    "The request is submitted, but no confirmation email is sent.",
                    "An error message appears when they select a reason for the return."]),
        rng.choice(["The problem started after the most recent software update.",
                    "It seems to have begun after last week's system maintenance."]),
        rng.choice(["We have cleared the cache and tested different browsers, but the issue continues.",
                    "Restarting the service did not help."]),
        "Please investigate and let us know when returns can be processed normally again.",
    ]
    return subject, body


def bulk_compat_return(rng):
    n = rng.choice(["two", "three", "four", "several"])
    subject = rng.choice(["Return of Multiple Products Due to Compatibility",
                          "Start Return for Incompatible Products",
                          f"Return Request for {n.title()} Products"])
    body = [
        f"Please start a return for {n} products from our recent order.",
        rng.choice(["They are not compatible with the systems we use.",
                    "After testing, they do not work with our existing hardware and software."]),
        rng.choice(["We would prefer a refund rather than replacements.",
                    "If possible, we would like to exchange them for compatible alternatives."]),
        rng.choice(["Please tell us how to send them back.", "Let us know the next steps."]),
    ]
    return subject, body


def policy_change(rng):
    line = rng.choice(PRODUCT_LINES)
    subject = rng.choice(["Request to Update Return Policy",
                          f"Longer Return Window for {line.title()}",
                          "Suggestion to Change Return Conditions"])
    body = [
        f"We would like to request a change to the return policy for {line}.",
        rng.choice(["The current return window is too short for customers to test products properly.",
                    "Customers have told us the current conditions make returns difficult."]),
        rng.choice(["Extending the return period would improve customer satisfaction.",
                    "A more flexible policy would reduce complaints and build trust."]),
        "Could you review this request and let us know whether the policy can be updated?",
    ]
    return subject, body


def digital_return(rng):
    s = rng.choice(SOFTWARE)
    subject = rng.choice(["Return of Digital Product", f"Refund Request for {s.title()}",
                          "Unable to Install Purchased Software"])
    body = [
        rng.choice([f"A customer wants to return the {s} they purchased because it will not install.",
                    f"I would like to return the {s} I bought, as I cannot get it to install."]),
        rng.choice(["The installer stops with an error part of the way through.",
                    "It appears to be incompatible with the operating system in use."]),
        rng.choice(["The troubleshooting guide was followed, but the problem was not solved.",
                    "Reinstalling and running it as administrator did not help."]),
        "Please advise whether a refund is possible for a digital product in this situation.",
    ]
    return subject, body


BUILDERS = {name: fn for name, fn in globals().items() if name in SEEDS}


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower().replace("\\n", " "))


def longest_shared_run(a: str, b: str) -> int:
    """Length (in words) of the longest run of consecutive words shared by a and b."""
    wa, wb = _words(a), _words(b)
    best, prev = 0, [0] * (len(wb) + 1)
    for x in wa:
        cur = [0] * (len(wb) + 1)
        for j, y in enumerate(wb, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def make_record(rng: random.Random, scenario: str) -> dict:
    subject, sentences = BUILDERS[scenario](rng)
    greeting, closing = rng.choice(GREETINGS), rng.choice(CLOSINGS)
    middle = " ".join(sentences + ([closing] if closing else []))
    body = f"{greeting}\n\n{middle}" if greeting else middle
    ticket_type, weights = SCENARIO_META[scenario]
    priority = rng.choices(list(weights), weights=list(weights.values()))[0]
    return {"scenario": scenario, "seed_record_id": SEEDS[scenario], "subject": subject,
            "body": body, "priority": priority, "type": ticket_type}


def main() -> None:
    english = filter_english(load_source())
    seed_rows = english.set_index("record_id").loc[list(SEEDS.values())]
    assert (seed_rows[LABEL_FIELD] == TARGET_QUEUE).all(), "a seed is not in the target queue"
    seed_texts = dict(zip(seed_rows.index, seed_rows[TEXT_FIELD]))
    source_bodies = set(english[TEXT_FIELD].dropna())

    rng = random.Random(SEED)
    scenarios = [s for s in SEEDS for _ in range(N_RECORDS // len(SEEDS))]
    scenarios += list(SEEDS)[: N_RECORDS - len(scenarios)]   # 6,6,6,6,6,5,5,5,5
    rng.shuffle(scenarios)

    records, seen = [], set()
    for i, scenario in enumerate(scenarios, 1):
        for _attempt in range(50):
            rec = make_record(rng, scenario)
            if rec["body"] not in seen:
                break
        else:
            raise RuntimeError(f"could not make a distinct body for {scenario}")
        seen.add(rec["body"])

        assert rec["body"] not in source_bodies, "generated body copies a source ticket"
        overlap = max(longest_shared_run(rec["body"], t) for t in seed_texts.values())
        assert overlap < NO_COPY_WORDS, f"record {i} shares {overlap} consecutive words with a seed"

        records.append({"record_id": f"SYN-RET-{i:03d}", "provenance": "synthetic",
                        "generator": GENERATOR, **rec, "queue": TARGET_QUEUE,
                        "language": "en", "max_seed_overlap_words": overlap})

    out = pd.DataFrame(records)
    assert len(out) == N_RECORDS and out["record_id"].is_unique
    out.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(out)} synthetic records (seed {SEED}) to {OUT_FILE}")
    print(out["scenario"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
