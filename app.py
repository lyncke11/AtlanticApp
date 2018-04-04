# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atlanticapp.db'
db = SQLAlchemy(app)

# order of the columns in input
COLS = ['cust_id',
        'cust_first_name',
        'cust_last_name',
        'cust_street',
        'cust_state',
        'cust_zip_code',
        'purchase_status',
        'prod_id',
        'prod_name',
        'purchase_amt',
        'purchase_date']

class Customer(db.Model):
    __tablename__ = 'customer'
    #id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, primary_key=True)
    cust_first_name = db.Column(db.String)
    cust_last_name = db.Column(db.String)
    cust_street = db.Column(db.String)
    cust_state = db.Column(db.String)
    cust_zip_code = db.Column(db.Integer)

class Product(db.Model):
    __tablename__ = 'product'
    #id = db.Column(db.Integer, primary_key=True)
    prod_id = db.Column(db.Integer, primary_key=True)
    prod_name = db.Column(db.String)

class Purchase(db.Model):
    tablename = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    # for normalization purposes, have a customer id column only instead of all customer data
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.cust_id'))
    customer = db.relationship("Customer", backref=db.backref("customer", uselist=False))
    # for normalization purposes, have a product id column only insead of all product data
    prod_id = db.Column(db.Integer, db.ForeignKey('product.prod_id'))
    product = db.relationship("Product", backref=db.backref("product", uselist=False))
    purchase_amt = db.Column(db.String)
    purchase_date = db.Column(db.String)
    
def writeCustomer(row):
    # first make sure customer is not already in table
    customer_id = row[COLS.index('cust_id')]
    exists = db.session.query(Customer.cust_id).filter_by(cust_id=customer_id).scalar() is not None
    if not exists:
        custRow = Customer(cust_id=customer_id,
                           cust_first_name=row[COLS.index('cust_first_name')],
                           cust_last_name=row[COLS.index('cust_last_name')],
                           cust_street=row[COLS.index('cust_street')],
                           cust_state=row[COLS.index('cust_state')],
                           cust_zip_code=row[COLS.index('cust_zip_code')])

        db.session.add(custRow)
        db.session.commit()

def writeProduct(row):
    # first make sure product not aleady in table
    product_id = row[COLS.index('prod_id')]
    exists = db.session.query(Product.prod_id).filter_by(prod_id=product_id).scalar() is not None
    if not exists:
        prodRow = Product(prod_id=product_id,
                          prod_name=row[COLS.index('prod_name')])
        db.session.add(prodRow)
        db.session.commit()

def writePurchase(row):
    purchaseRow = Purchase(cust_id=row[COLS.index('cust_id')],
                           prod_id=row[COLS.index('prod_id')],
                           purchase_amt=row[COLS.index('purchase_amt')],
                           purchase_date=row[COLS.index('purchase_date')])
    db.session.add(purchaseRow)
    db.session.commit()

def writeRow(row):
    writeCustomer(row)
    writeProduct(row)
    writePurchase(row)

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['inputFile']

    data = file.read().splitlines()
    
    for row in data:
        row = row.split('\t')
        writeRow(row)

    return 'Saved ' + file.filename + ' to the db'

if __name__ == "__main__":
    app.run(debug=True)