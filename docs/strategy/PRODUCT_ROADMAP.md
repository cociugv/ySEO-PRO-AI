# ySEO-PRO-AI Product Roadmap

## Mission

Build the most trusted free, local-first, AI-native SEO automation project: a system that turns reproducible evidence into safe, verified website improvements.

The project is community-funded through sponsorships. Core capabilities, adapters, skills, MCP tools, benchmarks, and documentation remain free and open source.

## Initial User

The initial user is an **SEO Operator**: a technical SEO specialist, freelancer, or agency practitioner who works with AI-enabled terminals and manages roughly 5–100 websites.

The first experience must optimize for this operator, not for enterprise procurement or non-technical website owners.

## Product Promise

```text
DISCOVER → SCAN → DIAGNOSE → PLAN → PREVIEW → APPROVE → APPLY → VERIFY → ROLLBACK
```

ySEO-PRO-AI is not another collection of prompts or an audit that ends with recommendations. It owns the full improvement loop.

A remediation is never reported as applied merely because content was generated. It is applied only after the intended target changed and verification passed.

## What “Top 1” Means

The project will not define leadership by feature count alone. It must lead across five measurable dimensions:

1. **Trust** — findings have evidence; writes are previewable, scoped, verifiable, and reversible.
2. **Coverage** — technical SEO, multilingual SEO, structured data, AI-search readiness, monitoring, and remediation work as one system.
3. **Distribution** — installation and first audit take less than five minutes across major AI terminals.
4. **Scale** — the same operation model handles one page, a 100-page site, and a very large site through streaming and resumable execution.
5. **Community** — external contributors can add a check, adapter, rule pack, or skill without understanding the whole repository.

The public claim “top open-source AI SEO project” should only be used after the benchmark and adoption scorecard supports it.

## Non-Negotiable Principles

- Free and open source; no premium feature gate.
- Local-first; website data stays on the operator's machine by default.
- Evidence before recommendation.
- Preview before mutation.
- Explicit approval before externally visible mutation.
- Verification after every mutation.
- Rollback for every reversible mutation.
- Multilingual behavior is part of the core model.
- Deterministic rules before model judgment.
- AI augments evidence; it does not invent evidence.
- Config over code for policies and thresholds.
- Honest tool names and honest result states.
- External repositories are research inputs only; implementation follows ADR-0001.

## The Product System

### 1. Evidence Engine

The engine collects facts without deciding what to change.

Required evidence sources:

- HTTP status, headers, redirects, response timing, content type.
- robots.txt, sitemap indexes, XML sitemaps, canonical signals, meta robots.
- Parsed HTML, rendered HTML when needed, headings, metadata, links, images.
- Structured data and visible-content consistency.
- Hreflang clusters and return-tag validation.
- Internal link graph, crawl depth, orphan candidates, duplicate clusters.
- Page templates and site-level patterns.
- Optional Search Console, GA4, PageSpeed/CrUX, IndexNow, and third-party provider data.
- Historical snapshots for drift and regression detection.

Every evidence item needs:

- source;
- collection time;
- target URL;
- normalized value;
- collection error, if any;
- freshness and confidence metadata.

### 2. Diagnosis Engine

Checks consume evidence and produce findings. A finding contains:

- stable rule ID and version;
- severity and confidence;
- affected targets;
- exact evidence;
- standards or policy reference;
- impact explanation;
- remediation availability;
- false-positive suppression reason, when suppressed.

Checks are grouped into rule packs:

- crawlability and indexability;
- status and redirect integrity;
- canonicalization and duplicate control;
- metadata and headings;
- internal links and information architecture;
- images and media;
- performance evidence;
- security signals that affect delivery or trust;
- structured data;
- multilingual and hreflang;
- JavaScript rendering;
- content quality signals;
- AI-search/GEO evidence;
- ecommerce, local business, publisher, SaaS, and programmatic SEO profiles.

Rule packs must be independently versioned and testable.

### 3. Remediation Engine

The remediation lifecycle is a state machine:

```text
PROPOSED
  → PREVIEWED
  → APPROVED
  → APPLYING
  → APPLIED
  → VERIFYING
  → VERIFIED

Failure branches:
  APPLY_FAILED
  VERIFICATION_FAILED → ROLLBACK_AVAILABLE → ROLLED_BACK
```

Each remediation contains:

- finding IDs it addresses;
- intended target and allowed scope;
- before state;
- proposed after state;
- human-readable diff;
- risk classification;
- approval requirement;
- apply adapter;
- verification recipe;
- rollback recipe;
- immutable audit record.

