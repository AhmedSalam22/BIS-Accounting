import streamlit as st
import pandas as pd
import numpy as np


st.title("Accounting process Automation for sole proprietorship ")
path = st.text_input("please input the file path")

@st.cache(persist=True)
def load_data(path):
    accounts = pd.read_excel(path)
    journal = pd.read_excel(path , sheet_name=1)
    df = pd.merge(accounts , journal , how='outer' , left_on="Account_ID" , right_on="Account_id" )
    df.drop(columns=["Account_ID", "Account_id" , "Type_y" , "Helper2", "Balance"] , inplace= True)

    return df

if path != "" :
    df = load_data(path)
    
if st.checkbox("Show raw data" , False):
    st.write(df)

def prepare_trial_balance():
    trial_balance = df.pivot_table(values="Helper" , index="Account" , columns="Normal Balance" ,aggfunc=np.sum, fill_value=0)
    return trial_balance , trial_balance.sum()


def prepare_net_income():
    net_income = df.query('Type_x == "Revenue" or Type_x == "Expenses" ').pivot_table(index = "Account" , columns="Type_x" , values="Helper" , aggfunc=np.sum).sort_values('Revenue' , ascending=False)
    return net_income , net_income.sum()


def prepare_equity_statement():
    investment = df.query('Type_x == "Investment"')["Helper"].sum()
    drawings = df.query('Type_x == "Drawings"')["Helper"].sum()
    return  investment , drawings 

@st.cache(persist=True)
def account_in_ledger(name):
    return df[["Account" , "Date" , "Account Title and Explanation"  , "Debit" , "Credit"]].query('Account == @name').iloc[: , 1:]

# Financial statements
if st.sidebar.checkbox("Prepare  financial statements" , False):
    st.header("Trial Balance")
    trial_balance , trial_balance_sum = prepare_trial_balance()
    st.write(trial_balance , trial_balance_sum)

    st.header("Net Income")
    net_income  , net_income_sum = prepare_net_income()
    st.write(net_income , net_income_sum )

    amount = net_income_sum[1] - net_income_sum[0]
    if amount > 0 :
        st.write("There are a Net income by: {}".format(amount))
    else:
        st.write("There are a Net Loss by: {}".format(amount))


    st.header("Prepare owner's equity statements")
    investment ,  drawings = prepare_equity_statement()
    equity = investment + amount - drawings
    markdown = """
                | Owner's Equity Statement          |
                |-----------------------------------|:-------------:|-------------:|
                | Owner's capital investment        |               | {investment} |
                | Add net income/substract net loss |    {amount}   |              |
                | Less: Drawings                    |({drawings})   |              |
                | Owner's Equity is equal to        |               |    {equity}  |
                """.format(investment = investment , amount = amount , drawings = drawings , equity =  equity)
    st.markdown(markdown)

#  Ledger
if st.sidebar.checkbox("Show Ledger" , False):
    account = st.sidebar.selectbox("Account" , list(df.Account.unique()))
    st.header("Ledger for {account}".format(account= account))
    ledger = account_in_ledger(account)
    st.write(ledger)


st.markdown("##### copyright@Ahmed Maher Fouzy Mohamed Salam 221999")