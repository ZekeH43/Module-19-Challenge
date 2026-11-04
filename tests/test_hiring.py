import unittest
from unittest.mock import patch

from hiring import CANDIDATES, DemoWallet, WEI, eth, quote


class HiringTests(unittest.TestCase):
    def test_exact_fractional_wage(self):
        self.assertEqual(quote("Ash", "1.25"), 412_500_000_000_000_000)
        self.assertEqual(eth(1), "0.000000000000000001")
        self.assertEqual(eth(WEI), "1")

    def test_invalid_hours_and_unknown_candidate(self):
        for hours in ("0", "-1", "NaN", "Infinity", "1.234", "", "10000", "1e3"):
            with self.subTest(hours=hours), self.assertRaises(ValueError):
                quote("Lane", hours)
        with self.assertRaises(ValueError):
            quote("Unknown", "1")

    def test_distinct_recipients_and_confirmed_balance_changes(self):
        w = DemoWallet()
        targets = [w.accounts[c.account_index] for c in CANDIDATES.values()]
        self.assertEqual(len(set(targets + [w.accounts[0]])), 5)
        before = w.balance
        balance = w.chain.get_balance(targets[3])
        p = w.pay("Kendall", "2")
        self.assertEqual(p.recipient, targets[3])
        self.assertEqual(w.chain.get_balance(p.recipient) - balance, 32 * WEI // 100)
        self.assertEqual(before - w.balance, p.value_wei + p.fee_wei)
        self.assertGreater(p.fee_wei, 0)
        self.assertEqual(w.chain.get_transaction_receipt(p.tx_hash)["status"], 1)
        self.assertEqual(w.history, [p])

    def test_insufficient_balance_does_not_send(self):
        w = DemoWallet()
        with (
            patch.object(w.chain, "get_balance", return_value=quote("Jo", "1")),
            self.assertRaises(ValueError),
        ):
            w.pay("Jo", "1")
        self.assertEqual(w.chain.get_block_by_number("latest")["number"], 0)
        self.assertEqual(w.history, [])

    def test_failed_receipt_never_appears_in_confirmed_history(self):
        w = DemoWallet()
        with (
            patch.object(w.chain, "send_transaction", return_value="stub"),
            patch.object(
                w.chain, "get_transaction_receipt", return_value={"status": 0}
            ),
            self.assertRaises(ValueError),
        ):
            w.pay("Jo", "1")
        self.assertEqual(w.history, [])
