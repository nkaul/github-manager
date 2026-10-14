import json
import math
import re
import subprocess
from collections import Counter

from markdown_it import MarkdownIt
from rake_nltk import Rake
from rank_bm25 import BM25Okapi

from app.config import REPO_ROOT
from app.pretest.ai.storage import digest

# Project-authored deterministic English stopword list; no NLTK corpus download.
STOPWORDS = frozenset(
    "a an and are as at be been but by can for from has have how i if in into is it its "
    "of on or our that the their then there these they this to use used uses using was "
    "we were which will with you your also via not no".split()
)
TOKEN = re.compile(r"[\w]+(?:[-+#.][\w]+)*", re.UNICODE)
SECRET = re.compile(r"(?i)(?:api[_ -]?key|token|password|secret)\s*[=:]\s*[^\s,;]+")
INSTRUCTION = re.compile(
    r"(?i)ignore (?:all |the )?(?:previous|prior) instructions|reveal.*(?:key|secret)"
)
SECTIONS = (
    "overview",
    "about",
    "purpose",
    "feature",
    "use case",
    "architecture",
    "what is",
    "intro",
)
EXCLUDED = (
    "install",
    "license",
    "changelog",
    "quickstart",
    "usage",
    "benchmark",
    "sponsor",
    "contribut",
)


def tokens(text):
    return [word for word in TOKEN.findall(text.casefold()) if word not in STOPWORDS]


def clean(text):
    lines = [line for line in text.splitlines() if not INSTRUCTION.search(line)]
    text = SECRET.sub("[REDACTED]", " ".join(lines))
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(text.split())


def selected_evidence(repo):
    if repo.get("private") is not False or repo.get("source") not in {"SYNTHETIC", "PUBLIC_GITHUB"}:
        raise ValueError("Only explicitly public/synthetic evidence may leave the corpus loader")
    text = repo.get("readme", "")
    if len(text.encode()) > 262144:
        raise ValueError("README exceeds extraction ceiling")
    metadata = clean(
        f"{repo['name']}. {repo['description']} "
        f"Topics: {', '.join(repo['topics'][:12])}. Language: {repo['language'] or 'unknown'}"
    )
    evidence = [{"id": "E0", "section": "GITHUB_METADATA", "text": metadata[:600]}]
    section, enabled, count = "TITLE", True, 0
    stream = MarkdownIt("commonmark").parse(text)
    for index, token in enumerate(stream):
        if token.type == "heading_open" and index + 1 < len(stream):
            section = stream[index + 1].content.casefold()
            enabled = token.tag == "h1" or (
                any(word in section for word in SECTIONS)
                and not any(x in section for x in EXCLUDED)
            )
        if token.type != "inline" or not enabled:
            continue
        children = token.children or []
        content = clean(" ".join(c.content for c in children if c.type in {"text", "softbreak"}))
        if len(content) < 12:
            continue
        content = content[:700]
        if count + len(content) > 8000:
            break
        count += len(content)
        evidence.append({"id": f"E{len(evidence)}", "section": section, "text": content})
    return evidence


def rake_phrases(text, limit=20):
    extractor = Rake(
        stopwords=STOPWORDS,
        min_length=1,
        max_length=4,
        sentence_tokenizer=lambda value: re.split(r"[.!?\n]+", value),
        word_tokenizer=lambda value: TOKEN.findall(value),
    )
    extractor.extract_keywords_from_text(text)
    return [
        {"text": phrase, "score": score}
        for score, phrase in extractor.get_ranked_phrases_with_scores()[:limit]
    ]