Initial remediation families:

- title and meta description changes;
- canonical corrections;
- robots directives;
- sitemap generation and correction;
- hreflang generation and repair;
- structured-data generation and correction;
- broken internal-link replacement;
- image alt-text proposals with human approval;
- redirects as configuration artifacts;
- content briefs and patches, never silent mass publishing.

High-risk remediations must remain proposal-only until the safety model is proven.

### 4. Target Adapters

The engine never writes directly to arbitrary targets. Adapters translate a remediation into a target-specific change.

Recommended sequence, pending Decision Map ticket #4:

1. Local files and Git-backed sites.
2. WordPress through a dedicated plugin or authenticated integration.
3. Static frameworks: Next.js, Astro, Hugo, Jekyll.
4. Shopify.
5. Generic CMS adapter contract.
6. Pull-request adapter for GitHub and GitLab.

Every write adapter must implement:

- capability discovery;
- scoped read;
- preview;
- apply;
- verify;
- rollback or an explicit irreversible classification;
- idempotency;
- redaction of secrets and personal data.

### 5. Monitoring Engine

Monitoring is incremental, not a repeated full audit.

- Store normalized snapshots and content hashes.
- Re-scan changed pages first.
- Compare rule results across versions.
- Detect new issues, resolved issues, and severity changes.
- Detect template-wide regressions.
- Create CI annotations, terminal reports, and optional notifications.
- Keep baselines explicit; never infer baseline identity from timestamp equality.

### 6. AI Layer

AI is used only where judgment adds value:

- classify page intent and page type;
- explain evidence in operator language;
- cluster duplicate or overlapping content;
- propose titles, descriptions, schema, alt text, and internal links;
- evaluate passage clarity and citation readiness;
- prioritize findings using site goals and real performance data;
- create remediation plans from deterministic findings.

AI output rules:

- cite the evidence used;
- return structured output validated against a schema;
- include model/provider/version metadata;
- expose uncertainty;
- support bring-your-own-provider and local models;
- never be required for deterministic audit functions;
- never apply a write without the remediation safety workflow.

### 7. Interfaces

All interfaces call the same operation modules and return the same result model.

#### CLI

Target experience:

```bash
yseo audit https://example.com
yseo audit https://example.com --profile saas --output html
yseo plan https://example.com
yseo apply ./yseo-plan.json --dry-run
yseo apply ./yseo-plan.json --approve medium
yseo verify ./yseo-run-id
yseo rollback ./yseo-run-id
yseo monitor https://example.com
```

Requirements:

- human-readable output and stable JSON output;
- exit codes suitable for CI;
- progress without corrupting machine output;
- resume interrupted crawls;
- offline fixtures for testing;
- shell completion;
- Windows, macOS, and Linux support.

#### MCP

Expose a small set of deep tools rather than dozens of aliases:

- `seo_capabilities`
- `seo_audit`
- `seo_get_findings`
- `seo_create_plan`
- `seo_preview_plan`
- `seo_apply_plan`
- `seo_verify_run`
- `seo_rollback_run`
- `seo_monitor`

Tool metadata must accurately identify read-only, open-world, and destructive behavior. Write tools require narrow scope and explicit approval.

#### Agent Skills

Create focused workflows rather than one enormous prompt:

- onboarding and capability discovery;
- full technical audit;
- remediation planning;
- safe apply and verify;
- multilingual audit;
- structured-data audit;
- AI-search readiness;
- migration audit;
- release regression check;
- agency client report.

Skills contain workflow guidance; the evidence and mutation behavior stay in the engine.

#### Plugin Packages

Package skills and MCP configuration together for supported agent environments. Maintain native install metadata and test fixtures for each supported surface.

#### CI

Provide reusable GitHub Actions and a generic non-interactive command:

- audit changed pages on pull requests;
- fail only on new issues above a configured severity;
- publish SARIF or annotations where appropriate;
- attach HTML and JSON artifacts;
- compare against a committed or remote baseline.

## Architecture Direction

### One Operation Model

Replace independent composition in CLI, MCP bridge, and crew agents with deep operation modules:

- Audit Operation
- Remediation Operation
- Verification Operation
- Monitoring Operation

Adapters select an operation and presentation format. They do not register stages or reconstruct internal state.

### Typed Domain Records

Replace broad mutable dictionaries with explicit records for:

- Target;
- Fetch Evidence;
- Page Evidence;
- Site Graph;
- Finding;
- Remediation;
- Execution Run;
- Verification Result;
- Snapshot and Drift Report.

Serialization belongs at adapter seams. Internal modules should not depend on presentation-specific dictionaries.

