# avel-aero-assessment-
# Avel Aero — Workflow Execution Engine

## Overview

This project implements a lightweight workflow execution engine for a fictional private charter inquiry. It uses a finite state machine (FSM) to coordinate four steps:

1. Check aircraft availability.
2. Prepare a quote.
3. Wait for human approval.
4. Send the approved quote (mock operation).

All external services are simulated. No actual messages are sent.

## Architecture

The workflow is managed by a `WorkflowEngine` class.

The engine uses an enumerated `WorkflowState` to track its current execution state. A transition map defines which state changes are permitted.

The engine also maintains:
- A shared data dictionary to pass results between workflow steps.
- An execution history with timestamps.
- A retry counter for temporary failures.
- An approval flag to control sensitive actions.

### Workflow sequence

`START → CHECK_AVAILABILITY → PREPARE_QUOTE → WAITING_APPROVAL → SEND_QUOTE → COMPLETE`

A temporary availability failure triggers a retry. A rejected quote terminates the workflow in the `REJECTED` state.

## Key Engineering Decision

I chose a finite state machine rather than executing a sequence of independent functions. This makes workflow progression explicit and allows transitions to be validated.

I also implemented an approval guard in the sending function. The quote cannot be sent unless explicit human approval has been recorded.

## Failure Handling

The availability tool simulates a temporary API timeout on the first attempt. The engine records the failure, transitions to a retry state, and attempts the availability check again.

The maximum number of attempts is configurable.

## How to Run

Requires Python 3.

Run the workflow:

```bash
python3 main.py
```

Run automated tests:

```bash
python3 -m unittest -v test_workflow.py
```

When prompted, enter `yes` to approve the quote or `no` to reject it.

## Tests

Automated tests verify:
- The initial workflow state.
- Invalid state transitions are rejected.
- Sending is blocked without approval.
- Sending is permitted after approval.

## Limitations

This is a simulated execution engine. Aircraft availability, quote preparation, and message delivery use hardcoded responses rather than live external services. Workflow state is stored in memory and is not persisted between program executions.