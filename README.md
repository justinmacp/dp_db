# Make your database differentially private

This project allows you to grant data analysts access to your data without revealing information on any individual in
your dataset by implementing differential privacy: https://en.wikipedia.org/wiki/Differential_privacy

In short it allows for data analysis, where answers to a query are indistinguishable from one another whether a
particular individual's data is contained in the dataset or not

# Setup with sample database

1. Clone the repository and cd into it

```
git clone https://github.com/justinmacp/dp_db.git
cd dp_db
```

2. Install all the requirements

```
conda install --yes --file requirements.txt
```

3. Start the streamlit app:

```
streamlit run login.py
```

4. You can then allow users to register and manage their privacy consumption