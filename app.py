"""Run with: python -m streamlit run app.py."""

from pathlib import Path

import streamlit as st

from hiring import CANDIDATES, DemoWallet, eth, quote

IMAGES = Path(__file__).resolve().parent / "Starter_Code" / "Images"


def main():
    st.title("KryptoJobs2Go")
    st.write(
        "Hire a fictional fintech professional on a local Ethereum test chain. No real funds move."
    )
    if "wallet" not in st.session_state:
        st.session_state.wallet = DemoWallet()
    wallet = st.session_state.wallet
    name = st.selectbox("Professional", list(CANDIDATES))
    candidate = CANDIDATES[name]
    st.image(str(IMAGES / candidate.portrait), width=140)
    st.write(
        f"{name} · Rating {candidate.rating}/5 · {candidate.rate} test ETH per hour"
    )
    st.caption(f"Test recipient: {wallet.accounts[candidate.account_index]}")
    hours = st.text_input("Hours", value="1.00", max_chars=7)
    try:
        wage = quote(name, hours)
    except ValueError as error:
        st.error(str(error))
        wage = None
    if wage is not None:
        st.write(f"Quoted wage: {eth(wage)} test ETH, plus the test network fee.")
    if st.button("Pay on test chain", disabled=wage is None):
        try:
            payment = wallet.pay(name, hours)
        except ValueError as error:
            st.error(str(error))
        else:
            st.success(
                f"Confirmed payment to {name} in test block {payment.block_number}."
            )
    st.metric("Client balance (test ETH)", eth(wallet.balance))
    st.subheader("Confirmed payments")
    if wallet.history:
        st.dataframe(
            [
                {
                    "Professional": p.candidate,
                    "Wage (test ETH)": eth(p.value_wei),
                    "Fee (wei)": p.fee_wei,
                    "Block": p.block_number,
                    "Transaction hash": p.tx_hash,
                }
                for p in reversed(wallet.history)
            ],
            hide_index=True,
        )
    else:
        st.caption("Your first confirmed payment will appear here.")
    st.caption("Refreshing the page can reset this session's test chain and receipts.")


if __name__ == "__main__":
    main()
