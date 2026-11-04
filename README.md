# KryptoJobs2Go: an Ethereum hiring demo

Pick a fictional professional, quote a wage for fractional hours, and pay it on an Ethereum test chain that runs in memory. The app shows the mined transaction's hash, block number, and fee. It requires no wallet credentials, Ganache installation, or external blockchain connection.

## Run the demo

Use Python 3.11 or 3.12. From a terminal:

```sh
git clone https://github.com/ZekeH43/Module-19-Challenge.git
cd Module-19-Challenge
```

**Windows PowerShell:**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

**WSL, Linux, or macOS:**

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Select **Ash** and enter **1.25** hours. The quote should be **0.4125 test ETH** (0.33 × 1.25). Choose **Pay on test chain** once. Look under **Confirmed payments** for the receipt and compare the wage with the separate fee. Each click creates a new payment; changing the hours or candidate alone does not.

## Follow a payment through the code

1. [app.py](app.py) displays the original candidate portraits, ratings, and rates. It keeps a separate wallet for each Streamlit session. A new session starts with prefunded test accounts; refreshing can discard the old chain.
2. [hiring.py](hiring.py) checks the chosen candidate and hours. It uses decimal arithmetic and converts the wage to integer wei before submission (1 ETH = 10¹⁸ wei). Accepted hours are 0.01–9999.99 with at most two fractional digits.
3. The wallet takes the recipient from the selected candidate's dedicated test account. It checks the client's balance against the wage plus the maximum possible fee, then sends a plain account-to-account transfer using the in-process Py-EVM backend.
4. The test backend mines the transfer. Only a receipt with a success status enters the payment history. The actual fee is gas used × effective gas price; it can be smaller than the fee allowance checked before sending.

**An interview exercise:** Explain why a transaction hash alone cannot establish that the recipient was paid. Then inspect [the balance-change test](tests/test_hiring.py): it checks the recipient's increase, the client's decrease, the fee, and the receipt for the same payment.

## Run the tests

```sh
python -m unittest discover -s tests -v
```

On Windows, use `.\.venv\Scripts\python` in place of `python`. The suite includes a transfer mined on the local EVM and simulated Streamlit interactions. It also checks rejected inputs, insufficient funds, failed receipts, and session isolation. CI runs the suite on Python 3.11 and 3.12.

## What changed from the classroom version

The old payment button omitted the blockchain client required by its helper, and two candidates shared an address. The current app keeps the four original profiles but maps them to distinct local recipients. Test accounts sign within the backend; the app no longer derives keys from a recovery phrase or connects to an RPC server. The [old launch path](Starter_Code/krypto_jobs.py) still opens the updated interface.

The [original assignment](Starter_Code/README.md) and [earlier screenshots](docs/original-screenshots.md) are historical material. Use the setup above for this version. This exercise demonstrates payment accounting and receipt handling; it does not verify identities, track real work hours, or send real funds. Test account addresses and keys must never be used for real assets.
