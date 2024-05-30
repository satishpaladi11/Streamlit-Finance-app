import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import numpy as np


# Initialize user data if not already present in the session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "income": 5000,
        "expenses": {
            "Housing": 1000,
            "Food": 500,
            "Transport": 300,
            "Entertainment": 200,
            "Others": 300,
        },
        "debts": {
            "Credit Card": 1000,
            "Student Loan": 500,
            "Car Loan": 700,
        }
    }

# Initialize default categories and user-added categories
if 'categories' not in st.session_state:
    st.session_state.categories = ["Housing", "Food", "Transport", "Entertainment", "Others"]

def main():
    with st.sidebar:
        selected = option_menu(
            "Main Menu",
            ["Home", "Add Expense", "Budget Tracker", "Debt Tracker"],
            icons=["house", "plus-circle", "calculator", "bar-chart"],
            menu_icon="cast",
            default_index=0,
        )
    
    if selected == "Home":
        home()
    elif selected == "Budget Tracker":
        budget_tracker()
    elif selected == "Debt Tracker":
        debt_tracker()
    elif selected == "Add Expense":
        add_expense()

    st.sidebar.markdown("---")
    donate_sidebar()

def home():
    st.title("Welcome to your Financial Dashboard")
    st.write("Use the sidebar to navigate through different sections.")
    st.markdown(
        """
        This dashboard helps you to manage your personal finances and debts effectively. 
        - **Budget Tracker**: Track your income and expenses.
        - **Debt Tracker**: Monitor your debts.
        - **Add Expense**: Quickly add your expenses.
        """
    )

def budget_tracker():
    st.title("Budget Tracker")
    st.info("Track your income and expenses")

    st.subheader("Update Monthly Income")
    new_income = st.number_input("Enter your new monthly income", value=st.session_state.user_data['income'], step=100, help="Update your monthly income to see how it affects your budget.")
    if new_income != st.session_state.user_data['income']:
        st.session_state.user_data['income'] = new_income
        st.success("Monthly income updated successfully!")

    st.write(f"**Monthly Income:** ${st.session_state.user_data['income']}")

    total_expenses = sum(st.session_state.user_data['expenses'].values())
    total_debts = sum(st.session_state.user_data['debts'].values())
    remaining_money = st.session_state.user_data['income'] - total_expenses - total_debts

    st.write(f"**Total Expenses:** ${total_expenses}")
    st.write(f"**Total Debts:** ${total_debts}")
    st.write(f"**Remaining Money:** ${remaining_money}")

    # Create a horizontal bar chart for income, expenses, debts, and remaining money
    data = {
        "Category": ["Income", "Expenses", "Debts", "Remaining Money"],
        "Amount": [st.session_state.user_data['income'], total_expenses, total_debts, remaining_money]
    }
    chart_df = pd.DataFrame(data)

    fig = px.bar(chart_df, x='Amount', y='Category', orientation='h', title='Financial Overview')
    fig.update_traces(marker_color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'], marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Amount ($)", yaxis_title="")
    st.plotly_chart(fig)

    st.subheader("Monthly Spending Breakdown and Expense Distribution")
    col1, col2 = st.columns(2)

    with col1:
        #st.subheader("Monthly Spending Breakdown")
        expense_data = {'Category': list(st.session_state.user_data['expenses'].keys()), 'Amount': list(st.session_state.user_data['expenses'].values())}
        expense_df = pd.DataFrame(expense_data)

        fig_bar = px.bar(expense_df, x='Category', y='Amount', title='Monthly Spending Breakdown')
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar)

    with col2:
        #st.subheader("Expense Distribution")
        remaining_money_abs = abs(remaining_money)
        expense_data = {
            'Category': list(st.session_state.user_data['expenses'].keys()) + ['Remaining Money'] + list(st.session_state.user_data['debts'].keys()),
            'Amount': list(st.session_state.user_data['expenses'].values()) + [remaining_money_abs] + list(st.session_state.user_data['debts'].values())
        }
        expense_df = pd.DataFrame(expense_data)

        fig_pie = px.pie(expense_df, names='Category', values='Amount', title='Expense Distribution')

        if fig_pie.data:
            # Change color for negative remaining money slice
            if remaining_money < 0:
                # Adjust pie chart colors for negative remaining money
                colors = np.array(px.colors.qualitative.Plotly)
                remaining_money_index = np.where(expense_df['Category'] == 'Remaining Money')[0]
                if len(remaining_money_index) > 0:
                    colors[remaining_money_index[0]] = '#1f77b4'  # Dark blue color for 'Remaining Money' slice
                fig_pie.update_traces(marker=dict(colors=colors, line=dict(color='#FFFFFF', width=1)))

                # Add annotation for deficit with professional appearance
                deficit_annotation = "Account Deficit: -${:,.2f}".format(remaining_money_abs)
                fig_pie.add_annotation(x=0.5, y=0.5, text=deficit_annotation, showarrow=False, font=dict(color="white", size=16))

        st.plotly_chart(fig_pie)

