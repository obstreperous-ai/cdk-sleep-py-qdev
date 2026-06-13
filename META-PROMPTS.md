# Meta-Prompts & Reusable Patterns for TDD IaC Development

This document extracts **reusable meta-prompting patterns** from the Sleep Audio Pipeline project that can be applied to future TDD Infrastructure as Code (IaC) projects, particularly when working with AI agents like Q Developer, GitHub Copilot, or similar tools.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Core TDD IaC Workflow](#core-tdd-iac-workflow)
- [Agent Prompting Strategies](#agent-prompting-strategies)
- [Issue-Driven Development Patterns](#issue-driven-development-patterns)
- [CDK Testing Patterns](#cdk-testing-patterns)
- [Documentation Synchronization Patterns](#documentation-synchronization-patterns)
- [Security-First Patterns](#security-first-patterns)
- [Multi-Environment Patterns](#multi-environment-patterns)
- [Error Handling & Observability Patterns](#error-handling--observability-patterns)
- [Template Prompts](#template-prompts)
- [How to Use with AI Agents](#how-to-use-with-ai-agents)

---

## 🎯 Overview

These patterns were extracted from a successful 12-issue TDD IaC project that built a production-ready event-driven audio processing pipeline on AWS using CDK (Python). The patterns focus on:

- **Strict TDD discipline** for infrastructure code
- **Issue-driven development** for focused incremental progress
- **Living documentation** that stays synchronized with code
- **AI agent collaboration** to accelerate development while maintaining quality

### Key Success Metrics from Original Project

- ✅ **82+ tests** written before implementation
- ✅ **Zero regressions** - tests caught all breaking changes
- ✅ **100% documentation coverage** - ARCHITECTURE.md updated with every issue
- ✅ **12 issues completed** with consistent TDD approach
- ✅ **Production-ready output** - comprehensive error handling, observability, security

---

## 🔴🟢🔵 Core TDD IaC Workflow

### The Red-Green-Refactor-Document Cycle

**Pattern**: Infrastructure development must follow strict TDD with documentation as a first-class activity.

#### Phase 1: 🔴 RED (Write Failing Test)

```python
# Example: Before implementing S3 bucket, write this test
def test_input_s3_bucket_exists(template):
    """TDD Test: Verify Input S3 Bucket exists."""
    template.resource_count_is("AWS::S3::Bucket", 1)
    template.has_resource_properties("AWS::S3::Bucket", {
        "VersioningConfiguration": {
            "Status": "Enabled"
        }
    })
```

**Agent Prompt Template**:
```
I am implementing [FEATURE] using strict TDD. Write a failing test for [RESOURCE] 
that asserts:
1. The resource exists
2. [PROPERTY_1] is configured to [VALUE_1]
3. [PROPERTY_2] is configured to [VALUE_2]

Use aws_cdk.assertions.Template for CDK tests.
The test must fail when run before implementation.
```

#### Phase 2: 🟢 GREEN (Minimal Implementation)

```python
# Minimal code to pass the test
self.input_bucket = s3.Bucket(
    self,
    "InputBucket",
    versioned=True,
)
```

**Agent Prompt Template**:
```
Write the minimal CDK code to make the following test pass:
[PASTE TEST CODE]

Use AWS CDK L2 constructs. Do not add extra features beyond what the test requires.
```

#### Phase 3: 🔵 REFACTOR (Clean Up)

```python
# Refactored with proper naming, constants, and best practices
self.input_bucket = s3.Bucket(
    self,
    f"SleepAudioInputBucket{self.env_name.capitalize()}",
    encryption=s3.BucketEncryption.S3_MANAGED,
    versioned=True,
    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
    enforce_ssl=True,
    removal_policy=RemovalPolicy.RETAIN,
)
```

**Agent Prompt Template**:
```
Refactor this CDK code while keeping tests green:
[PASTE CODE]

Apply these improvements:
1. Add descriptive resource IDs with environment suffix
2. Add security best practices (encryption, public access blocking)
3. Add removal policies appropriate for production
4. Extract magic values to constants if reused
5. Add inline comments explaining non-obvious configurations

Ensure all existing tests still pass.
```

#### Phase 4: 📝 DOCUMENT (Sync Architecture)

**Agent Prompt Template**:
```
Update ARCHITECTURE.md to reflect the following changes:
[DESCRIBE WHAT WAS IMPLEMENTED]

Update these sections:
1. Mermaid diagram (if data flow changed)
2. "Stack Components" section - mark [COMPONENT] as implemented
3. "Change Log" section - add Issue #[N] with summary
4. Any affected rationale or configuration sections

Keep formatting consistent with existing style.
```

---

## 🤖 Agent Prompting Strategies

### 1. Context Setting Prompt

Use at the **start of each session** to establish context:

```
I am working on [PROJECT NAME], a TDD-first AWS CDK project. Key context:

- Language: Python 3.12
- Framework: AWS CDK 2.x
- Testing: pytest with aws_cdk.assertions
- Philosophy: Strict TDD (Red-Green-Refactor-Document)
- Documentation: ARCHITECTURE.md is the source of truth
- Current Issue: #[N] - [ISSUE TITLE]

Before suggesting any code:
1. Have I written tests first?
2. Does this align with ARCHITECTURE.md?
3. Am I following existing patterns in the codebase?
4. Will this require documentation updates?
```

### 2. Incremental Progress Prompt

Use when feeling overwhelmed or unsure:

```
Break down Issue #[N] into minimal testable units. For each unit:
1. What is the smallest test I can write?
2. What is the minimal code to pass that test?
3. What refactoring would improve quality?

List units in dependency order (foundations first).
```

### 3. Test-First Enforcement Prompt

Use when tempted to write implementation first:

```
STOP. I am about to implement [FEATURE] without tests.

Instead, help me write a failing test that asserts:
- [EXPECTED BEHAVIOR 1]
- [EXPECTED BEHAVIOR 2]
- [EXPECTED BEHAVIOR 3]

Use aws_cdk.assertions and follow naming convention:
test_[resource]_[property]_[expected_behavior]
```

### 4. Documentation Sync Prompt

Use after **every implementation**:

```
I just implemented [FEATURE] in [FILE]. 

Review ARCHITECTURE.md and identify:
1. Which sections need updates?
2. Does the Mermaid diagram need changes?
3. Should I add this to the Change Log?
4. Are there any outdated statements?

Provide specific line numbers and suggested changes.
```

---

## 📋 Issue-Driven Development Patterns

### Issue Structure Template

Every issue should follow this structure:

```markdown
# Issue #[N]: [Title - Descriptive, Action-Oriented]

## Goal
[What are we trying to achieve? Why does this matter?]

## Acceptance Criteria
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)
- [ ] All tests pass
- [ ] ARCHITECTURE.md updated
- [ ] CI passes

## TDD Approach
1. Write tests for [FEATURE A]
2. Implement [FEATURE A]
3. Write tests for [FEATURE B]
4. Implement [FEATURE B]
5. Refactor for quality
6. Update documentation

## Dependencies
- Requires: Issue #[M] (completed)
- Blocks: Issue #[P] (future)

## Related Documentation
- ARCHITECTURE.md: Section [X]
- AGENT_GUIDELINES.md: Pattern [Y]
```

### Issue Workflow Prompt

```
I am starting Issue #[N]: [TITLE]

Guide me through strict TDD workflow:
1. Review ARCHITECTURE.md - what's the current state?
2. What tests should I write first? (List in order)
3. For each test, what's the minimal implementation?
4. What refactoring opportunities exist?
5. What documentation updates are needed?

Keep me disciplined - no implementation before tests.
```

---

## 🧪 CDK Testing Patterns

### Pattern 1: Resource Existence Test

```python
def test_[resource]_exists(template):
    """TDD Test: Verify [RESOURCE] exists."""
    template.resource_count_is("AWS::[SERVICE]::[TYPE]", expected_count)
```

### Pattern 2: Resource Properties Test

```python
def test_[resource]_has_[property](template):
    """TDD Test: Verify [RESOURCE] has [PROPERTY] configured."""
    template.has_resource_properties("AWS::[SERVICE]::[TYPE]", {
        "PropertyName": expected_value
    })
```

### Pattern 3: IAM Permissions Test

```python
def test_[resource]_has_[permission](template):
    """TDD Test: Verify [RESOURCE] has [PERMISSION]."""
    template.has_resource_properties("AWS::IAM::Policy", {
        "PolicyDocument": {
            "Statement": assertions.Match.array_with([
                assertions.Match.object_like({
                    "Action": assertions.Match.array_with(["service:Action"]),
                    "Effect": "Allow"
                })
            ])
        }
    })
```

### Pattern 4: State Machine Definition Test

```python
def test_state_machine_contains_[task](template):
    """TDD Test: Verify state machine definition contains [TASK]."""
    template.has_resource_properties("AWS::StepFunctions::StateMachine", {
        "DefinitionString": assertions.Match.string_like_regexp(".*[PatternToMatch].*")
    })
```

### Testing Prompt Template

```
Write CDK assertion tests for [RESOURCE] that verify:
1. Resource exists with correct count
2. [PROPERTY_1] = [VALUE_1]
3. [PROPERTY_2] = [VALUE_2]
4. IAM permissions are correctly granted
5. Integration with [OTHER_RESOURCE] works

Use aws_cdk.assertions.Template.from_stack()
Follow naming: test_[resource]_[property]_[expected_behavior]
```

---

## 📝 Documentation Synchronization Patterns

### Synchronization Checklist

After every implementation, verify:

- [ ] ARCHITECTURE.md Mermaid diagram matches current flow
- [ ] Stack Components section shows correct status (✅ or pending)
- [ ] Change Log includes new issue with summary
- [ ] Service rationale explains new AWS services used
- [ ] IAM permissions are documented
- [ ] Future enhancements list is updated

### Documentation Review Prompt

```
I completed Issue #[N] which added [FEATURE].

Review ARCHITECTURE.md and create a diff showing:
1. Mermaid diagram changes (if any)
2. Updated component status
3. Change log entry
4. Any new sections needed

Provide markdown diff I can apply directly.
```

---

## 🔒 Security-First Patterns

### Security Checklist Prompt

Use **before finalizing** any infrastructure:

```
Security review for [RESOURCE]:

1. Encryption at rest? (S3, DynamoDB, SNS, etc.)
2. Encryption in transit? (HTTPS/TLS enforced?)
3. Least privilege IAM? (Minimal permissions granted?)
4. No hardcoded secrets? (Use Secrets Manager/Parameter Store?)
5. Public access blocked? (S3 buckets, databases, etc.)
6. Input validation? (Lambda validates all inputs?)
7. Audit logging? (CloudTrail, S3 access logs?)
8. Network security? (VPC, security groups if applicable?)

For each "No", provide specific remediation code.
```

### IAM Policy Pattern

```python
# Always grant permissions explicitly, never use wildcards unless necessary
resource.grant_[action](principal)  # Preferred

# If custom policy needed, document why
principal.add_to_role_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["service:SpecificAction"],  # Not service:*
        resources=[specific_resource_arn],   # Not "*"
    )
)
```

---

## 🌍 Multi-Environment Patterns

### Environment Configuration Pattern

```python
def _get_environment_config(self) -> dict:
    """Get environment-specific configuration."""
    configs = {
        "dev": {
            "log_retention": logs.RetentionDays.ONE_WEEK,
            "enable_xray": False,  # Cost savings
        },
        "stage": {
            "log_retention": logs.RetentionDays.ONE_MONTH,
            "enable_xray": True,  # Prod-like testing
        },
        "prod": {
            "log_retention": logs.RetentionDays.THREE_MONTHS,
            "enable_xray": True,  # Full observability
        }
    }
    return configs.get(self.env_name, configs["dev"])
```

### Multi-Environment Testing Prompt

```
Test my stack across all environments:

Write tests that:
1. Create stacks for dev, stage, prod
2. Assert environment-specific configurations
3. Verify resource naming includes environment suffix
4. Check log retention matches environment
5. Verify X-Ray enabled based on environment

Each test should pass for all three environments.
```

---

## 🚨 Error Handling & Observability Patterns

### Retry Policy Pattern

```python
task.add_retry(
    errors=["Service.Exception", "States.Timeout"],
    interval=Duration.seconds(2),
    max_attempts=3,
    backoff_rate=2.0  # Exponential backoff
)
```

### CloudWatch Alarm Pattern

```python
alarm = cloudwatch.Alarm(
    self, "ResourceFailureAlarm",
    metric=resource.metric_[metric](period=Duration.minutes(5)),
    threshold=threshold_value,
    evaluation_periods=1,
    comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
)
alarm.add_alarm_action(cloudwatch.actions.SnsAction(sns_topic))
```

### Observability Checklist Prompt

```
Observability review for [COMPONENT]:

1. CloudWatch Logs enabled?
2. X-Ray tracing active?
3. Alarms for failures?
4. SNS notifications configured?
5. Structured logging (JSON)?
6. Request IDs tracked?
7. Retry policies with exponential backoff?

For each "No", provide implementation code.
```

---

