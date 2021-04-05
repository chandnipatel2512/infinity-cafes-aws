import pandas as pd
import numpy as np
from datetime import datetime as dt
from decimal import Decimal as dec
from src.db.core import connection, check, update
import uuid
import csv

# EXTRACT ================================================


def extract(file_path):

    data = csv.reader(file_path)

    # convert data to dataframe
    df = pd.DataFrame(
        data,
        columns=[
            "datetime",
            "location_name",
            "customer_info",
            "basket",
            "payment_method",
            "total_cost",
            "card_details",
        ],
    )

    # remove rows with null values
    df.dropna(inplace=True)

    # convert values in column "datetime" to datetime objects
    df["datetime"] = pd.to_datetime(df["datetime"])

    # drop "customer name" column
    df.drop(["customer_info"], axis=1, inplace=True)

    # drop "card details" column
    df.drop("card_details", axis=1, inplace=True)

    return df


# TRANSFORM ===============================================

# Cleanse our data and organise it into rows to easily load each row in a database


def transform(df):

    # make a copy of the dataframe
    breakdown = df.copy()

    # reorder the columns
    reordered = breakdown[
        ["datetime", "location_name", "payment_method", "total_cost", "basket"]
    ]

    # An empty list to append new rows of data with breakdown of items in basket
    transformed_data = []

    # loop through the dataframe
    for i, row in reordered.iterrows():
        new_row = {}
        # Iterates through all columns other than basket, and adds column name and respectice value to dictionary
        for column in row.items():

            if column[0] != "basket":

                new_row[column[0]] = column[1]

            elif column[0] == "basket":

                # Splits basket row into list of values
                basket_split = column[1].split(",")

                index = 0
                # Stops when there are no more list_items to iterate through
                while index < len(basket_split):

                    new_row["size"] = basket_split[index]
                    new_row["name"] = basket_split[index + 1]
                    new_row["price"] = float(basket_split[index + 2])

                    split_type = new_row["name"].split("-")
                    # if the product has a name and type
                    try:
                        new_row["name"] = split_type[0].strip()
                        new_row["type"] = split_type[1].strip()
                    except IndexError:
                        # if the product has only a name, but no type
                        new_row["name"] = split_type[0]
                        new_row["type"] = ""

                    # Appends new row for each basket item -
                    # if there are multiple items purchased in one transaction,
                    # the same information for the non-basket key:value pairs is used,
                    # so only the product related columns will differ
                    transformed_data.append(new_row.copy())

                    index += 3

    return transformed_data


# LOAD ====================================================


def load_transaction(row, location_id, conn):
    # load transaction
    transaction_id = str(uuid.uuid4())
    date_time = row["datetime"]
    payment_type = row["payment_method"]
    total_cost = row["total_cost"]

    sql_insert_transaction = "INSERT INTO transaction (transaction_id, location_id, date_time, payment_type, total_cost) VALUES (%s, %s, %s, %s, %s)"
    update(
        conn,
        sql_insert_transaction,
        (transaction_id, location_id, date_time, payment_type, total_cost),
    )

    return transaction_id


def load_location(row, conn):
    # load location
    location_name = row["location_name"]

    location_id = str(uuid.uuid4())

    # check if location already exists in the database
    get_locations = "SELECT * FROM location WHERE name = %s"
    result = check(conn, get_locations, [location_name])

    # if the location doesn't already exists in db, make new id and add to db
    if result == []:

        sql_insert_locations = (
            "INSERT INTO location (location_id, name) VALUES (%s, %s)"
        )
        update(conn, sql_insert_locations, (location_id, location_name))
    else:
        # else get the existing id returned from the db
        location_id = result[0][0]

    return location_id


def load(data, conn):

    # load Location
    loc_id = load_location(data[0], conn)

    # load Transaction
    transaction_id = load_transaction(data[0], loc_id, conn)

    for row in data:

        # load product
        product_size = row["size"]
        product_name = row["name"]
        product_type = row["type"]

        # check if product already exists in the database
        get_products = (
            "SELECT * FROM product WHERE name = %s AND type = %s AND size = %s"
        )
        result = check(conn, get_products, [product_name, product_type, product_size])

        if result == []:
            product_id = str(uuid.uuid4())
            sql_insert_products = "INSERT INTO product (product_id, name, type, size) VALUES (%s, %s, %s, %s)"
            update(
                conn,
                sql_insert_products,
                (product_id, product_name, product_type, product_size),
            )
        else:
            product_id = result[0][0]

        # load basket

        price = row["price"]

        basket_id = str(uuid.uuid4())
        sql_insert_basket = "INSERT INTO basket(basket_id, transaction_id, product_id, price) VALUES (%s, %s, %s, %s)"
        update(conn, sql_insert_basket, (basket_id, transaction_id, product_id, price))
