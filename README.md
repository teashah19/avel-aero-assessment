# Avel Aero Workflow Engine

A small workflow engine that handles a made-up private charter inquiry. It runs a finite state machine through four steps:

1. Check aircraft availability
2. Prepare a quote
3. Wait for a human to approve it
4. Send the quote (mocked)

Everything external is simulated, so no real messages go out.

## How it works

The core is a `WorkflowEngine` class. It tracks where it is with a `WorkflowState` enum, and a transition map decides which moves are allowed. Alongside that it keeps:

- a shared dictionary so steps can pass results to each other
- a timestamped history of what ran
- a retry counter for temporary failures
- an approval flag that gates the send step

The happy path looks like this:

`START → CHECK_AVAILABILITY → PREPARE_QUOTE → WAITING_APPROVAL → SEND_QUOTE → COMPLETE`

If the availability check fails temporarily, the engine retries. If the quote is rejected, the workflow ends in `REJECTED`.

## Design choices

I used a state machine instead of just calling a chain of functions, because it makes the progression explicit and lets the engine reject invalid transitions.

The send function also checks for approval itself. Even if something else in the code tries to skip ahead, a quote can't go out unless a human has approved it.

## Failure handling

The mock availability tool times out on the first call on purpose. The engine logs the failure, moves into a retry state, and tries again. The max number of attempts is configurable.

## Running it

You need Python 3.

```bash
python3 main.py
```

When prompted, type `yes` to approve the quote or `no` to reject it.

To run the tests:

```bash
python3 -m unittest -v test_workflow.py
```

## Tests

The tests cover:

- the initial state
- rejection of invalid transitions
- sending being blocked without approval
- sending working once approval is recorded

## Limitations

Availability, quotes, and message delivery all use hardcoded responses, not real services. State lives in memory only, so nothing is saved between runs.