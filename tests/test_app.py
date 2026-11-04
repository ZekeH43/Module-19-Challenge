import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class InterfaceTests(unittest.TestCase):
    def launch(self, entry="app.py"):
        return AppTest.from_file(
            str(Path(__file__).resolve().parents[1] / entry), default_timeout=20
        ).run()

    def test_quote_payment_and_session_isolation(self):
        app = self.launch()
        app.selectbox[0].set_value("Ash")
        app.text_input[0].set_value("1.25").run()
        self.assertIn("0.4125", " ".join(x.value for x in app.markdown))
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertIn("Confirmed payment to Ash", app.success[0].value)
        self.assertEqual(len(app.session_state["wallet"].history), 1)
        app.run()
        self.assertEqual(len(app.session_state["wallet"].history), 1)
        self.assertEqual(self.launch().session_state["wallet"].history, [])

    def test_invalid_quote_and_original_entry(self):
        app = self.launch("Starter_Code/krypto_jobs.py")
        app.text_input[0].set_value("-2").run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertTrue(app.button[0].disabled)
        self.assertEqual(app.session_state["wallet"].history, [])