def yake_phrases(text, limit=20):
    interpreter = REPO_ROOT / ".tools/yake/bin/python"
    if not interpreter.exists():
        raise ValueError("Isolated YAKE evaluation environment missing")
    code = (
        "import json,sys,yake; d=json.load(sys.stdin); "
        "e=yake.KeywordExtractor(lan='en',n=3,top=d['limit']); "
        "print(json.dumps([{'text':p,'score':s} for p,s in e.extract_keywords(d['text'])]))"
    )
    result = subprocess.run(
        [str(interpreter), "-c", code],
        input=json.dumps({"text": text, "limit": limit}),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    if result.returncode:
        raise ValueError("Isolated YAKE extraction failed")
    return json.loads(result.stdout)


def profile(repo, extractor="rake"):
    evidence = selected_evidence(repo)
    text = "\n".join(e["text"] for e in evidence)
    phrases = (rake_phrases if extractor == "rake" else yake_phrases)(text)
    retained, seen = [], set()
    for phrase in phrases:
        phrase["normalized"] = " ".join(tokens(phrase["text"]))
        parts = TOKEN.findall(phrase["text"])
        pattern = r"\W+".join(re.escape(part) for part in parts)
        spans = []
        for item in evidence:
            match = re.search(pattern, item["text"], re.IGNORECASE) if pattern else None
            if match:
                spans.append({"id": item["id"], "start": match.start(), "end": match.end()})
                phrase.setdefault("original", match.group())
        phrase["evidence_ids"] = [span["id"] for span in spans]
        phrase["spans"] = spans
        if spans and phrase["normalized"] not in seen:
            retained.append(phrase)
            seen.add(phrase["normalized"])
    phrases = retained
    return {
        "id": repo["id"],
        "source": repo["source"],
        "private": False,
        "extractor": extractor + "-v1",
        "evidence": evidence,
        "phrases": phrases,
        "hash": digest({"evidence": evidence, "phrases": phrases, "extractor": extractor + "-v1"}),
        "metadata_hash": digest(
            {k: repo[k] for k in ("name", "description", "topics", "language")}
        ),
        "sha": repo["sha"],
        "policy": "public_and_synthetic-v1",
    }


def compact(prof, *, representation="rake"):
    evidence = prof["evidence"]
    purposes = [e for e in evidence[1:] if e["section"] != "title"][:2]
    if not purposes:
        purposes = evidence[1:3]
    selected = [evidence[0], *purposes]
    if representation == "baseline":
        return {"evidence": selected}
    return {"evidence": selected, "phrases": [p["text"] for p in prof["phrases"][:8]]}


def document_frequency(profiles):
    counts = Counter()
    for prof in profiles:
        counts.update(set(tokens(" ".join(e["text"] for e in prof["evidence"]))))
    return dict(counts)


class Retriever:
    LIMITS = {"PROJECT": 8, "TOPIC": 10, "TAG": 12}

    def __init__(self, registry, method="bm25"):
        self.registry, self.method = registry, method
        self.ids = [ident for ident, item in registry.items() if item["kind"] in self.LIMITS]
        self.docs = [
            tokens(
                " ".join([registry[i]["name"], registry[i]["description"], *registry[i]["aliases"]])
            )
            for i in self.ids
        ]
        self.bm25 = BM25Okapi(self.docs)
        df = Counter(word for document in self.docs for word in set(document))
        self.idf = {word: math.log((1 + len(self.docs)) / (1 + n)) + 1 for word, n in df.items()}

    def candidates(self, prof, *, expanded=False):
        text = " ".join(e["text"] for e in prof["evidence"])
        query = tokens(text)
        q = set(query)
        if self.method == "bm25":
            scores = self.bm25.get_scores(query)
        else:
            scores = []
            for doc in self.docs:
                numerator = sum(self.idf[w] ** 2 for w in q & set(doc))
                denominator = math.sqrt(
                    sum(self.idf.get(w, 1) ** 2 for w in q)
                    * sum(self.idf[w] ** 2 for w in set(doc))
                )
                scores.append(numerator / denominator if denominator else 0)
        ranked = []
        for ident, score in zip(self.ids, scores, strict=True):
            item = self.registry[ident]
            aliases = [item["name"], *item["aliases"]]
            exact = any(set(tokens(alias)) <= q for alias in aliases if tokens(alias))
            if self.method == "alias":
                score = 0
            score = float(score) + 3 * exact
            if score > 0:
                ranked.append((ident, score))
        result = []
        for kind, limit in self.LIMITS.items():
            subset = [(i, s) for i, s in ranked if self.registry[i]["kind"] == kind]
            subset.sort(key=lambda pair: (-pair[1], pair[0]))
            result.extend(i for i, _ in subset[: limit * (2 if expanded else 1)])
        return result
