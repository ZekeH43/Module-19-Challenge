"""Quote demo wages in integer wei and settle them on a private, in-memory test EVM."""

from dataclasses import dataclass
from decimal import Decimal
import re

from eth_tester import EthereumTester, PyEVMBackend

WEI = 10**18
GAS = 21_000  # Plain transfer between accounts with no contract bytecode.


@dataclass(frozen=True)
class Candidate:
    name: str
    rating: str
    rate: Decimal  # Test ETH per hour, taken from the original assignment.
    account_index: int
    portrait: str


CANDIDATES = {
    p.name: p
    for p in (
        Candidate("Lane", "4.3", Decimal("0.20"), 1, "lane.jpeg"),
        Candidate("Ash", "5.0", Decimal("0.33"), 2, "ash.jpeg"),
        Candidate("Jo", "4.7", Decimal("0.19"), 3, "jo.jpeg"),
        Candidate("Kendall", "4.1", Decimal("0.16"), 4, "kendall.jpeg"),
    )
}


def quote(name: str, hours: str) -> int:
    """Accept up to two fractional hour digits; return the exact transfer value."""
    if name not in CANDIDATES:
        raise ValueError("Choose a listed candidate.")
    if not isinstance(hours, str) or not re.fullmatch(
        r"[0-9]{1,4}(\.[0-9]{1,2})?", hours.strip()
    ):
        raise ValueError(
            "Enter hours from 0.01 to 9999.99 with at most two decimal places."
        )
    quantity = Decimal(hours.strip())
    if quantity <= 0:
        raise ValueError("Hours must be greater than zero.")
    return int(CANDIDATES[name].rate * quantity * WEI)


def eth(value: int) -> str:
    """Format an integer number of wei without floating-point rounding."""
    whole, remainder = divmod(value, WEI)
    return f"{whole}.{remainder:018d}".rstrip("0").rstrip(".")


@dataclass(frozen=True)
class Payment:
    candidate: str
    recipient: str
    value_wei: int
    fee_wei: int
    tx_hash: str
    block_number: int


class DemoWallet:
    def __init__(self):
        # Explicit backend: no RPC URL, .env, imported seed, or fallback network.
        self.chain = EthereumTester(backend=PyEVMBackend())
        self.accounts = self.chain.get_accounts()
        self.history: list[Payment] = []

    @property
    def balance(self) -> int:
        return self.chain.get_balance(self.accounts[0])

    def pay(self, name: str, hours: str) -> Payment:
        """Submit to this session's EVM and record only a mined, successful receipt."""
        value = quote(name, hours)
        recipient = self.accounts[CANDIDATES[name].account_index]
        tip = 10**9
        fee_cap = 2 * self.chain.get_block_by_number("latest")["base_fee_per_gas"] + tip
        if value + GAS * fee_cap > self.balance:
            raise ValueError(
                "The demo account cannot cover the wage and maximum network fee."
            )
        tx_hash = self.chain.send_transaction(
            {
                "from": self.accounts[0],
                "to": recipient,
                "value": value,
                "gas": GAS,
                "max_fee_per_gas": fee_cap,
                "max_priority_fee_per_gas": tip,
            }
        )
        receipt = self.chain.get_transaction_receipt(tx_hash)
        if receipt["status"] != 1:
            raise ValueError("The test chain did not confirm a successful payment.")
        payment = Payment(
            name,
            recipient,
            value,
            receipt["gas_used"] * receipt["effective_gas_price"],
            tx_hash,
            receipt["block_number"],
        )
        self.history.append(payment)
        return payment
