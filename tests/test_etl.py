import unittest
from unittest.mock import Mock, patch

from src.etl import extract, remove_sensitive_data, create_location_table, create_transaction_table, normalise_df_breakdown, normalise_df_cleanse, create_product_table
import datetime
import pandas as pd
from pandas._testing import assert_frame_equal

mock_df = extract("tests/mock_csv.csv")
mock_df = remove_sensitive_data(mock_df)

mock_df2 = extract("tests/mock_csv2.csv")
mock_df2 = remove_sensitive_data(mock_df2)

def test_extract():
    assert_frame_equal(extract("tests/mock_csv.csv"), pd.DataFrame({
        "datetime": datetime.datetime(2021, 2, 23, 9, 0, 48),
        "location": "Isle of Wight",
        "customer_info": "Morgan Berka",
        "basket": "Large,Hot chocolate,2.9,Large,Chai latte,2.6,Large,Hot chocolate,2.9",
        "payment_method": "CASH",
        "total_cost": 8.40,
        "card_details": "None"
        },index=[0]))
    
def test_remove_sensitive_data():
    mock_df = extract("tests/mock_csv.csv")
    assert_frame_equal(remove_sensitive_data(mock_df), pd.DataFrame({
        "datetime": datetime.datetime(2021, 2, 23, 9, 0, 48),
        "location": "Isle of Wight",
        "basket": "Large,Hot chocolate,2.9,Large,Chai latte,2.6,Large,Hot chocolate,2.9",
        "payment_method": "CASH",
        "total_cost": 8.40,
        },index=[0]))

def test_create_location_table():
    with patch("uuid.uuid4", return_value="3288e242-1d0e-4f3e-adf7-89bc0be4b7b1"):
        assert_frame_equal(create_location_table(mock_df), pd.DataFrame({
            "location_id": "3288e242-1d0e-4f3e-adf7-89bc0be4b7b1",
            "location_name": "Isle of Wight"
            },index=[0]))

def test_create_transaction_table(): # create_transaction_table needs new dependency "location"
    with patch("uuid.uuid4", return_value="3288e242-1d0e-4f3e-adf7-89bc0be4b7b1"):
        mock_location = create_location_table(mock_df)
        mock_location_id = mock_location.loc[0].at["location_id"]
        assert_frame_equal(create_transaction_table(mock_df, mock_location), pd.DataFrame({ # 
            "transaction_id": "3288e242-1d0e-4f3e-adf7-89bc0be4b7b1",
            "location_id": mock_location_id,
            "datetime": datetime.datetime(2021, 2, 23, 9, 0, 48),
            "payment_method": "CASH",
            "total_cost": 8.40
            },index=[0]))

def test_normalise_df_breakdown():
    assert_frame_equal(normalise_df_breakdown(mock_df), pd.DataFrame({
        "datetime": [datetime.datetime(2021, 2, 23, 9, 0, 48), datetime.datetime(2021, 2, 23, 9, 0, 48), datetime.datetime(2021, 2, 23, 9, 0, 48)],
        "location": ["Isle of Wight", "Isle of Wight", "Isle of Wight"],
        "payment_method": ["CASH", "CASH", "CASH"],
        "total_cost": [8.40, 8.40, 8.40],
        "size": ["Large", "Large", "Large"],
        "name": ["Hot chocolate", "Chai latte", "Hot chocolate"],
        "price": [2.90, 2.60, 2.90]
    }))

# Need to add df.loc[df["type"] == None] = "None" to change NoneType values to "None" string values

# def test_normalise_df_cleanse():
#     assert_frame_equal(normalise_df_cleanse(mock_df), pd.DataFrame({
#         "datetime": [datetime.datetime(2021, 2, 23, 9, 0, 48), datetime.datetime(2021, 2, 23, 9, 0, 48), datetime.datetime(2021, 2, 23, 9, 0, 48)],
#         "location": ["Isle of Wight", "Isle of Wight", "Isle of Wight"],
#         "payment_method": ["CASH", "CASH", "CASH"],
#         "size": ["large", "large", "large"],
#         "name": ["hot chocolate", "chai latte", "hot chocolate"],
#         "price": [2.90, 2.60, 2.90],
#         "total_cost": [8.40, 8.40, 8.40]
#     }))

# def test_normalise_df_cleanse2():
#     assert_frame_equal(normalise_df_cleanse(mock_df2), pd.DataFrame({
#         "datetime": [datetime.datetime(2021,2,23,9,2,27), datetime.datetime(2021,2,23,9,2,27), datetime.datetime(2021,2,23,9,2,27), datetime.datetime(2021,2,23,9,2,27), datetime.datetime(2021,2,23,9,2,27)],
#         "location": ["Isle of Wight", "Isle of Wight", "Isle of Wight", "Isle of Wight", "Isle of Wight"],
#         "payment_method": ["CARD", "CARD", "CARD", "CARD", "CARD"],
#         "size": ["", "", "", "", ""],
#         "name": ["frappes", "cortado", "glass of milk", "speciality tea", "speciality tea"],
#         "type": ["coffee", None, None, "camomile", "camomile"],
#         "price": [2.75, 2.05, 0.70, 1.30, 1.30],
#         "total_cost": [8.10, 8.10, 8.10, 8.10, 8.10]
#     }))

# def test_creat_product_table():
#     mock_data = normalise_df_cleanse(mock_df)
#     assert_frame_equal(create_product_table(mock_df, mock_data), pd.DataFrame({ 
#         "product_id": [mock_data.loc[0].at["location_id"], mock_data.loc[1].at["location_id"]],
#         "size": ["large", "large"],
#         "name": ["hot chocolate", "chai latte"],
#         "type": [None, None]
#     }))

# def test_creat_product_table2():
#     mock_data = normalise_df_cleanse(mock_df2)
#     assert_frame_equal(create_product_table(mock_df2, mock_data), pd.DataFrame({
#         "product_id": 
