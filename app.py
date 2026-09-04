import json
import random
import string
from pathlib import Path

import streamlit as st


class Bank:
    database = "data.json"
    data = []

    # Load database
    try:
        if Path(database).exists():
            with open(database, "r") as fs:
                data = json.load(fs)
        else:
            data = []
    except Exception as err:
        st.error(f"An exception occurred: {err}")
        data = []

    @classmethod
    def __update(cls):
        with open(cls.database, "w") as fs:
            json.dump(cls.data, fs, indent=4)

    @classmethod
    def __accountgenerate(cls):
        alpha = random.choices(string.ascii_letters, k=3)
        num = random.choices(string.digits, k=3)
        spchr = random.choices("!@#$%^&*", k=1)

        account_id = alpha + num + spchr
        random.shuffle(account_id)

        return "".join(account_id)

    @classmethod
    def find_account(cls, account_number, pin):
        return next(
            (
                account
                for account in cls.data
                if account["accountNo."] == account_number
                and str(account["pin"]) == str(pin)
            ),
            None,
        )

    @classmethod
    def create_account(cls, name, age, email, pin):
        if age < 18:
            return False, "You must be at least 18 years old."

        if not pin.isdigit() or len(pin) != 4:
            return False, "PIN must contain exactly 4 digits."

        
        account_number = cls.__accountgenerate()

        info = {
            "name": name,
            "age": age,
            "email": email,
            "pin": pin,
            "accountNo.": account_number,
            "balance": 0,
        }

        cls.data.append(info)
        cls.__update()

        return True, info

    @classmethod
    def deposit(cls, account_number, pin, amount):
        account = cls.find_account(account_number, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if amount <= 0:
            return False, "Amount must be greater than 0."

        if amount > 10000:
            return False, "You can deposit a maximum of ₹10,000 at a time."

        account["balance"] += amount
        cls.__update()

        return True, account["balance"]

    @classmethod
    def withdraw(cls, account_number, pin, amount):
        account = cls.find_account(account_number, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if amount <= 0:
            return False, "Amount must be greater than 0."

        if amount > account["balance"]:
            return False, "Insufficient balance."

        account["balance"] -= amount
        cls.__update()

        return True, account["balance"]

    @classmethod
    def get_details(cls, account_number, pin):
        account = cls.find_account(account_number, pin)

        if not account:
            return None

        return account

    @classmethod
    def update_details(
        cls,
        account_number,
        pin,
        new_name,
        new_email,
        new_pin,
    ):
        account = cls.find_account(account_number, pin)

        if not account:
            return False, "Invalid account number or PIN."

        if new_name:
            account["name"] = new_name

        if new_email:
            account["email"] = new_email

        if new_pin:
            if not new_pin.isdigit() or len(new_pin) != 4:
                return False, "New PIN must contain exactly 4 digits."

            account["pin"] = new_pin

        cls.__update()

        return True, "Details updated successfully."

    @classmethod
    def delete_account(cls, account_number, pin):
        account = cls.find_account(account_number, pin)

        if not account:
            return False, "Invalid account number or PIN."

        cls.data.remove(account)
        cls.__update()

        return True, "Account deleted successfully."




st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="centered",
)

st.title("🏦 Bank Management System")
st.caption("Simple banking application using Streamlit + JSON")

# Sidebar
menu = st.sidebar.radio(
    "Select an operation",
    [
        "Create Account",
        "Deposit Money",
        "Withdraw Money",
        "Account Details",
        "Update Details",
        "Delete Account",
    ],
)


# ---------------------------------------------------------
# CREATE ACCOUNT
# ---------------------------------------------------------

if menu == "Create Account":

    st.header(" Create Account")

    with st.form("create_account_form"):

        name = st.text_input("Full Name")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            step=1,
        )

        email = st.text_input("Email")

        pin = st.text_input(
            "4 Digit PIN",
            type="password",
            max_chars=4,
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True,
        )

        if submitted:

            if not name.strip():
                st.error("Please enter your name.")

            elif not email.strip():
                st.error("Please enter your email.")

            else:
                success, result = Bank.create_account(
                    name.strip(),
                    int(age),
                    email.strip(),
                    pin,
                )

                if success:
                    st.success("Account created successfully! ")

                    st.info(
                        f"Your account number is: **{result['accountNo.']}**"
                    )

                    st.write("### Account Information")

                    st.write(f"**Name:** {result['name']}")
                    st.write(f"**Age:** {result['age']}")
                    st.write(f"**Email:** {result['email']}")
                    st.write(f"**Account Number:** {result['accountNo.']}")
                    st.write(f"**Balance:** ₹{result['balance']}")

                    st.warning(
                        "Please save your account number safely."
                    )

                else:
                    st.error(result)


