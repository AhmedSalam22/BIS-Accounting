import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt


st.title("Accounting process Automation for sole proprietorship ")
# path = st.text_input("please input the file path")

uploaded_file = st.file_uploader("Choose a xlsx file", type="xlsx")


@st.cache(persist=True)
def load_data(uploaded_file):
    accounts = pd.read_excel(uploaded_file)
    journal = pd.read_excel(uploaded_file , sheet_name=1)
    df = pd.merge(accounts , journal , how='outer' , left_on="Account_ID" , right_on="Account_id" )
    df.drop(columns=["Account_ID", "Account_id" , "Type_y" , "Helper2", "Balance"] , inplace= True)

    return df

if uploaded_file != None :
    df = load_data(uploaded_file)
    # filter by date if user want 
    if st.sidebar.checkbox("Do you want to filter data by date between?" , False):
        d = st.sidebar.date_input("Start date", datetime.date(2019, 7, 6))
        d2 = st.sidebar.date_input("End date", datetime.date(2019, 8, 6))
        if st.sidebar.button("Filter"):
            df = df.query('Date >= @d and Date <= @d2')
            st.sidebar.header("Filter is applied")
        else:
            st.sidebar.header("No filter")

    
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

def prepare_finacial_statement():
    assest = df.query('Type_x == "Assest"').pivot_table(values="Helper" , index="Account" , columns="Normal Balance" ,aggfunc=np.sum, fill_value=0)
    total_assest= assest.sum()
    assest[""] = ""
    
    liabilities = df.query('Type_x == "liabilities"').pivot_table(values="Helper" , index="Account" , columns="Normal Balance" ,aggfunc=np.sum, fill_value=0)
    total_liabilities = liabilities.sum()
    return assest , total_assest , liabilities ,total_liabilities

@st.cache(persist=True)
def account_in_ledger(name):
    account = df[["Account" , "Date" , "Account Title and Explanation"  , "Debit" , "Credit" , "Helper"]].query('Account == @name')
    account["Balance"] = np.cumsum(df["Helper"])
    account.drop(columns=["Account" , "Helper"]  , inplace =True)
    return account




# Financial statements
if st.sidebar.checkbox("Prepare  financial statements" , False):
    st.header("Trial Balance")
    trial_balance , trial_balance_sum = prepare_trial_balance()
    st.table(trial_balance )
    st.write(trial_balance_sum)

    # add bar chart
    trial_balance.plot(kind="bar" , figsize=(5,15))
    st.pyplot()



    st.title("")
    st.header("Net Income")
    net_income  , net_income_sum = prepare_net_income()
    st.table(net_income)
    st.write(net_income_sum)
    # add pie chart
    net_income_sum.plot(kind="pie" , figsize= (5,5) )
    st.pyplot()


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

    st.header('Financial statements')
    assest , total_assest , liabilities ,total_liabilities = prepare_finacial_statement()

    st.markdown("#### Assest")
    st.table(assest)
    st.markdown("#### Tota Assest amount")
    st.table(total_assest)
    st.markdown("#### liabilities")
    st.table(liabilities)
    st.markdown("#### Tota liabilities amount")
    st.table(total_liabilities)
    st.markdown("#### Owner's Equity:\n{}".format(equity))

#  Ledger
if st.sidebar.checkbox("Show Ledger" , False):
    account = st.sidebar.selectbox("Account" , list(df.Account.unique()))
    st.header("Ledger for {account}".format(account= account))
    ledger = account_in_ledger(account)
    st.table(ledger)
    #Dynamic line chart
    line_chart = ledger.iloc[: ,np.r_[0,4]]
    line_chart.plot(x="Date" , y="Balance")
    st.pyplot()



st.markdown("<br><br>" , True)
st.markdown("##### copyright@Ahmed Maher Fouzy Mohamed Salam 221999")