def debt_tracker():
    st.title("Debt Tracker")
    st.info("Track and manage your debts")

    st.subheader("Debt Portfolio")

    # Add new debt section
    st.write("Add a new debt")
    new_debt_type = st.text_input("Debt Type", key="new_debt_type")
    new_debt_amount = st.number_input("Debt Amount", min_value=0.0, step=1.0, format="%.2f", key="new_debt_amount")

    if st.button("Add Debt"):
        if new_debt_type and new_debt_amount:
            st.session_state.user_data['debts'][new_debt_type] = new_debt_amount
            st.success(f"Added {new_debt_type} with amount ${new_debt_amount:.2f}")

    # Update the debts in the session state
    debts_df = pd.DataFrame(list(st.session_state.user_data['debts'].items()), columns=['Debt Type', 'Amount'])
    edited_debts_df = st.data_editor(debts_df, num_rows="dynamic", key="debts_editor")

    # Check for changes in the data editor and update session state
    if edited_debts_df is not None:
        updated_debts = dict(zip(edited_debts_df['Debt Type'], edited_debts_df['Amount']))
        if updated_debts != st.session_state.user_data['debts']:
            st.session_state.user_data['debts'] = updated_debts

    # Ensure the chart is always displayed with the current data
    fig = px.bar(pd.DataFrame(list(st.session_state.user_data['debts'].items()), columns=['Debt Type', 'Amount']), x='Debt Type', y='Amount', title='Debt Portfolio')
    st.plotly_chart(fig)

def add_expense():
    st.title("Add a New Expense")
    st.info("Quickly add your expenses to keep track of your spending.")

    new_category = st.text_input("New Category Name", key="new_category_name")
    if new_category and new_category not in st.session_state.categories:
        st.session_state.categories.append(new_category)
        st.success(f"Category '{new_category}' has been added!")

    with st.form(key='expense_form'):
        category = st.selectbox("Expense Category", st.session_state.categories)
        amount = st.number_input("Expense Amount", min_value=0.0, step=1.0, format="%.2f")
        submit_button = st.form_submit_button(label='Add Expense')

    if submit_button:
        if category in st.session_state.user_data['expenses']:
            st.session_state.user_data['expenses'][category] += amount
        else:
            st.session_state.user_data['expenses'][category] = amount
        st.success(f"Added ${amount:.2f} to {category}")

def donate_sidebar():
    st.sidebar.subheader("❤️ Support Our Development ❤️")
    st.sidebar.write("""
        If you find this app useful, consider making a small donation. Your support helps us to keep improving and maintaining this tool. 
        Even a $1 donation can make a big difference. Thank you for your generosity!
    """)

    st.sidebar.markdown("""
    <a href="https://paypal.me/PaladiSathish?country.x=IN&locale.x=en_GB" target="_blank">
    <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="Donate with PayPal button" />
    </a>
    """, unsafe_allow_html=True)

    st.sidebar.write("""
        **Why Donate?**
        - Your support helps us maintain and improve this tool.
        - Every donation, no matter how small, makes a difference!
    """)

    st.sidebar.write("""
        **What Your Donation Supports:**
        - Server hosting and maintenance costs
        - Development of new features and enhancements
        - Community support and user engagement
    """)

    st.sidebar.write("""
        **Thank You for Your Support!**
        We greatly appreciate your generosity and contributions to our project. Together, we can make this tool even better!
    """)

if __name__ == "__main__":
    main()