# ---------------------------------------------------------
# DEPOSIT
# ---------------------------------------------------------

elif menu == "Deposit Money":

    st.header(" Deposit Money")

    with st.form("deposit_form"):

        account_number = st.text_input(
            "Account Number"
        )

        pin = st.text_input(
            "PIN",
            type="password",
            max_chars=4,
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            max_value=10000.0,
            step=100.0,
        )

        submitted = st.form_submit_button(
            "Deposit Money",
            use_container_width=True,
        )

        if submitted:

            success, result = Bank.deposit(
                account_number,
                pin,
                amount,
            )

            if success:
                st.success("Amount deposited successfully! ")
                st.metric(
                    "New Balance",
                    f"₹{result:,.2f}",
                )
            else:
                st.error(result)


# ---------------------------------------------------------
# WITHDRAW
# ---------------------------------------------------------

elif menu == "Withdraw Money":

    st.header(" Withdraw Money")

    with st.form("withdraw_form"):

        account_number = st.text_input(
            "Account Number"
        )

        pin = st.text_input(
            "PIN",
            type="password",
            max_chars=4,
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=100.0,
        )

        submitted = st.form_submit_button(
            "Withdraw Money",
            use_container_width=True,
        )

        if submitted:

            success, result = Bank.withdraw(
                account_number,
                pin,
                amount,
            )

            if success:
                st.success("Amount withdrawn successfully! ")
                st.metric(
                    "Remaining Balance",
                    f"₹{result:,.2f}",
                )
            else:
                st.error(result)


# ---------------------------------------------------------
# ACCOUNT DETAILS
# ---------------------------------------------------------

elif menu == "Account Details":

    st.header(" Account Details")

    with st.form("details_form"):

        account_number = st.text_input(
            "Account Number"
        )

        pin = st.text_input(
            "PIN",
            type="password",
            max_chars=4,
        )

        submitted = st.form_submit_button(
            "Show Details",
            use_container_width=True,
        )

        if submitted:

            account = Bank.get_details(
                account_number,
                pin,
            )

            if account:

                st.success("Account found! ")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Name**")
                    st.write(account["name"])

                    st.write("**Age**")
                    st.write(account["age"])

                    st.write("**Email**")
                    st.write(account["email"])

                with col2:
                    st.write("**Account Number**")
                    st.write(account["accountNo."])

                    st.write("**Balance**")
                    st.write(f"₹{account['balance']:,.2f}")

                

            else:
                st.error(
                    "No account found with these credentials."
                )


# ---------------------------------------------------------
# UPDATE DETAILS
# ---------------------------------------------------------

elif menu == "Update Details":

    st.header("Update Details")

    st.info(
        "You can update your name, email, or PIN. "
        "Age, account number, and balance cannot be changed."
    )

    with st.form("update_form"):

        account_number = st.text_input(
            "Account Number"
        )

        old_pin = st.text_input(
            "Current PIN",
            type="password",
            max_chars=4,
        )

        new_name = st.text_input(
            "New Name (optional)"
        )

        new_email = st.text_input(
            "New Email (optional)"
        )

        new_pin = st.text_input(
            "New PIN (optional)",
            type="password",
            max_chars=4,
        )

        submitted = st.form_submit_button(
            "Update Details",
            use_container_width=True,
        )

        if submitted:

            if not new_name and not new_email and not new_pin:
                st.warning(
                    "Please enter at least one new detail."
                )

            else:

                success, message = Bank.update_details(
                    account_number,
                    old_pin,
                    new_name.strip(),
                    new_email.strip(),
                    new_pin,
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)


# ---------------------------------------------------------
# DELETE ACCOUNT
# ---------------------------------------------------------

elif menu == "Delete Account":

    st.header(" Delete Account")

    st.warning(
        " Deleting an account is permanent."
    )

    with st.form("delete_form"):

        account_number = st.text_input(
            "Account Number"
        )

        pin = st.text_input(
            "PIN",
            type="password",
            max_chars=4,
        )

        confirmation = st.checkbox(
            "I understand that this account will be permanently deleted."
        )

        submitted = st.form_submit_button(
            "Delete Account",
            use_container_width=True,
        )

        if submitted:

            if not confirmation:
                st.error(
                    "Please confirm that you want to delete the account."
                )

            else:

                success, message = Bank.delete_account(
                    account_number,
                    pin,
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.caption("Bank Management System")
st.sidebar.caption("Python + Streamlit + JSON")
