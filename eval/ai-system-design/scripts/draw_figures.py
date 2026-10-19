"""Deterministic editable SVG figures: blue/purple whiteboard architecture style."""

import html
import json
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "figures"
W, H = 1800, 1080
INK = "#20213f"
PURPLE = "#673ab7"
INDIGO = "#3949ab"
BLUE = "#1976d2"
LIGHT = "#e3f2fd"
LAVENDER = "#f3e5f5"


def esc(value):
    return html.escape(str(value), quote=True)


class Figure:
    def __init__(self, number, name, title, subtitle):
        self.name = f"{number:02d}-{name}"
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">{esc(subtitle)}</desc>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="none" stroke="{INDIGO}" stroke-width="1.5"/></marker></defs>
<style>text {{font-family: "Chalkboard SE", "Comic Sans MS", "Trebuchet MS", sans-serif; fill:{INK}}} .title {{font-size:43px;font-weight:700;fill:{INDIGO}}} .subtitle {{font-size:23px}} .card-title {{font-size:28px;font-weight:700;fill:{PURPLE}}} .body {{font-size:23px}} .small {{font-size:21px}} .label {{font-size:22px;fill:{INDIGO}}} .metric {{font-family:"Trebuchet MS",sans-serif;font-size:28px;font-weight:700}}</style>
<rect width="{W}" height="{H}" fill="#fff"/>
<path d="M60 34 Q850 5 1730 34 L1734 112 Q840 98 58 116Z" fill="{LIGHT}" opacity=".55"/>
<text x="75" y="80" class="title">{esc(title)}</text>
<path d="M76 99 Q700 106 1718 99" fill="none" stroke="{PURPLE}" stroke-width="4" opacity=".7"/>
<text x="78" y="142" class="subtitle">{esc(subtitle)}</text>''']

    def text(self, x, y, text, cls="body", anchor="start", color=None):
        style = f' style="fill:{color}"' if color else ""
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{style}>{esc(text)}</text>')

    def box(self, x, y, w, h, title, lines, fill=LAVENDER, badge=None):
        self.parts.append(f'<g data-card="{esc(title)}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>')
        # A second light stroke recalls the pen outlines of the existing diagrams.
        self.parts.append(f'<path d="M{x+14} {y+4} Q{x+w/2} {y-1} {x+w-15} {y+4}" fill="none" stroke="{PURPLE}" stroke-width="1" opacity=".35"/>')
        self.text(x + 24, y + 44, title, "card-title")
        yy = y + 84
        for line in lines:
            for part in textwrap.wrap(line, width=max(20, int((w - 52) / 11.9)), break_long_words=False):
                self.text(x + 25, yy, part)
                yy += 32
        if yy - 32 > y + h - 16:
            raise ValueError(f"Card text too tall: {title}")
        if badge:
            self.text(x+w-24, y+h-17, badge, "small", "end", BLUE)
        self.parts.append("</g>")

    def arrow(self, points, label=None, lx=None, ly=None, dashed=False):
        path = "M" + " L".join(f"{x},{y}" for x, y in points)
        dash = ' stroke-dasharray="9 7"' if dashed else ""
        self.parts.append(f'<path d="{path}" fill="none" stroke="{INDIGO}" stroke-width="3" marker-end="url(#arrow)"{dash}/>')
        if label:
            self.text(lx, ly, label, "label", "middle")

    def note(self, y, title, body, fill=LIGHT):
        self.parts.append(f'<rect x="75" y="{y}" width="1650" height="104" rx="18" fill="{fill}"/>')
        self.text(100, y+37, title, "card-title")
        self.text(100, y+77, body, "small")

    def save(self):
        self.text(75, 1048, "GitHub Manager · AI system design · October 14, 2026", "small")
        self.text(1725, 1048, self.name.split("-")[0], "small", "end")
        self.parts.append("</svg>")
        OUT.mkdir(exist_ok=True)
        (OUT / (self.name + ".svg")).write_text("\n".join(self.parts))


def architecture():
    f = Figure(1, "actual-system", "From GitHub evidence to user-owned organization", "Implemented local app: three logical data areas in SQLite; AWS runtime remains a separate design.")
    f.box(75, 190, 510, 205, "GitHub + OAuth App", ["Trusted identity and repository data", "Public-source verification", "Credentials stay on the server"], LIGHT)
    f.box(645, 190, 510, 205, "FastAPI + durable local jobs", ["Owner-scoped session and CSRF", "Reviewed cohort → exact run plan", "One active organization run"], LAVENDER)
    f.box(1215, 190, 510, 205, "Next.js workspace", ["Browse Projects, Topics and Tags", "Review drafts and suggestions", "Manual mappings + explicit resets"], LIGHT)
    f.arrow([(585, 290), (645, 290)])
    f.arrow([(1155, 290), (1215, 290)])
    f.box(75, 500, 510, 230, "Core · authoritative metadata", ["Stable GitHub IDs and URLs", "Inventory, access and activity", "Model cannot rewrite these fields"], LIGHT)
    f.box(645, 500, 510, 230, "Intelligence · local evidence", ["Heading-aware README selection", "RAKE phrases + source spans", "Versioned profiles and hashes"], LAVENDER)
    f.box(1215, 500, 510, 230, "Organization · durable memory", ["Canonical IDs, aliases and rules", "USER decisions and rejections", "Receipts, proposals and fences"], LIGHT)
    # Storage is accessed by the API/runner, never directly by the browser.
    f.arrow([(900, 395), (900, 445), (330, 445), (330, 500)])
    f.arrow([(900, 395), (900, 500)])
    f.arrow([(900, 445), (1470, 445), (1470, 500)])
    f.box(370, 805, 1060, 160, "LangChain → hosted OpenAI model", ["Bounded evidence + retrieved canonical candidates → strict JSON", "Tools disabled · review-first results · separate durable spending ledger"], LAVENDER)
    f.arrow([(900, 730), (900, 805)])
    f.text(75, 985, "Deferred cloud: DynamoDB Core / Intelligence / Organization + SQS workers + EventBridge.", "small")
    f.save()


def retrieval():
    f = Figure(2, "retrieval-and-generation", "Retrieve candidates, augment context, validate decisions", "Sparse candidate retrieval is implemented. Dense embeddings and a neural reranker are absent.")
    f.box(75, 190, 510, 230, "1 · Repository evidence", ["Metadata + selected README blocks", "RAKE phrases preserve source links", "Retrieval query uses all evidence"], LIGHT)
    f.box(645, 190, 510, 230, "2 · Canonical candidate search", ["Name + description + aliases", "Binary-IDF cosine + alias boost", "PROJECT 8 · TOPIC 10 · TAG 12"], LAVENDER)
    f.box(1215, 190, 510, 230, "3 · Application policy filters", ["Exclude existing accepted edges", "Exclude rejections and rule IDs", "Active concepts; Domain is derived"], LIGHT)
    f.arrow([(585, 300), (645, 300)])
    f.arrow([(1155, 300), (1215, 300)])
    f.box(1215, 545, 510, 240, "4 · Prompt augmentation", ["Metadata + first 2 purpose blocks", "Up to 8 phrases + short ID records", "System policy + strict JSON Schema", "Exact provider input-token count"], LAVENDER)
    f.box(645, 545, 510, 240, "5 · Structured generation", ["Classification model / low effort", "CLASSIFIED or NO_MATCH", "NEEDS_MORE_CONTEXT supported", "No tool loop; no automatic retry"], LIGHT)
    f.box(75, 545, 510, 240, "6 · Validate and propose", ["IDs, kinds, evidence references", "Current access / decision / fence", "Save receipt; user reviews proposal", "Reference validity ≠ entailment"], LAVENDER)
    f.arrow([(1470, 420), (1470, 545)])
    f.arrow([(1215, 665), (1155, 665)])
    f.arrow([(645, 665), (585, 665)])
    f.note(875, "A ranking stage is not automatically a reranker", "BM25 was an alternative offline candidate retriever. No dense+sparse fusion or cross-encoder was used.")
    f.save()


def chunking():
    f = Figure(3, "evidence-and-chunking", "Chunk for purpose, while keeping the source visible", "Implemented heuristic: Markdown blocks and heading filters; no fixed token windows or semantic splitter.")
    f.box(75, 190, 510, 475, "Source README + metadata", ["README ≤262,144 UTF-8 bytes", "Title / Overview / Features", "Purpose / Architecture / Use cases", "", "Installation / License / Changelog", "Code fences, image-only markup", "Untrusted instructions / secrets"], LIGHT)
    f.box(645, 190, 510, 475, "Versioned evidence profile", ["E0 metadata ≤600 characters", "Each selected block ≤700 chars", "README evidence ≤8,000 chars", "Heading + E ID + selected text", "", "RAKE: 1–4-word phrases, top 20", "Keep matching source spans only", "Profile hash + metadata hash + SHA"], LAVENDER)
    f.box(1215, 190, 510, 475, "Bounded generation context", ["E0 + first 2 non-title blocks", "At most 8 retained phrases", "Canonical candidate IDs and text", "No raw full README", "", "Classification ceiling: 2,000 input", "Taxonomy ceiling: 12,000 input", "Counts include schema + instructions"], LIGHT)
    f.arrow([(585, 400), (645, 400)])
    f.arrow([(1155, 400), (1215, 400)])
    f.note(740, "Tradeoff: predictable context, imperfect selection", "Character truncation may cut a sentence. Early blocks may omit decisive later evidence or negation.")
    f.note(875, "Versioned correction without rewriting history", "The app's v2 wrapper removes selected RST directives; frozen v1 benchmark profiles remain unchanged.", LAVENDER)
    f.save()


def loops():
    f = Figure(4, "controlled-analysis-loop", "Loop engineering: spend once, reconcile safely", "Analysis completion, label coverage, freshness and human review are independent states.")
    f.box(75, 190, 510, 215, "Exact reviewed plan", ["Operation + cohort + reason", "State / price / budget versions", "Finite calls and dollar reservation"], LIGHT)
    f.box(645, 190, 510, 215, "Durable admission guard", ["NEW → first analysis allowed", "RUNNING → no second dispatch", "Success / unknown / failure → local"], LAVENDER)
    f.box(1215, 190, 510, 215, "Explicit re-analysis", ["Live AI + reason + new preview", "Taxonomy and classification separate", "fresh=True; all safeguards retained"], LIGHT)
    f.arrow([(585, 300), (645, 300)])
    f.arrow([(1215, 300), (1155, 300)])
    f.box(75, 535, 510, 245, "Admitted inference path", ["Claim attempt before dispatch", "Count → reserve → generate", "Persist validated response receipt", "Fenced commit → human proposal"], LAVENDER)
    f.box(645, 535, 510, 245, "Offline reconciliation path", ["Apply user-approved rules", "Reuse compatible stored assignments", "Offer local canonical/alias matches", "No new AI completion claimed"], LIGHT)
    f.box(1215, 535, 510, 245, "Change and reset controls", ["Weight ≥6 AND entities ≥3", "OR at least 2 new projects", "900s window · 90s quiet · 1800s gap", "Reset invalidates old references"], LAVENDER)
    f.arrow([(825, 405), (825, 465), (330, 465), (330, 535)])
    f.arrow([(975, 405), (975, 535)])
    f.arrow([(1470, 535), (1470, 465), (1080, 465)], dashed=True)
    f.note(875, "A stale result can still be a historical processing fact", "Keep the receipt and cost; discard unsafe assignment references. Never repeat uncertain calls automatically.")
    f.save()


def budget():
    f = Figure(5, "harness-and-tokenomics", "Harness engineering: reserve before generation", "Original experiment ceiling $5; fixed request limits and adaptive run dollars are distinct controls.")
    f.box(75, 190, 510, 260, "Before any generation", ["Check public/synthetic policy", "Check auth, workspace and access", "Validate actual LangChain payload", "Count input incl. JSON Schema", "max_retries=0; no model tools"], LIGHT)
    f.box(645, 190, 510, 260, "Atomic monetary admission", ["Reserve worst-case input + output", "Include cache-write allowance", "5% headroom; integer microdollars", "Account for all outstanding holds", "Pin application price snapshot"], LAVENDER)
    f.box(1215, 190, 510, 260, "Outcome and recovery", ["Usage known → settle estimate", "Usage uncertain → retain reservation", "Bound violation → stop paid work", "Finish run → release unused hold", "Reset does not replenish money"], LIGHT)
    f.arrow([(585, 320), (645, 320)])
    f.arrow([(1155, 320), (1215, 320)])
    f.box(75, 565, 795, 220, "Fixed mode", ["Audited HTTP window + generation allowance", "Count request is a separate HTTP attempt", "Renew selected counters explicitly; preserve history", "Lifetime accounting and cumulative dollars remain"], LIGHT)
    f.box(930, 565, 795, 220, "Adaptive budget mode", ["Reviewed run hold under an operator's dollar ceiling", "Finite grant: at most 2 HTTP attempts / generation", "Transfer held money into a call reservation", "No infinite calls; no automatic paid re-analysis"], LAVENDER)
    f.note(875, "Measured 20-case round · historical Luna pricing", "16,041 input + 3,414 output tokens (702 reasoning included) → $0.003319 ledger estimate; 40 HTTP requests.")
    f.save()


def evaluation():
    f = Figure(6, "evaluation-evidence", "Evaluate retrieval, generation and the harness separately", "Measured Phase 0.5 regression results; small reused corpus limits all generalization claims.")
    f.box(75, 190, 650, 300, "Frozen benchmark and human policy", ["30 cases: 10 development + 20 evaluation", "Evaluation: 8 public + 12 synthetic", "42 concepts; 38 searchable non-Domains", "References approved; labels never in prompts", "Primary-label clarification preceded round 2", "Numeric taxonomy rubric remains missing"], LIGHT)
    f.box(75, 545, 650, 265, "What was actually measured", ["Candidate recall@8 / @10 / @12", "Multi-label micro precision / recall / F1", "Contract validity, tokens and latency", "One small representation ablation + repeat", "Fault/concurrency tests use mock transport"], LAVENDER)
    f.text(810, 220, "20-case model round · TP 50 / FP 0 / FN 2", "card-title")
    measures = [("Precision", 1.0, BLUE), ("Recall", 50/52, INDIGO), ("Micro F1", 100/102, PURPLE)]
    for idx, (label, value, color) in enumerate(measures):
        y = 270 + idx * 125
        f.text(810, y, label, "body")
        f.parts.append(f'<rect x="810" y="{y+16}" width="790" height="40" rx="10" fill="{LIGHT}"/><rect x="810" y="{y+16}" width="{790*value:.1f}" height="40" rx="10" fill="{color}"/>')
        f.text(1630, y+48, f"{value*100:.1f}%", "metric")
    f.box(810, 680, 915, 155, "Retrieval ceiling on this set", ["TF-IDF and BM25 each retrieve all 52 expected labels.", "This is shortlist coverage, not evidence of semantic correctness."], LIGHT)
    f.note(875, "Research limit: regression success is not an independent test", "No dense / reranker / contextual-retrieval trial, RAGAS score, calibrated confidence or production benchmark.", LAVENDER)
    f.save()


def contextual():
    f = Figure(7, "contextual-retrieval-comparison", "Context preservation is not Contextual Retrieval", "Anthropic's 2024 technique is a research reference; GitHub Manager has not implemented or evaluated it.")
    f.box(75, 190, 795, 320, "Implemented · deterministic repository context", ["Repository metadata + section heading", "Locally selected README text and phrase spans", "Sparse search over canonical taxonomy records", "Bounded evidence prompt → structured decisions", "No document-conditioned LLM chunk prefix", "No dense index or neural reranker"], LIGHT)
    f.box(930, 190, 795, 320, "Reference · Anthropic Contextual Retrieval", ["Whole document + chunk → explanatory context", "Prefix each chunk before embedding and BM25", "Retrieve with both contextual representations", "Optional reranking before final generation", "Published retrieval-failure results are vendor data", "Not comparable to our classification micro F1"], LAVENDER)
    f.box(75, 620, 795, 195, "Cheap first experiment · proposed", ["Add trusted repo + heading metadata to passages", "Preserve full sentences and negation", "Measure relevant-passage recall per input token"], LAVENDER)
    f.box(930, 620, 795, 195, "Higher-cost experiment · proposed", ["Generate bounded, source-checked chunk context", "Evaluate sparse / dense / fusion / reranker arms", "Include indexing cost and privacy authorization"], LIGHT)
    f.arrow([(470, 510), (470, 620)], dashed=True)
    f.arrow([(1325, 510), (1325, 620)], dashed=True)
    f.note(875, "Test the causal mechanism before adopting a larger stack", "Can added context recover missed supporting evidence without increasing false project membership or reviewer effort?")
    f.save()


def future():
    f = Figure(8, "future-experiment-roadmap", "A measured route to stronger retrieval and generation", "Proposed experiments only. Preserve the current sparse baseline and every original evaluation record.")
    f.box(75, 190, 510, 265, "A · Evidence correctness", ["Full-sentence, heading-aware packing", "Supplied-ID validation parity", "Negation and multilingual fixtures", "Numeric human rubric + adjudication", "Independent repository-level test split"], LIGHT)
    f.box(645, 190, 510, 265, "B · Retrieval ablations", ["Binary/count TF-IDF vs BM25", "Candidate caps + alias boost tuning", "Public-only dense bi-encoder trial", "Sparse+dense union with rank fusion", "ACL filters before and after retrieval"], LAVENDER)
    f.box(1215, 190, 510, 265, "C · Selective escalation", ["At most one broader retrieval pass", "Source-linked additional passages", "Rerank only when candidate set large", "Abstain if supporting evidence absent", "No learned claim without held-out eval"], LIGHT)
    f.arrow([(585, 320), (645, 320)], dashed=True)
    f.arrow([(1155, 320), (1215, 320)], dashed=True)
    f.box(75, 585, 1650, 220, "Promotion criteria · a constrained quality / cost frontier", ["Report candidate recall, passage recall, ranking quality, exact-set accuracy, project false positives and abstentions.", "Measure end-to-end tokens, indexing amortization, latency, accepted labels and human correction effort.", "Adopt a component only when its independent gain justifies added dollars, operational burden and privacy exposure.", "Distributed DynamoDB / SQS correctness remains a separate production-readiness gate."], LAVENDER)
    f.note(875, "Engineering contribution: the contract around intelligence", "Ground decisions in bounded evidence, protect user memory, retain receipts and make cost and state changes auditable.")
    f.save()


if __name__ == "__main__":
    for draw in [architecture, retrieval, chunking, loops, budget, evaluation, contextual, future]:
        draw()
    print(json.dumps({"status": "PASS", "svg_figures": 8, "size": [W, H]}))