### Streaming and Persistence

Large crawls require:

- disk-backed URL frontier;
- SQLite or equivalent local persistence;
- streaming result writes;
- per-host concurrency and crawl-delay policy;
- checkpoints and resume tokens;
- deduplication by normalized URL and content hash;
- bounded memory;
- separate collection and analysis queues;
- incremental re-analysis when rule versions change.

### Runtime Packaging Decision

The current Node-to-Python subprocess design adds installation and error-handling friction. Before v0.3, prototype and benchmark:

- Python-first package with optional MCP dependency;
- Node launcher plus bundled standalone engine;
- single-runtime TypeScript implementation;
- standalone cross-platform binaries.

Select the route with the best five-minute activation, update reliability, binary size, startup time, and contributor ergonomics. Do not rewrite before measuring.

## Security Model

- Audit is read-only by default.
- Network targets are restricted to explicit hosts and discovered same-site URLs.
- Block localhost, private network, metadata endpoints, and DNS-rebinding paths unless explicitly allowed.
- Validate redirects against the same network policy.
- File writes are restricted to approved workspace roots.
- No shell command is constructed from untrusted page content.
- Secrets never appear in reports, logs, or model prompts.
- Every mutation has a risk level and approval policy.
- Public publishing, IndexNow submission, CMS writes, and Git pushes are open-world actions.
- Irreversible actions are separately identified and cannot claim rollback.
- Prompt-injection strings found in website content are treated as untrusted evidence.

## Quality System

### Test Layers

1. Parser fixtures for malformed and multilingual HTML.
2. Rule tests with positive, negative, and ambiguous cases.
3. Operation contract tests through public interfaces.
4. Adapter conformance tests.
5. Remediation apply/verify/rollback tests in temporary targets.
6. MCP schema and safety tests.
7. CLI snapshot and exit-code tests.
8. End-to-end tests against controlled fixture sites.
9. Regression corpus built from anonymized, permissioned examples.
10. Performance and memory benchmarks.

### Public Benchmark

Create `yseo-bench`, a separate reproducible corpus containing:

- static fixture pages;
- rendered JavaScript pages;
- multilingual clusters;
- canonical and redirect traps;
- valid and invalid structured data;
- template-wide defects;
- adversarial prompt-injection content;
- remediation targets with expected diffs and rollback states.

Publish precision, recall, false-positive rate, runtime, peak memory, and verified-remediation rate by release. Competitors may run the same benchmark.

### Release Gates

No release advances only because a date arrived.

#### v0.1 — Honest Core

Goal: results mean what they say.

- Consolidate audit/fix composition.
- Introduce typed findings and evidence.
- Separate generated artifacts from applied remediations.
- Remove or mark unimplemented command aliases.
- Centralize the TypeScript-to-engine adapter.
- Add unit and operation contract tests.
- Add security policy and contribution rules.

Exit gates:

- all public commands have dedicated behavior;
- no generated artifact is labeled applied;
- tests run in CI on Windows, macOS, and Linux;
- clean install is documented and reproducible.

#### v0.2 — Trustworthy Audit

Goal: best-in-class deterministic technical audit for one site.

- Disk-backed crawler and resume.
- Indexability matrix.
- Site graph and internal-link analysis.
- Duplicate and canonical clusters.
- Hreflang cluster validation.
- Structured-data validation against current rule metadata.
- HTML and JSON reports with exact evidence.
- Rule suppression and configuration.

Exit gates:

- benchmark precision target met for high-severity rules;
- 10,000-page controlled crawl completes within bounded memory;
- interruption and resume work without duplicate findings;
- reports reproduce from stored evidence.

#### v0.3 — Safe Remediation for Git/File Targets

Goal: prove the full product promise on a reversible target.

- Remediation state machine.
- Diff preview and approval policy.
- File/Git adapter.
- Verification recipes.
- Automatic rollback on failed verification where safe.
- Immutable local run history.
- Pull-request output mode.

Exit gates:

- every supported remediation has apply, verify, and rollback tests;
- 100% of simulated failed verifications leave targets restored or clearly flagged;
- repeated apply is idempotent;
- no mutation escapes the approved scope.

#### v0.4 — WordPress Adapter

Goal: make the product valuable to agencies managing real client sites.

- Capability discovery for themes and plugins.
- Authenticated read/write integration.
- Draft or staging mode.
- WordPress revisions as an additional rollback path.
- Template-aware remediations.
- Site backup and compatibility checks.

Exit gates:

