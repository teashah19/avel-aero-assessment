from enum import Enum
from datetime import datetime

# 1. Define every possible workflow state
class WorkflowState(Enum):
    START = "START"
    CHECK_AVAILABILITY = "CHECK_AVAILABILITY"
    RETRY = "RETRY"
    PREPARE_QUOTE = "PREPARE_QUOTE"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    SEND_QUOTE = "SEND_QUOTE"
    COMPLETE = "COMPLETE"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


# 2. Define the workflow engine
class WorkflowEngine:

    def __init__(self):
        self.state = WorkflowState.START
        self.history = []
        self.data = {}

        self.attempts = 0
        self.max_attempts = 2
        self.approved = False

        # Only these transitions are permitted
        self.allowed_transitions = {
            WorkflowState.START: [
                WorkflowState.CHECK_AVAILABILITY
            ],
            WorkflowState.CHECK_AVAILABILITY: [
                WorkflowState.RETRY,
                WorkflowState.PREPARE_QUOTE,
                WorkflowState.FAILED
            ],
            WorkflowState.RETRY: [
                WorkflowState.CHECK_AVAILABILITY,
                WorkflowState.FAILED
            ],
            WorkflowState.PREPARE_QUOTE: [
                WorkflowState.WAITING_APPROVAL,
                WorkflowState.FAILED
            ],
            WorkflowState.WAITING_APPROVAL: [
                WorkflowState.SEND_QUOTE,
                WorkflowState.REJECTED
            ],
            WorkflowState.SEND_QUOTE: [
                WorkflowState.COMPLETE,
                WorkflowState.FAILED
            ],
            WorkflowState.COMPLETE: [],
            WorkflowState.REJECTED: [],
            WorkflowState.FAILED: []
        }

    # 3. Record workflow events
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")

        entry = f"[{timestamp}] [{self.state.value}] {message}"

        self.history.append(entry)
        print(entry)

    # 4. Control state transitions
    def transition(self, new_state):

    if new_state not in self.allowed_transitions[self.state]:
        raise ValueError(
            f"Invalid transition: {self.state.value} "
            f"to {new_state.value}"
        )

    old_state = self.state
    self.state = new_state

    self.log(f"Transition: {old_state.value} -> {new_state.value}")


    # 5. Mock aircraft availability tool
    def check_availability(self):

        self.attempts += 1

        self.log(f"Checking aircraft availability. "
                 f"Attempt {self.attempts}")

        # Simulate a temporary API timeout on attempt one
        if self.attempts == 1:
            raise TimeoutError("Temporary API timeout")

        # Mock successful API response
        availability = {
            "aircraft": "Citation CJ3",
            "available": True,
            "departure": "San Francisco",
            "destination": "Las Vegas",
            "passengers": 4
        }

        self.data["availability"] = availability

        self.log("Aircraft availability received successfully")

        return availability


    # 6. Prepare quote using availability results
    def prepare_quote(self):

        availability = self.data["availability"]

        if not availability["available"]:
            raise RuntimeError("No aircraft available")

        quote = {
            "aircraft": availability["aircraft"],
            "route": (
                f"{availability['departure']} to "
                f"{availability['destination']}"
            ),
            "passengers": availability["passengers"],
            "price": 12500
        }

        self.data["quote"] = quote

        self.log("Quote successfully prepared")

        print("\n----- DRAFT QUOTE -----")
        print(f"Aircraft: {quote['aircraft']}")
        print(f"Route: {quote['route']}")
        print(f"Passengers: {quote['passengers']}")
        print(f"Estimated price: ${quote['price']:,}")
        print("-----------------------\n")

        return quote


    # 7. Wait for explicit human approval
    def request_approval(self):

        self.log("Workflow paused. Awaiting human approval.")

        while True:
            response = input(
                "Approve this quote? (yes/no): "
            ).strip().lower()

            if response in ("yes", "y"):
                self.approved = True
                self.log("Human approval received")
                return True

            elif response in ("no", "n"):
                self.approved = False
                self.log("Human rejected the quote")
                return False

            else:
                print("Please enter yes or no.")


    # 8. Mock sending tool
    def send_quote(self):

        # Safety check: sending is impossible without approval
        if not self.approved:
            raise PermissionError(
                "Cannot send quote without human approval"
            )

        quote = self.data["quote"]

        self.log("Mock sending approved quote...")

        # No actual email or message is sent
        self.data["sent_quote"] = quote

        self.log("Mock send completed successfully")


    # 9. Execute the complete workflow
    def run(self):

        self.log("Starting workflow REQ-1042")

        try:

            # STEP 1: Check aircraft availability
            self.transition(
                WorkflowState.CHECK_AVAILABILITY
            )

            while True:
                try:
                    self.check_availability()
                    break

                except TimeoutError as error:

                    self.log(f"FAILED: {error}")

                    if self.attempts < self.max_attempts:

                        self.transition(WorkflowState.RETRY)

                        self.log("Retrying availability check")

                        self.transition(
                            WorkflowState.CHECK_AVAILABILITY
                        )

                    else:
                        self.transition(WorkflowState.FAILED)
                        self.log("Maximum retries exceeded")
                        return

            # STEP 2: Prepare quote
            self.transition(WorkflowState.PREPARE_QUOTE)

            self.prepare_quote()

            # STEP 3: Wait for human approval
            self.transition(WorkflowState.WAITING_APPROVAL)

            approved = self.request_approval()

            if not approved:
                self.transition(WorkflowState.REJECTED)
                self.log("Workflow terminated without sending")
                return

            # STEP 4: Send approved quote
            self.transition(WorkflowState.SEND_QUOTE)

            self.send_quote()

            self.transition(WorkflowState.COMPLETE)

            self.log("Workflow finished successfully")

        except Exception as error:

            if self.state not in (
                WorkflowState.COMPLETE,
                WorkflowState.REJECTED,
                WorkflowState.FAILED
            ):
                self.transition(WorkflowState.FAILED)

            self.log(f"Workflow error: {error}")


# 10. Start the program
if __name__ == "__main__":

    engine = WorkflowEngine()

    engine.run()

    print("\n===== EXECUTION HISTORY =====")

    for event in engine.history:
        print(event)

    print("\nFinal workflow status:", engine.state.value)
