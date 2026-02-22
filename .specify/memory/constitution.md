# Atlas MCP Server Constitution

## Core Principles

### I. Protocol Compliance (NON-NEGOTIABLE)

All tools, resources, and prompts exposed by the Atlas MCP Server MUST strictly conform
to the MCP specification. No proprietary extensions that break spec compatibility are
permitted. Every capability MUST be expressible through standard MCP primitives (tools,
resources, prompts). Non-compliant implementations MUST be rejected at code review.
Protocol behaviour MUST be validated against the official MCP SDK type definitions,
not inferred from runtime observation alone.

**Rationale**: MCP protocol compliance guarantees interoperability with all
MCP-capable clients (Claude Desktop, Claude Code, third-party agents) and prevents
invisible lock-in to implementation quirks that only surface in production.

### II. Tool Atomicity

Each MCP tool MUST perform exactly one well-defined operation. Tools MUST be
independently callable, independently testable, and return deterministic outputs for
identical inputs. Side effects beyond the tool's declared scope are prohibited.
Tools MUST NOT depend on shared mutable state across invocations. Multipurpose tools
that combine distinct actions into a single interface MUST be decomposed before merge.

**Rationale**: Atomic tools are composable, debuggable, and safe for AI agents to call
without unexpected cascading effects. Agents rely on stable, predictable tool contracts.

### III. Test-First (NON-NEGOTIABLE)

TDD is mandatory: tests MUST be written and reviewed before any implementation begins.
The Red-Green-Refactor cycle MUST be strictly enforced for all tool and service code.
Every MCP tool MUST have at minimum one contract test (validating its MCP schema) and
one integration test (validating runtime behaviour). Tests that are written after code
exists—or that pass without a prior failing run—are considered invalid and MUST be
rewritten to confirm the failure case first.

**Rationale**: MCP tools are invoked autonomously by AI agents. Untested tools produce
silent failures that are extremely difficult to diagnose in agentic production workflows.
Test-first discipline is the primary defence against regressions in autonomous execution.

### IV. Observability & Error Transparency

All tools MUST return structured MCP-format error responses on failure—never silent null
returns, swallowed exceptions, or unstructured strings. Every tool invocation MUST emit
a structured, machine-parseable (JSON) log entry recording: tool name, sanitised input
parameters (secrets redacted), and outcome (success / error code). Debug tracing MUST
be activatable via configuration without requiring a server restart or code change.

**Rationale**: AI agents cannot inspect server internals the way human developers can.
Transparent errors and structured logs are the primary—often only—window into server
behaviour during agentic execution. Silent failures in MCP servers are production incidents.

### V. Simplicity

Implement only what is demonstrably needed today (YAGNI). Prefer single-purpose tools
over multipurpose ones. Every abstraction layer MUST pay its weight with a concrete,
demonstrated benefit documented in the plan. Complexity beyond what the MCP specification
requires MUST be justified in the feature plan's Complexity Tracking section before code
is written. When two approaches exist, the simpler one MUST be chosen unless the tradeoff
is explicitly documented and approved.

**Rationale**: MCP servers that grow without discipline become impossible to test and
reason about autonomously. AI agents are most effective with a focused, predictable,
minimal tool surface. Complexity compounds invisibly in server-side agentic systems.

## Technical Standards

- **Runtime**: Node.js (LTS) with TypeScript — strict mode MUST be enabled; no `any` types
  without explicit justification in code comments
- **MCP SDK**: Official `@modelcontextprotocol/sdk` MUST be used for all protocol handling;
  reimplementation of MCP protocol primitives is prohibited
- **Testing**: Vitest for unit and integration tests; contract tests MUST validate MCP
  schema shapes using SDK-provided type definitions
- **Linting & Formatting**: ESLint (with TypeScript rules) and Prettier enforced in CI;
  no lint warnings or type errors may be merged to `main`
- **Package Manager**: npm with committed `package-lock.json`; mixing package managers in
  the same repository is prohibited
- **Node Version**: Pinned in `.nvmrc` and CI configuration; divergence from the pinned
  version across environments is prohibited

## Development Workflow

- All features MUST be developed on a dedicated branch following the `###-feature-name`
  naming convention
- A feature spec (`specs/###-feature-name/spec.md`) MUST exist and be reviewed before
  implementation work begins on that feature
- The `/speckit.*` command suite (specify → clarify → plan → tasks → implement) MUST be
  used for all feature development; ad-hoc implementations without design artifacts are
  not permitted
- Pull Requests MUST pass all CI gates (tests, lint, typecheck, contract tests) before
  peer review commences
- Reviewers MUST verify Constitution Check compliance (from the feature's `plan.md`)
  before approving a PR
- New MCP tools MUST include contract tests validating their schema against the MCP SDK
  type definitions before the PR is approved
- Direct commits to `main` are prohibited; all changes MUST flow through reviewed PRs

## Governance

This Constitution supersedes all other development practices, coding conventions, and
informal agreements. In any conflict between this document and other guidance, this
Constitution governs.

**Amendment Procedure**: Amendments require (1) a written rationale explaining the change,
(2) a version bump determined by the semantic versioning policy below, and (3) re-running
`/speckit.constitution` to propagate changes to all dependent templates and artifacts.

**Versioning Policy**:
- MAJOR: Backward-incompatible governance changes, principle removals, or redefinitions
  that invalidate existing compliant implementations
- MINOR: New principle or section added, or materially expanded guidance in an existing
  principle that changes compliance requirements
- PATCH: Clarifications, improved wording, typo fixes, or non-semantic refinements

**Compliance Review**: All PRs and reviews MUST verify compliance with this Constitution.
Complexity violations (Principle V) MUST be documented in the feature plan's Complexity
Tracking section prior to implementation. Agent-facing runtime guidance is maintained in
`.specify/memory/` and the generated agent context file.

**Version**: 1.0.0 | **Ratified**: 2026-02-22 | **Last Amended**: 2026-02-22
