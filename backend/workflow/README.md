# Workflow Manager

The Workflow Manager manages execution state machines across multi-stage engine operations.

## Capabilities
- **Sequential Execution**: Strict dependency ordering across steps.
- **Conditional Execution**: Skip steps if prerequisite conditions or dependencies fail.
- **Retry Mechanism**: Automatic retries per step with configurable max retry policy.
- **Cancellation**: Asynchronous cancellation request propagation.
- **Progress Tracking**: Real-time step status and completion progress calculation.
