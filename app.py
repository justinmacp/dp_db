import streamlit as st
from src.utils import mechanisms, io

# SQLite database connection
DATABASE = 'data/titanic.db'
USER_ID = 1


# Streamlit app
st.title("Differential Privacy Web Interface")

# Sidebar settings
st.sidebar.header("Settings")
privacy_budget = float(io.query_database("SELECT PRIVACY_BUDGET FROM USERS WHERE ID = 1", DATABASE))
budget = st.sidebar.write(f"Your total privacy budget is {privacy_budget}")
epsilon = st.sidebar.number_input(
    "Epsilon (privacy budget for query)", min_value=0.1, max_value=privacy_budget, value=1.0, step=0.1
)
LOWER_BOUND = st.sidebar.number_input("Lower bound for sums and averages")
UPPER_BOUND = st.sidebar.number_input("Upper bound for sums and averages")

# Query options
query_type = st.selectbox(
    "Select Query Type",
    options=["Count", "Sum", "Average"]
)


# Execute the selected query
if st.button("Run Query"):
    if query_type == "Count":
        dp_result = mechanisms.count_with_laplacian_mechanism(epsilon=epsilon, db=DATABASE, user_id=USER_ID)
        st.write(f"Differentially Private Count: {dp_result}")
    elif query_type == "Sum":
        dp_result = mechanisms.sum_with_laplacian_mechanism(
            column='Age',
            epsilon=epsilon,
            lower_bound=LOWER_BOUND,
            upper_bound=UPPER_BOUND,
            db=DATABASE,
            user_id=USER_ID
        )
        st.write(f"Differentially Private Sum: {dp_result}")
    elif query_type == "Average":
        dp_result = mechanisms.average_with_laplacian_mechanism(
            column='Age',
            epsilon=epsilon,
            lower_bound=LOWER_BOUND,
            upper_bound=UPPER_BOUND,
            db=DATABASE,
            user_id=USER_ID
        )
        st.write(f"Differentially Private Average: {dp_result}")
