# Experiment Design Document - TDD IaC Development with AI Agents

## Project: Sleep Audio Pipeline (cdk-sleep-py-qdev)

**Status**: ✅ Complete (Issues #1-12)  
**AI Agent**: Amazon Q Developer  
**Language**: Python (AWS CDK 2.x)  
**Experiment Duration**: 12 Issues  
**Created**: Part of experimental series exploring TDD + AI for Infrastructure as Code

---

## 📚 Table of Contents

- [Overview & Goals](#overview--goals)
- [Experiment Design & Setup](#experiment-design--setup)
- [Methodology](#methodology)
- [Actors & Setup](#actors--setup)
- [Meta-Prompting Strategy](#meta-prompting-strategy)
- [Issue History Summary](#issue-history-summary)
- [Key Decisions & Trade-offs](#key-decisions--trade-offs)
- [Preliminary Observations](#preliminary-observations)
- [Success Metrics](#success-metrics)
- [Conclusions & Next Steps](#conclusions--next-steps)

---

## 🎯 Overview & Goals

### Experiment Hypothesis

**Can AI agents like Amazon Q Developer effectively collaborate with human developers to build production-ready Infrastructure as Code (IaC) using strict Test-Driven Development (TDD) practices?**

### Primary Research Questions

1. **TDD Viability for IaC**: Can infrastructure code be developed test-first with the same discipline as application code?
2. **AI Agent Effectiveness**: How effectively can AI agents follow TDD workflows and maintain consistency across multiple issues?
3. **Documentation Synchronization**: Can architecture documentation remain synchronized with code through AI-assisted development?
4. **Issue-Driven Development**: Does breaking work into focused GitHub issues improve code quality and maintainability?
5. **Production Readiness**: Can TDD+AI produce infrastructure that meets production standards (security, observability, error handling)?

### Experiment Goals

1. ✅ **Strict TDD Discipline**: Every infrastructure component written test-first (Red-Green-Refactor-Document)
2. ✅ **Pure Issue-Driven**: All work driven by GitHub issues (#1-#12), no ad-hoc changes
3. ✅ **Living Documentation**: ARCHITECTURE.md synchronized with code on every change
4. ✅ **Production-Ready Output**: Complete error handling, observability, security best practices
5. ✅ **Reusable Patterns**: Extract meta-prompts and guidelines for future TDD IaC projects

---

## 🔬 Experiment Design & Setup

### Experimental Context

This project is **part of a larger experimental series** exploring TDD with AI agents:

- **Series**: 5 programming languages × 3 AI agents = 15 parallel experiments
- **This Repository**: Python + Amazon Q Developer variant
- **Related Repositories**: Similar experiments with TypeScript, Java, C#, Go (other language flavors)
- **AI Agents Under Study**: Amazon Q Developer, GitHub Copilot, and others

### This Experiment's Configuration

| Dimension | Configuration |
|-----------|---------------|
| **Language** | Python 3.9+ (tested 3.9, 3.10, 3.11, 3.12) |
| **Framework** | AWS CDK 2.x (Infrastructure as Code) |
| **AI Agent** | Amazon Q Developer (full name: Amazon Q Developer Agent) |
| **Testing Framework** | pytest with aws_cdk.assertions |
| **Development Methodology** | Strict TDD (Red-Green-Refactor-Document) |
| **Project Management** | GitHub Issues (pure issue-driven development) |
| **Architecture Documentation** | Mermaid diagrams + Markdown (living documentation) |
| **Cloud Platform** | AWS (8 services: S3, EventBridge, Step Functions, Lambda, Polly, DynamoDB, SNS, CloudWatch) |

### Control Variables

To ensure experimental validity across language variants:

- **Same Architecture**: All language variants implement identical event-driven audio processing pipeline
- **Same AWS Services**: S3, EventBridge, Step Functions, Lambda, Polly, DynamoDB, SNS, CloudWatch
- **Same TDD Workflow**: Red-Green-Refactor-Document cycle enforced consistently
- **Same Issue Structure**: 12 issues with comparable scope and complexity
- **Same Documentation Standard**: ARCHITECTURE.md with Mermaid diagrams, synchronized with code

### Independent Variables

- **Programming Language**: Python (this variant)
- **AI Agent**: Amazon Q Developer (this variant)
- **Language-Specific Patterns**: Python idioms, CDK L2 constructs, pytest conventions

---

## 📋 Methodology

### 1. Test-Driven Development (TDD) for Infrastructure

#### The Red-Green-Refactor-Document Cycle

**Core Principle**: No infrastructure code written before tests.

```
🔴 RED → 🟢 GREEN → 🔵 REFACTOR → 📝 DOCUMENT
```

**Phase 1: 🔴 RED (Write Failing Test)**
- Write CDK assertion tests that define desired infrastructure behavior
- Tests must fail for the right reason (resource doesn't exist yet)
- Use `aws_cdk.assertions.Template` for infrastructure validation
- Example: Assert S3 bucket exists with versioning enabled before creating bucket

**Phase 2: 🟢 GREEN (Minimal Implementation)**
- Write minimal CDK code to make tests pass
- No gold-plating or premature optimization
- Use CDK L2 constructs for best practices
- Example: Create S3 bucket with only properties tested

**Phase 3: 🔵 REFACTOR (Clean Up)**
- Improve code quality while keeping tests green
- Add security best practices (encryption, IAM least privilege)
- Extract constants and reusable patterns
- Add descriptive resource naming with environment suffixes

**Phase 4: 📝 DOCUMENT (Synchronize Architecture)**
- Update ARCHITECTURE.md with implemented changes
- Modify Mermaid diagrams to reflect data flow
- Mark components as implemented (✅)
- Add issue to change log with summary

### 2. Issue-Driven Development

**Principle**: Every feature starts with a GitHub issue. No ad-hoc development.

#### Issue Structure

Each issue includes:
1. **Goal**: What are we building and why?
2. **Acceptance Criteria**: Testable, specific outcomes
3. **TDD Approach**: Step-by-step test-then-implement plan
4. **Dependencies**: Which issues must complete first?
5. **Documentation Impact**: What needs updating in ARCHITECTURE.md?

#### Issue Workflow

1. Create GitHub issue with clear acceptance criteria
2. Review ARCHITECTURE.md for context
3. Write failing tests (RED phase)
4. Implement minimal code (GREEN phase)
5. Refactor for quality (REFACTOR phase)
6. Update ARCHITECTURE.md (DOCUMENT phase)
7. Create pull request with issue reference
8. Verify CI passes before merging

### 3. Architecture-as-Code with Mermaid

**Principle**: Architecture diagrams are code, stored in git, and synchronized with implementation.

#### Living Documentation Standard

- **ARCHITECTURE.md**: Single source of truth for system design
- **Mermaid Diagrams**: Embedded flowcharts showing data flow and service integration
- **Synchronization Requirement**: Diagrams updated with every infrastructure change
- **Change Log**: Every issue tracked with date, changes made, and rationale

#### Benefits Observed

1. **Visual Clarity**: Mermaid diagrams provide immediate understanding of system flow
2. **Version Control**: Architecture changes tracked in git alongside code
3. **AI Comprehension**: Mermaid text format easily parsed by AI agents for context
4. **Onboarding**: New developers can understand system quickly from diagrams

---

## 🤖 Actors & Setup

### Primary Actor: Amazon Q Developer + Python

**Full Actor Name**: Amazon Q Developer Agent (Python Language Flavor)

**Role**: AI pair programming assistant collaborating with human developer on TDD IaC

**Capabilities Utilized**:
- Code generation (CDK infrastructure constructs)
- Test generation (pytest with CDK assertions)
- Documentation assistance (Markdown, Mermaid diagrams)
- Issue workflow guidance (breaking down tasks, planning implementation)
- Pattern recognition (identifying reusable IaC patterns)

**Interaction Model**:
- **Human Developer**: Creates issues, reviews code, provides architectural direction, enforces TDD discipline
- **Q Developer**: Generates tests, implements infrastructure code, updates documentation, suggests improvements
- **Feedback Loop**: Human reviews Q's output, requests refinements, validates tests pass

### Human Developer Role

**Responsibilities**:
1. Define high-level architecture and goals
2. Create GitHub issues with acceptance criteria
3. Review and validate AI-generated code
4. Enforce TDD discipline (reject implementations without tests)
5. Make final architectural decisions
6. Verify security and production-readiness

### Development Environment

**Tools & Platforms**:
- **IDE**: Visual Studio Code with AWS Toolkit extension
- **Version Control**: GitHub (issues, pull requests, CI/CD)
- **AI Integration**: Amazon Q Developer integrated into development workflow
- **Testing**: pytest with aws-cdk.assertions library
- **CI/CD**: GitHub Actions for automated testing and validation

**Environment Configuration**:
- Python virtual environment (venv)
- AWS CDK CLI (Node.js based)
- AWS account with CDK bootstrapped
- Multi-environment support (dev/stage/prod)

---

## 🧠 Meta-Prompting Strategy

### Prompting Patterns Used

The experiment employed structured prompting patterns to guide AI collaboration. These patterns are fully documented in **[META-PROMPTS.md](META-PROMPTS.md)** and include:

#### 1. Context-Setting Prompts

**Purpose**: Establish project context at the start of each session

**Pattern**:
```
I am working on [PROJECT], a TDD-first AWS CDK project.
- Language: Python 3.12
- Framework: AWS CDK 2.x
- Testing: pytest with aws_cdk.assertions
- Philosophy: Strict TDD (Red-Green-Refactor-Document)
- Documentation: ARCHITECTURE.md is the source of truth
- Current Issue: #[N]
```

**Effectiveness**: High - Prevents context drift across sessions

#### 2. Test-First Enforcement Prompts

**Purpose**: Prevent implementation before tests

**Pattern**:
```
STOP. I am about to implement [FEATURE] without tests.
Instead, help me write a failing test that asserts:
- [EXPECTED BEHAVIOR 1]
- [EXPECTED BEHAVIOR 2]
```

**Effectiveness**: Critical - Maintains TDD discipline

#### 3. Incremental Progress Prompts

**Purpose**: Break complex issues into manageable units

**Pattern**:
```
Break down Issue #[N] into minimal testable units.
For each unit:
1. Smallest test to write?
2. Minimal code to pass?
3. Refactoring opportunities?
```

**Effectiveness**: High - Reduces overwhelm, maintains focus

#### 4. Documentation Synchronization Prompts

**Purpose**: Keep ARCHITECTURE.md in sync with code

**Pattern**:
```
I just implemented [FEATURE].
Review ARCHITECTURE.md and identify:
1. Which sections need updates?
2. Mermaid diagram changes?
3. Change log entry needed?
```

**Effectiveness**: Essential - Prevents documentation drift

### Agent Guidelines Document

**[AGENT_GUIDELINES.md](AGENT_GUIDELINES.md)** serves as a persistent instruction set for Q Developer, containing:

- TDD workflow enforcement rules
- Code style conventions (PEP 8, CDK naming patterns)
- Testing standards (assertion patterns, naming conventions)
- Security checklist (encryption, IAM, input validation)
- Pull request requirements

**Impact**: Provides consistent behavioral expectations across all issues

---

## 📊 Issue History Summary

### Timeline: Issues #1-12

#### Foundation Issues (#1-3)

**Issue #1: Initial Setup**
- Established project structure and CI/CD pipeline
- Set up pytest with aws-cdk.assertions
- Configured GitHub Actions for automated testing
- **Key Learning**: Foundation setup critical for TDD success

**Issue #2: Architecture Documentation**
- Created comprehensive ARCHITECTURE.md with Mermaid diagram
- Documented all AWS services and rationale
- Defined multi-environment strategy (dev/stage/prod)
- **Key Learning**: Early documentation prevents architectural drift

**Issue #3: Foundational Infrastructure (TDD)**
- **Tests**: S3 buckets (input/output), EventBridge rule
- **Implementation**: Created buckets with encryption, versioning, EventBridge integration
- **Tests Written**: 12 tests before any infrastructure code
- **Key Learning**: TDD discipline pays off - caught misconfiguration early

#### Orchestration Issues (#4-6)

**Issue #4: Step Functions State Machine + Polly**
- **Tests**: State machine existence, Polly integration, IAM permissions
- **Implementation**: Minimal state machine with Polly StartSpeechSynthesisTask
- **Tests Written**: 6 tests
- **Key Learning**: CDK assertions can validate complex state machine definitions

**Issue #5: DynamoDB Metadata Table**
- **Tests**: Table schema, encryption, billing mode, IAM permissions
- **Implementation**: DynamoDB table with audioId partition key
- **Tests Written**: 6 tests
- **Key Learning**: Testing IAM grants in CDK requires careful assertion patterns

**Issue #6: SNS Notifications + Error Handling**
- **Tests**: SNS topics, encryption, error handling catch blocks
- **Implementation**: Success/failed topics, state machine error paths
- **Tests Written**: 12 tests
- **Key Learning**: Error handling complexity requires separate tests per path

#### Processing Issues (#7-8)

**Issue #7: Lambda Function Integration**
- **Tests**: Lambda function, runtime, environment variables, IAM
- **Implementation**: Audio processor Lambda (Python 3.12)
- **Tests Written**: 8 tests
- **Key Learning**: Lambda + CDK testing straightforward with proper patterns

**Issue #8: Complete Pipeline Wiring + Validation**
- **Tests**: End-to-end integration, validation logic, error paths
- **Implementation**: Input validation (file extensions), error routing
- **Tests Written**: 8 tests
- **Milestone**: Complete basic pipeline operational
- **Key Learning**: Integration tests catch wiring issues early

#### Refinement Issues (#9-11)

**Issue #9: Multi-Environment Support**
- **Tests**: Environment-specific configurations (dev/stage/prod)
- **Implementation**: Environment context, log retention, X-Ray settings
- **Tests Written**: 8 tests
- **Key Learning**: Multi-env testing prevents production surprises

**Issue #10: Advanced Error Handling + Observability**
- **Tests**: Retry policies, X-Ray tracing, CloudWatch alarms
- **Implementation**: Exponential backoff, distributed tracing, failure alarms
- **Tests Written**: 10 tests
- **Key Learning**: Observability must be tested, not assumed

**Issue #11: Core Audio Processing Logic**
- **Tests**: S3 read/write permissions, Polly integration, DynamoDB updates
- **Implementation**: Real audio download, Polly TTS, output upload
- **Tests Written**: 5 tests
- **Milestone**: Functional audio processing complete
- **Key Learning**: Transition from skeleton to real logic requires careful IAM testing

#### Completion Issue (#12)

**Issue #12: End-to-End Validation + Project Completion**
- **Tests**: Complete pipeline validation, success/error flows
- **Implementation**: Documentation polish (README, SUMMARY)
- **Tests Written**: 6 E2E validation tests
- **Total Tests**: 82+ across all issues
- **Key Learning**: E2E tests provide confidence in production readiness

---

## 🔑 Key Decisions & Trade-offs

### Technical Decisions

1. **EventBridge vs. S3 Lambda Triggers**
   - **Decision**: Use EventBridge
   - **Rationale**: Decoupling, content filtering, multiple consumers
   - **Trade-off**: Slight complexity increase vs. significant flexibility gain

2. **Step Functions vs. Lambda Orchestration**
   - **Decision**: Use Step Functions
   - **Rationale**: Visual debugging, built-in error handling, state persistence
   - **Trade-off**: Cost (~$25/million transitions) vs. operational simplicity

3. **DynamoDB On-Demand vs. Provisioned Capacity**
   - **Decision**: On-demand for dev/stage, consider provisioned for prod
   - **Rationale**: Unpredictable workload, no capacity planning
   - **Trade-off**: Higher per-request cost vs. zero throttling risk

4. **S3-Managed Encryption vs. KMS**
   - **Decision**: SSE-S3 (managed encryption)
   - **Rationale**: Lower cost, simpler key management, sufficient for audio files
   - **Trade-off**: Less control over keys vs. operational simplicity

### Methodological Decisions

5. **Strict TDD vs. Pragmatic TDD**
   - **Decision**: Strict TDD (no code before tests)
   - **Rationale**: Experimental validation of TDD discipline
   - **Trade-off**: Slower initial progress vs. higher quality and confidence

6. **Living Documentation vs. Static Docs**
   - **Decision**: ARCHITECTURE.md synchronized with every change
   - **Rationale**: Prevent documentation rot, aid AI context
   - **Trade-off**: Documentation overhead vs. long-term maintainability

---

## 🔍 Preliminary Observations

### Strengths of the Approach

1. **High Code Quality**
   - 82+ tests caught numerous configuration errors before deployment
   - Zero regressions due to comprehensive test coverage
   - Production-ready security and error handling built in from start

2. **AI-Human Collaboration Effectiveness**
   - Q Developer excelled at generating CDK assertion tests
   - Pattern recognition improved over issues (learning effect)
   - Documentation synchronization successful with prompt guidance

3. **Documentation Synchronization Success**
   - ARCHITECTURE.md remained accurate throughout 12 issues
   - Mermaid diagrams provided visual clarity at every stage
   - Change log created comprehensive project history

4. **Issue-Driven Development Benefits**
   - Focused scope prevented feature creep
   - Clear acceptance criteria enabled objective completion assessment
   - Dependency tracking prevented blocking issues

### Challenges Encountered

1. **TDD Discipline Requires Vigilance**
   - Temptation to implement before testing required constant enforcement
   - Some complex infrastructure patterns hard to test (state machine JSON)
   - Initial learning curve for CDK assertion patterns

2. **AI Context Limitations**
   - Q Developer occasionally forgot project context between sessions
   - Required re-establishing TDD discipline in each session
   - Mitigation: AGENT_GUIDELINES.md provided persistent context

3. **State Machine Testing Complexity**
   - Testing Step Functions definitions required regex pattern matching
   - Error handling paths difficult to validate statically
   - Mitigation: Snapshot tests caught unexpected changes

4. **Documentation Overhead**
   - Updating ARCHITECTURE.md after every issue time-consuming
   - Mermaid diagram complexity increased over time
   - Trade-off accepted for long-term maintainability

### Lessons Learned

1. **TDD for IaC is Viable**: Infrastructure can be developed test-first with same rigor as application code
2. **AI Agents Benefit from Structure**: Clear guidelines and prompts essential for consistency
3. **Living Documentation Works**: Synchronization overhead worth it for accuracy
4. **Issue Granularity Matters**: Focused issues (1-2 day scope) optimal for TDD workflow
5. **Multi-Environment Early**: Environment abstraction from Issue #1 would have saved refactoring

---

## 📈 Success Metrics

### Quantitative Metrics

- ✅ **82+ Tests**: All passing, written before implementation
- ✅ **12 Issues**: Completed with consistent TDD approach
- ✅ **0 Regressions**: Test suite caught all breaking changes
- ✅ **8 AWS Services**: Integrated with full observability
- ✅ **3 Environments**: Multi-environment support (dev/stage/prod)
- ✅ **100% Documentation**: ARCHITECTURE.md synchronized with code

### Qualitative Metrics

- ✅ **Production-Ready**: Encryption, error handling, observability, IAM least privilege
- ✅ **Maintainable**: Clear code structure, comprehensive tests, living documentation
- ✅ **AI Collaboration**: Q Developer effectively followed TDD discipline with prompting
- ✅ **Knowledge Transfer**: META-PROMPTS.md extracted reusable patterns

---

## 🎓 Conclusions & Next Steps

### Experiment Conclusions

1. **Hypothesis Confirmed**: AI agents (Q Developer) can effectively collaborate on TDD IaC with proper prompting and guidelines
2. **TDD Viable for IaC**: Infrastructure code can be developed test-first with measurable quality benefits
3. **Documentation Synchronization Achievable**: Living documentation remained accurate with disciplined workflow
4. **Production-Ready Output**: TDD+AI approach produced infrastructure meeting production standards

### Comparison Readiness

This experiment (Python + Q Developer) is **ready for cross-comparison** with:
- Other language variants (TypeScript, Java, C#, Go)
- Other AI agents (GitHub Copilot, etc.)
- Traditional development approaches (without AI or without TDD)

### Next Steps

**Issue #15: Code Quality, Coverage & Reflection** will provide:
- Final code quality assessment
- Test coverage analysis
- Retrospective on TDD+AI approach
- Cross-experiment comparison (if other variants complete)
- Recommendations for future TDD IaC projects

---

**Experiment Document Status**: ✅ Complete  
**Last Updated**: Issue #14 - Q Developer  
**For Evaluation**: See Issue #15 for final assessment and comparison
