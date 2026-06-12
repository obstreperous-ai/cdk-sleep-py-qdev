# Agent Guidelines for cdk-sleep-py-qdev

## Project Status

✅ **COMPLETE** - All core functionality implemented through Issue #12.

The Sleep Audio Pipeline is production-ready with:
- Full end-to-end processing (S3 → EventBridge → Step Functions → Lambda → Polly → S3)
- Comprehensive error handling and retry policies
- Multi-environment support (dev/stage/prod)
- Complete observability (CloudWatch, X-Ray, alarms)
- 82+ passing tests with full TDD coverage

## Purpose
This document provides guidance for AI agents (Q Developer, GitHub Copilot, etc.) and human developers working on the **Event-Driven Sleep Audio Pipeline** project. It establishes conventions, references, and best practices to ensure consistency across all future issues and pull requests.

## Source of Truth

### Primary Reference: ARCHITECTURE.md

**[ARCHITECTURE.md](ARCHITECTURE.md)** is the **single source of truth** for the system architecture, including:

- Complete system design and data flow
- AWS service selection and rationale
- Security, observability, and cost considerations
- Mermaid diagrams showing the full pipeline
- Multi-environment configuration (dev/stage/prod)
- Future extensibility plans

**Before implementing any feature or fix:**
1. ✅ Read ARCHITECTURE.md thoroughly
2. ✅ Understand how your change fits into the overall system
3. ✅ Ensure your implementation aligns with documented patterns
4. ✅ Update ARCHITECTURE.md if your change adds new components or modifies data flow

## Development Philosophy

### Test-Driven Development (TDD) First

This project **strictly follows TDD**. No production code is written before tests.

#### TDD Cycle

```
🔴 RED → 🟢 GREEN → 🔵 REFACTOR → 📝 DOCUMENT
```

1. **🔴 RED**: Write a failing test that defines the desired behavior
   - Test must fail for the right reason
   - Test must be specific and focused
   - Use `aws_cdk.assertions` for infrastructure tests

2. **🟢 GREEN**: Write minimal code to make the test pass
   - Simplest implementation that satisfies the test
   - No gold-plating or premature optimization
   - Keep changes focused and atomic

