
import unittest

from main import WorkflowEngine, WorkflowState


class TestWorkflowEngine(unittest.TestCase):

    def test_cannot_send_without_approval(self):
        engine = WorkflowEngine()

        engine.data["quote"] = {
            "aircraft": "Citation CJ3",
            "route": "San Francisco to Las Vegas",
            "passengers": 4,
            "price": 12500
        }

        with self.assertRaises(PermissionError):
            engine.send_quote()

    def test_approval_allows_sending(self):
        engine = WorkflowEngine()

        engine.data["quote"] = {
            "aircraft": "Citation CJ3",
            "route": "San Francisco to Las Vegas",
            "passengers": 4,
            "price": 12500
        }

        engine.approved = True
        engine.send_quote()

        self.assertIn("sent_quote", engine.data)

    def test_invalid_transition_is_rejected(self):
        engine = WorkflowEngine()

        with self.assertRaises(ValueError):
            engine.transition(WorkflowState.COMPLETE)

    def test_initial_state(self):
        engine = WorkflowEngine()

        self.assertEqual(
            engine.state,
            WorkflowState.START
        )


if __name__ == "__main__":
    unittest.main()
