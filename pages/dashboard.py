import streamlit as st
from src.utils import mechanisms, io
import navigation_bar
from src.utils.consts import DATABASE, TABLE_NAME, SCHEMA
import yaml


# Streamlit app
st.title("Differential Privacy Web Interface")

navigation_bar.make_sidebar()

st.sidebar.write(f"Logged in as {st.session_state.username}")

st.session_state.privacy_budget = float(io.query_database(
    f"SELECT current_privacy_budget FROM users WHERE name = '{st.session_state.username}'",
    DATABASE
)[0][0])

with open(SCHEMA) as file:
    db_schema = yaml.load(file, Loader=yaml.loader.SafeLoader)

numerical_columns = db_schema[TABLE_NAME]['numerical']
categorical_columns = db_schema[TABLE_NAME]['categorical']

# Sidebar settings
st.sidebar.header("Settings")

query_budget = st.sidebar.write(f"Your total privacy budget is {st.session_state.privacy_budget}")
epsilon = st.sidebar.number_input(
    "Epsilon (privacy budget for query)", min_value=0.1, max_value=query_budget, value=1.0, step=0.1
)

# Query options
query_type = st.selectbox(
    "Select Query Type",
    options=["Count", "Sum", "Average", "Histogram"]
)

if query_type in ["Sum", "Average", "Histogram"]:
    column_name = st.selectbox(
        "Select Column",
        options=numerical_columns
    )
    LOWER_BOUND = st.sidebar.number_input("Lower bound")
    UPPER_BOUND = st.sidebar.number_input("Upper bound")
else:
    column_name = None
    LOWER_BOUND = None
    UPPER_BOUND = None

if query_type == "Histogram":
    bin_size = st.sidebar.number_input("Bin Size")
else:
    bin_size = None

# Execute the selected query
if st.button("Run Query"):
    try:
        if st.session_state.privacy_budget >= epsilon:
            if query_type == "Count":
                dp_result = mechanisms.count_with_laplacian_mechanism(
                    epsilon=epsilon, db=DATABASE, username=st.session_state.username
                )
                st.write(f"Differentially Private Count: {dp_result}")
            elif query_type == "Sum":
                dp_result = mechanisms.sum_with_laplacian_mechanism(
                    column=column_name,
                    epsilon=epsilon,
                    lower_bound=LOWER_BOUND,
                    upper_bound=UPPER_BOUND,
                    db=DATABASE,
                    username=st.session_state.username
                )
                st.write(f"Differentially Private Sum: {dp_result}")
            elif query_type == "Average":
                dp_result = mechanisms.average_with_laplacian_mechanism(
                    column=column_name,
                    epsilon=epsilon,
                    lower_bound=LOWER_BOUND,
                    upper_bound=UPPER_BOUND,
                    db=DATABASE,
                    username=st.session_state.username
                )
                st.write(f"Differentially Private Average: {dp_result}")
            elif query_type == "Histogram":
                dp_result = mechanisms.histogram_with_laplacian_mechanism(
                    column=column_name,
                    epsilon=epsilon,
                    lower_bound=LOWER_BOUND,
                    upper_bound=UPPER_BOUND,
                    bin_size=bin_size,
                    db=DATABASE,
                    username=st.session_state.username
                )
                pass
        else:
            raise Exception("The privacy budget allocated to this query exceeds your current total privacy budget")
    except Exception as e:
        st.error(e)