3. **🔵 REFACTOR**: Clean up code while keeping tests green
   - Improve readability and maintainability
   - Extract common patterns
   - Follow DRY (Don't Repeat Yourself) principle

4. **📝 DOCUMENT**: Update ARCHITECTURE.md and code comments
   - Keep diagrams in sync with implementation
   - Document rationale for design decisions
   - Update change log

### Issue-Driven Development

Every feature, enhancement, or bug fix:
- ✅ Starts with a GitHub issue
- ✅ Is broken down into testable units
- ✅ Has clear acceptance criteria
- ✅ References ARCHITECTURE.md for context
- ✅ Results in a pull request with tests

## Coding Standards

### Python Style
- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type annotations for function signatures
- **Docstrings**: Use Google-style docstrings for classes and public methods
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### CDK Conventions

#### Resource Naming
```python
# Pattern: {resource_type}_{descriptive_name}_{env}
input_bucket = s3.Bucket(self, "InputBucket",
    bucket_name=f"sleep-audio-input-{environment}")
```

#### Resource IDs (Logical Names)
- Use descriptive, human-readable IDs
- PascalCase for CDK construct IDs
- Example: `"InputBucket"`, `"AudioProcessingStateMachine"`, `"ValidateLambda"`

#### IAM Policies
- **Least Privilege**: Grant minimal required permissions
- **Inline Policies**: Use for function-specific permissions
- **Managed Policies**: Use for shared permissions across resources
- **Comments**: Document why each permission is needed

### Testing Standards

#### Test File Organization
```
tests/
├── unit/
│   ├── test_cdk_base_stack.py      # Infrastructure tests
│   ├── test_s3_buckets.py          # Specific component tests
│   ├── test_lambda_functions.py
│   └── test_step_functions.py
└── integration/                     # Future: end-to-end tests
    └── test_audio_pipeline.py
```

#### Test Naming
```python
def test_{resource}_{property}_{expected_behavior}():
    # Example: test_input_bucket_has_versioning_enabled()
    pass
```

#### Assertions
- Use `aws_cdk.assertions.Template.from_stack()` for CDK tests
- Use specific assertions: `has_resource_properties()`, `resource_count_is()`
- Test both positive cases (resource exists) and negative cases (unwanted configs)

## Pull Request Guidelines

### PR Title Format
```
[Issue #X] Brief description of change
```

### PR Description Must Include
1. **Issue Reference**: Link to GitHub issue
2. **Summary**: What was changed and why
3. **Testing**: How the change was tested (test names, coverage)
4. **Architecture Impact**: Does this change affect ARCHITECTURE.md? (If yes, include updates)
5. **Checklist**:
   - [ ] Tests written and passing
   - [ ] ARCHITECTURE.md updated (if applicable)
   - [ ] Code follows project conventions
   - [ ] All CI checks passing

## Environment Configuration

### Multi-Environment Support

The project supports three environments via CDK context in `cdk.json`:

- **dev**: Local development and experimentation
- **stage**: Pre-production testing with prod-like configuration
- **prod**: Live customer-facing environment

### Deployment Commands

```bash
# Deploy to dev
cdk deploy --context env=dev

# Deploy to stage
cdk deploy --context env=stage

# Deploy to prod (requires approval)
cdk deploy --context env=prod --require-approval broadening
```

### Environment-Specific Configuration

Always use CDK context to parameterize:
- Resource names (include environment suffix)
- Log retention periods
- Lambda memory/timeout configurations
- DynamoDB billing modes
- Feature flags (e.g., `enable_bedrock`)

## Security Best Practices

### Mandatory Security Checks

1. **No Hardcoded Secrets**: Use AWS Secrets Manager or Parameter Store
2. **Least Privilege IAM**: Review every permission grant
3. **Encryption at Rest**: All data stores must use KMS encryption
4. **Encryption in Transit**: HTTPS/TLS for all communications
5. **Private Resources**: S3 buckets must block public access
6. **Input Validation**: Validate all user inputs in Lambda functions

### Security Testing

Include security-focused tests:
```python
def test_s3_bucket_blocks_public_access():
    # Assert that public access is blocked
    pass

def test_lambda_has_minimal_iam_permissions():
    # Assert only required permissions granted
    pass
```

## Common Patterns

### Adding a New Lambda Function

1. **Test First**: Write test asserting Lambda resource exists with correct properties
2. **Implement**: Create Lambda construct in CDK stack
3. **IAM Policy**: Define least-privilege execution role
4. **Environment Variables**: Pass configuration via env vars (not hardcoded)
5. **Logging**: Ensure CloudWatch log group is created
6. **Update ARCHITECTURE.md**: Document the function's purpose and data flow

### Adding a New S3 Bucket

1. **Test First**: Assert bucket exists with required properties
2. **Properties to Test**:
   - Versioning enabled/disabled
   - Encryption configuration (SSE-KMS)
   - Public access blocked
   - Lifecycle policies (if applicable)
3. **Event Notifications**: If bucket triggers events, test EventBridge integration
4. **Update ARCHITECTURE.md**: Add bucket to diagram and data flow description

### Adding a Step Functions State Machine

1. **Test First**: Assert state machine resource exists
2. **Definition**: Use CDK's high-level constructs or JSON definition
3. **IAM Role**: Define execution role with permissions for all integrated services
4. **Error Handling**: Test that Catch and Retry policies are configured
5. **Logging**: Enable execution logging to CloudWatch
6. **Update ARCHITECTURE.md**: Update Mermaid diagram with new states

## Resources and References

### Internal Documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and design
- **[README.md](README.md)**: Project setup and quick start guide
- **[META-PROMPTS.md](META-PROMPTS.md)**: Reusable meta-prompting patterns for TDD IaC projects
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines (if exists)

### AWS CDK Resources
- AWS CDK Python Reference: Consult official AWS CDK documentation
- CDK Patterns: Review AWS-provided CDK patterns for common architectures

### Testing Resources
- pytest: Python testing framework
- aws-cdk.assertions: CDK testing library

## Issue Workflow

### For AI Agents (Q Developer)

When assigned an issue:

1. **Understand Context**:
   - Read the issue description carefully
   - Review ARCHITECTURE.md for system context
   - Identify affected components

2. **Plan Implementation**:
   - Break down the issue into testable units
   - Identify which files need changes (tests first, then implementation)
   - Consider impact on existing components

3. **Implement with TDD**:
   - Write failing tests first
   - Implement minimal code to pass tests
   - Refactor for quality
   - Update documentation

4. **Create Pull Request**:
   - Follow PR template
   - Include test results
   - Reference issue number
   - Request review

### Example Issue Flow

**Issue #3: TDD: Core S3 Buckets + EventBridge Rule**

1. ✅ Read ARCHITECTURE.md section on S3 buckets and EventBridge
2. ✅ Write test: `test_input_bucket_exists_with_versioning()`
3. ✅ Run test: Should fail (RED)
4. ✅ Implement: Add S3 bucket construct to CDK stack
5. ✅ Run test: Should pass (GREEN)
6. ✅ Repeat for other properties (encryption, public access block, etc.)
7. ✅ Write test: `test_eventbridge_rule_triggers_on_s3_upload()`
8. ✅ Implement: Add EventBridge rule
9. ✅ Refactor: Clean up code, extract constants
10. ✅ Update ARCHITECTURE.md: Mark S3 buckets as implemented
11. ✅ Create PR with all tests passing

## Questions or Clarifications?

If you encounter ambiguity or need clarification:

1. **Check ARCHITECTURE.md**: Most design decisions are documented
2. **Review Existing Tests**: See how similar features were tested
3. **Ask in Issue Comments**: Tag maintainers for guidance
4. **Propose Changes**: If architecture needs adjustment, open a discussion

## Reusable Patterns for Future Projects

The **[META-PROMPTS.md](META-PROMPTS.md)** file contains extracted reusable patterns from this project:
- TDD workflow prompts for AI agents
- Issue-driven development templates
- Security and observability checklists
- Multi-environment configuration patterns

## Summary Checklist
## Project Completion Notes (Issue #12)

### What Was Completed

The project successfully implemented all planned features through Issues #1-12:
- ✅ Core infrastructure (S3, EventBridge, Step Functions, Lambda, DynamoDB, SNS)
- ✅ Real audio processing with Polly TTS integration
- ✅ Comprehensive error handling and retry policies
- ✅ Full observability (CloudWatch Logs, X-Ray, CloudWatch Alarms)
- ✅ Multi-environment support (dev/stage/prod)
- ✅ Complete documentation (README, ARCHITECTURE, SUMMARY)
- ✅ 82+ TDD tests with end-to-end validation

### Future Enhancements (Beyond Current Scope)

Potential areas for continued development:
- API Gateway for programmatic access
- Advanced audio mixing (multi-track support)
- User authentication with Cognito
- CloudFront CDN for global audio delivery
- Amazon Transcribe for reverse text extraction
- SageMaker integration for ML-powered audio enhancement
- Real-time processing status via WebSocket API


Before submitting any pull request:

- [ ] Tests written first (TDD)
- [ ] All tests passing
- [ ] Code follows project conventions
- [ ] ARCHITECTURE.md updated if needed
- [ ] Security best practices followed
- [ ] Environment-specific configuration used
- [ ] PR description complete
- [ ] Issue referenced in PR title
- [ ] CI checks passing

---

**Remember**: 
- ARCHITECTURE.md is the source of truth for system design
- META-PROMPTS.md contains reusable patterns for future TDD IaC projects
- README.md is the comprehensive entry point for new contributors
- SUMMARY.md contains key decisions and deployment guidance
- All features were implemented following strict TDD (Red-Green-Refactor-Document)
