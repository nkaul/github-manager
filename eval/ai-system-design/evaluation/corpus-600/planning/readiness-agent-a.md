# Readiness agent A — OpenMRS public repository smoke check

Date: October 16, 2026. Status: **Agent startup and all five live collection gates passed.**

This was a bounded, anonymous, read-only test for `openmrs/openmrs-core`, with an eight-attempt maximum. It used seven attempted connections and received six successful HTTP responses. The first system-Python request failed during TLS certificate verification before HTTP. An explicitly authorized corrective transport attempt used the existing backend Python/httpx environment with verified TLS and succeeded. No certificate verification was disabled and no packages were installed.

## Endpoint audit

| Attempt | Exact endpoint | Status | Resource | Remaining / limit |
|---|---|---|---|---|
| 1 | `https://api.github.com/rate_limit` | TLS failure | — | — / — |
| 2 | `https://api.github.com/rate_limit` | 200 | core | 60 / 60 |
| 3 | `https://api.github.com/search/repositories?q=topic%3Aopenmrs+is%3Apublic+fork%3Afalse+archived%3Afalse&per_page=5` | 200 | search | 9 / 10 |
| 4 | `https://api.github.com/repos/openmrs/openmrs-core` | 200 | core | 59 / 60 |
| 5 | `https://api.github.com/repos/openmrs/openmrs-core/commits/master` | 200 | core | 58 / 60 |
| 6 | `https://api.github.com/repos/openmrs/openmrs-core/readme?ref=8d62ce72f2f16ac626cb156dd97fd4ec1f9a95ef` | 200 | core | 57 / 60 |
| 7 | `https://api.github.com/repos/openmrs/openmrs-core/contents/pom.xml?ref=8d62ce72f2f16ac626cb156dd97fd4ec1f9a95ef` | 200 | core | 56 / 60 |

All exact rate-limit headers, ETags and relevant last-modified headers are preserved in [readiness-agent-a.json](readiness-agent-a.json). The search `topic:openmrs is:public fork:false archived:false` returned five of 125 candidates and did not report incomplete results. This confirms discovery, not the relevance of every returned item.

## Pinned source provenance

- Numeric repository ID: `5187976`. Visibility: `public`. Default branch: `master`.
- Snapshot commit: `8d62ce72f2f16ac626cb156dd97fd4ec1f9a95ef`.
- README: `README.md`, 15,834 bytes, Git blob `4ab8e39728efde16c1575e6e78278b32617f4e98`, SHA256 `8670b931cf8f10b7aebf5c14c2507d468c26209e1e8c5d7eb0a4b179e09be635`.
- Supporting manifest: `pom.xml`, 25,556 bytes, Git blob `c44b5880493a046316be3e803429db1148aeecc1`, SHA256 `412ce768c256838733712509d798adb39ea0c9c27845ca3bdc465e8a60aaf44d`.
- GitHub license metadata: `NOASSERTION` / Other. README and manifest identify MPL 2.0 with Healthcare Disclaimer; the actual LICENSE file was outside this smoke-check scope. Review is required before redistribution.

The single short evidence excerpt is: “OpenMRS is a patient-based medical record system” — [README, line 12](https://github.com/openmrs/openmrs-core/blob/8d62ce72f2f16ac626cb156dd97fd4ec1f9a95ef/README.md#L12).

## Reading and provisional annotation

The README describes a medical-record system for health-care delivery. The manifest declares the OpenMRS Maven identity and a master project with API, web and related modules, corroborating initiative membership beyond organization ownership. This supports **Healthcare → OpenMRS**, with **Electronic Medical Records** as a candidate Topic and **Java / Maven** as candidate Tags. These are **provisional, not human-approved ground truth**. Interoperability is not assigned because this limited source sample does not establish it sufficiently. Optional infrastructure mentioned in setup instructions is not automatically a primary-purpose label.

A useful annotation nuance appeared immediately: README line 47 describes a minimum Java 8 requirement, while pinned `pom.xml` line 819 declares compiler release 21. The corpus should preserve this disagreement and source provenance; it should not silently infer a single version from whichever file is read first. The pinned [manifest](https://github.com/openmrs/openmrs-core/blob/8d62ce72f2f16ac626cb156dd97fd4ec1f9a95ef/pom.xml) provides project identity at lines 16–21, module boundaries at 53–62, license declaration at 29–34 and compiler release at 819.

## Bulk readiness and safety

Anonymous access is adequate for this smoke test. Its live core limit of 60 requests, with 56 remaining after the four repository-specific core calls, is inadequate for an uninterrupted 600-repository collection requiring roughly 2,400 core requests before enrichment and failures. The live search limit was 10, with nine remaining after the one query. Use a separately verified authenticated quota or an explicitly scheduled collection before bulk execution.

No credentials or application databases were accessed. There were no HTTP retries, package installs, clones, paid-model calls, GitHub writes or repository-content execution. The corrective transport attempt is recorded separately. Source files were read as untrusted data; no README instructions or external links were followed. No full README or manifest was placed in tracked documentation. The full crawl remains pending approval.