- validated against a published compatibility matrix;
- no direct production write by default;
- recovery guide tested by someone other than the author;
- pilot use on permissioned sites with documented outcomes.

#### v0.5 — Universal AI Distribution

Goal: first useful result in under five minutes.

- Stable CLI package.
- MCP server with deep, truthful tools.
- Agent Skills package.
- Codex plugin with bundled skills and MCP configuration.
- Claude-compatible plugin/skill packaging.
- `npx skills add` compatible skill distribution.
- Docker and CI distribution.
- Install doctor and `seo_capabilities` diagnostics.

Exit gates:

- clean install tests on supported operating systems;
- five-minute activation benchmark passes;
- uninstall and update paths tested;
- five positive and three negative plugin test cases maintained;
- destructive tool annotations verified.

#### v0.6 — Data and Monitoring

Goal: prioritize work using real outcomes and detect regressions.

- Search Console adapter.
- PageSpeed/CrUX adapter.
- Optional GA4 adapter.
- Incremental monitoring and drift rules.
- CI regression checks.
- Provider-neutral data contracts.
- Bring-your-own-credentials storage and redaction.

Exit gates:

- audit remains useful without external credentials;
- adapter failures degrade gracefully;
- monitoring detects controlled regressions;
- provider data freshness is visible.

#### v0.7 — AI Search and Content Intelligence

Goal: evidence-based GEO/AEO rather than unverifiable scoring.

- Passage and answer extraction.
- Entity and source-coverage evidence.
- Citation-readiness checks.
- Content overlap and cannibalization clusters.
- Brief and patch generation tied to evidence.
- AI crawler access policy audit.
- Evaluation fixtures for model-assisted judgments.

Exit gates:

- every score exposes its evidence and calculation version;
- model-assisted results include confidence and can be disabled;
- no claim promises ranking or AI citation outcomes;
- generated content passes spam-policy safeguards.

#### v1.0 — Production Community Release

Goal: a stable platform others can extend confidently.

- Versioned extension contracts for checks, adapters, and rule packs.
- Migration policy and semantic versioning.
- Stable JSON schemas.
- Public benchmark dashboard.
- Contributor documentation and governance.
- Security response process.
- Long-term support policy for one stable line.

Exit gates:

- at least 20 external production pilots;
- at least 10 meaningful external contributors;
- no unresolved critical security issue;
- documented recovery from failed operations;
- stable contracts survive two minor releases.

## Scale Plan

### Tens of Thousands of Users

Local-first execution distributes crawl cost across operator machines. The project infrastructure needs to serve releases, documentation, issue triage, and optional anonymous update checks—not centrally crawl every site.

Required practices:

- reproducible signed releases;
- mirrored package distribution;
- small core downloads and optional capability packs;
- backward-compatible configuration migrations;
- crash reports and usage analytics only through explicit opt-in;
- documentation versioned with releases;
- security advisories and rapid patch releases.

### Millions of Sites

“Millions of sites” should mean aggregate operator coverage, not one centralized crawler. For an operator managing many sites:

- schedule locally or in their CI;
- reuse cached evidence;
- prioritize changed URLs;
- respect per-host budgets;
- persist and resume work;
- export machine-readable results;
- isolate credentials per target;
- never pool client data without explicit configuration.

### Very Large Individual Sites

- sitemap-first discovery;
- sampling mode before full crawl;
- template and cluster analysis;
- disk-backed frontier;
- content-hash deduplication;
- distributed execution only as an optional later adapter;
- incremental evidence updates;
- resource budgets visible to the operator.

## Adoption and Community Plan

### Repository Readiness

- Clear one-sentence value proposition.
- Five-minute quick start with a demo site.
- Animated terminal demo and sample reports.
- Architecture and security documentation.
- `CONTRIBUTING.md`, code of conduct, governance, and support policy.
- Issue templates for bugs, rules, adapters, and false positives.
- RFC template for contract changes.
- `good first issue` tasks with fixture-based acceptance criteria.
- Public roadmap and changelog.
- Automated contributor checks.

### Contribution Architecture

Make four contribution paths independent:

1. Add a rule using fixtures and metadata.
2. Add a target adapter using the conformance suite.
3. Add a data adapter using the provider contract.
4. Add or translate a skill/report without changing the engine.

Contributors should not need to edit the orchestration core for ordinary extensions.

### Launch Sequence

1. Private design partners: 5 SEO Operators, 20 sites.
2. Public alpha: evidence-first audits and benchmark.
3. Remediation beta: Git/file targets with recorded case studies.
4. Agency beta: WordPress adapter and multilingual sites.
5. Universal distribution launch: CLI, MCP, skills, plugins, CI.
6. v1.0 community launch with public benchmark and governance.

