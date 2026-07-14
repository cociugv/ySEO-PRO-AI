# ySEO-PRO-AI Leadership Decision Map

Canonical map for decisions that materially affect the product roadmap. Detailed execution lives in [PRODUCT_ROADMAP.md](./PRODUCT_ROADMAP.md).

## #1: Sustainability Model

Blocked by: none
Type: Grilling

### Question

How is a large free product sustained without introducing a paid feature gate?

### Answer

Accepted: the entire product remains free and open source. Maintenance is funded through voluntary sponsorships, with no sponsor-only product capabilities.

## #2: Initial User

Blocked by: #1
Type: Grilling

### Question

Who must the first useful release serve exceptionally well?

### Answer

Accepted: the SEO Operator—an AI-native technical specialist, freelancer, or agency practitioner managing roughly 5–100 sites.

## #3: Product Wedge

Blocked by: #2
Type: Grilling

### Question

What makes ySEO-PRO-AI meaningfully different from prompt collections, audit tools, and SEO data platforms?

### Answer

Accepted: evidence-to-remediation with preview, explicit approval, real application, verification, and rollback.

## #4: First Mutation Target

Blocked by: #3, #8
Type: Prototype

### Question

Should the first real target be local/Git files, WordPress, or another CMS?

### Answer

Frontier: prototype local/Git first because diff and rollback are native; validate that sequence with five SEO Operators before committing to WordPress second.

## #5: External Project Research

Blocked by: none
Type: Grilling

### Question

How can the project learn from existing repositories while remaining independently authored?

### Answer

Accepted in ADR-0001: external repositories provide behavioral research only. No external code, prompts, documentation, or assets are copied.

## #6: Runtime and Packaging

Blocked by: #3
Type: Prototype

### Question

Which runtime and packaging strategy produces the most reliable sub-five-minute activation across Windows, macOS, Linux, MCP clients, and AI terminals?

### Answer

Open: compare Python-first, Node launcher plus bundled engine, TypeScript-only, and standalone binary distributions before deciding.

## #7: Public Benchmark

Blocked by: #3
Type: Research

### Question

Which fixture corpus and metrics can fairly demonstrate accuracy, safety, and performance without copying competitor test assets?

### Answer

Open: create an original, standards-derived benchmark covering audit precision, false positives, scale, remediation verification, rollback, and adversarial content.

## #8: Remediation Safety Contract

Blocked by: #3
Type: Prototype

### Question

What exact state machine, approval policy, verification contract, and rollback guarantee must every write adapter satisfy?

### Answer

Frontier: prototype the contract with a temporary Git repository and failure injection before freezing an extension interface.

## #9: External Data Policy

Blocked by: #3, #6
Type: Research

### Question

Which official and optional providers are supported, how are credentials stored, and how does the product remain useful without paid data sources?

### Answer

Open: deterministic local audit remains complete without credentials; external data adapters are optional and bring-your-own-credentials.

## #10: Extension Model

Blocked by: #7, #8
Type: Prototype

### Question

How do contributors add rules, rule packs, target adapters, data adapters, and skills without editing orchestration code?

### Answer

Open: design only after two real implementations exist for each proposed seam.

## #11: Community Governance

Blocked by: #1
Type: Grilling

### Question

How are maintainers selected, sponsorships disclosed, safety disputes resolved, and releases approved?

### Answer

Open: begin founder-led with written contribution and security policies; define maintainer promotion criteria before v1.0.

## #12: Leadership Claim

Blocked by: #7, #10, #11
Type: Research

### Question

What objective evidence permits the project to claim leadership?

### Answer

Open: combine public benchmark leadership, verified remediation case studies, cross-platform activation, contributor health, and sustained adoption. Stars alone are insufficient.