Each launch must include a reproducible demo, release notes, known limitations, and a request for one specific type of feedback.

### Sponsorship

Sponsorship funds maintenance; it never unlocks product features.

Offer sponsors:

- public recognition if requested;
- roadmap briefings without roadmap control;
- sponsor logo placement under a transparent policy;
- funding goals tied to maintainership, security audits, fixtures, translations, and documentation;
- monthly public funding and spending summaries once funding becomes material.

Avoid paid prioritization that compromises safety or rule accuracy.

## Metrics

### North-Star Metric

**Weekly Verified Remediation Runs**: runs that start from evidence, apply an approved change, and pass verification.

Collect only through explicit opt-in. Never upload URLs, page content, credentials, or remediation diffs by default.

### Activation

- install success rate;
- time to first audit;
- percentage reaching first evidence-backed finding;
- percentage creating a remediation preview;
- documentation abandonment points.

### Quality

- precision and recall by rule;
- false-positive reports by rule/version;
- verified-remediation rate;
- rollback success rate;
- crash-free run rate;
- deterministic rerun agreement;
- stale-standard incidents;
- security incidents.

### Performance

- URLs per minute by evidence mode;
- peak memory per 10,000 URLs;
- cache hit rate;
- resume recovery time;
- MCP startup and response latency;
- package size and update time.

### Community

- weekly active contributors;
- first-PR completion rate;
- median issue response time;
- external rules and adapters merged;
- documentation languages maintained;
- sponsor concentration risk.

### Adoption

- verified package downloads;
- skill/plugin installs where platforms expose them;
- active GitHub stars and forks as secondary indicators;
- case studies with reproducible before/after evidence;
- retention measured only through privacy-preserving opt-in data.

## First 90 Days

### Days 1–30: Make the Core Honest

- Freeze new public tool names.
- Remove aliases that overpromise behavior.
- Define typed evidence, finding, remediation, and run records.
- Consolidate operation composition.
- Separate generated from applied fixes.
- Centralize process transport.
- Replace assertion scripts with a real test suite.
- Add CI across operating systems.
- Create the first 50 benchmark fixtures.
- Publish security and clean-room contribution policies.

### Days 31–60: Build the Trustworthy Audit

- Implement crawler persistence and resume.
- Build indexability, canonical, sitemap, link-graph, hreflang, and schema rule packs.
- Add evidence references to every finding.
- Produce stable JSON and a self-contained HTML report.
- Add suppression and configuration.
- Run five design-partner audits and triage every false positive.
- Publish benchmark results, including weaknesses.

### Days 61–90: Prove Safe Remediation

- Implement the remediation state machine.
- Add file/Git preview, apply, verify, and rollback.
- Support a deliberately small set of high-confidence remediations.
- Add adversarial and failure-injection tests.
- Generate pull requests instead of direct production writes.
- Record three permissioned case studies.
- Begin the runtime packaging prototype and WordPress design research.

## What Not to Build Yet

- A centralized SaaS dashboard.
- Hundreds of shallow MCP tools.
- Mass AI article generation.
- Automatic backlink outreach.
- Unverified “AI visibility” scores.
- A custom browser renderer before testing established browser adapters.
- Enterprise role management.
- Distributed crawling before local streaming and resume are proven.
- Dozens of CMS adapters before one adapter conformance suite exists.

## Immediate Backlog Order

1. Fix Doctor result semantics.
2. Consolidate operation composition.
3. Introduce typed evidence and findings.
4. Centralize MCP process transport.
5. Remove false command aliases.
6. Establish pytest and TypeScript tests in CI.
7. Create benchmark fixtures.
8. Add disk-backed crawling and resume.
9. Build the remediation state machine.
10. Implement the file/Git adapter.
11. Package truthful MCP tools and skills.
12. Begin WordPress pilot integration.

## References That Govern Behavior

- Google Search Essentials: https://developers.google.com/search/docs/essentials
- Google structured data guidelines: https://developers.google.com/search/docs/appearance/structured-data/sd-policies
- Open agent skills installer and ecosystem: https://github.com/vercel-labs/skills
- Codex plugin authoring: https://learn.chatgpt.com/docs/build-plugins.md
- Codex skill authoring: https://learn.chatgpt.com/docs/build-skills.md
- Codex MCP configuration: https://developers.openai.com/codex/mcp
- Codex public plugin submission: https://learn.chatgpt.com/docs/submit-plugins.md
- Clean-room external research decision: ../adr/0001-clean-room-external-research.md

