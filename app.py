from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import io
import csv

app = Flask(__name__)
app.secret_key = 'flash message'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Numeric(12, 2), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __init__(self, name, cost, qty):
        self.name = name
        self.cost = cost
        self.qty = qty

    def __repr__(self) -> str:
        return "Inventory({}, {}, {}, {})".format(self.id, self.name, self.cost, self.qty)

@app.route('/')
def Index():
    data = Inventory.query.all()
    return render_template('index.html', inventory=data)

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        flash('Data Inserted Successfully')
        name = request.form['name']
        cost = request.form['cost']
        qty = request.form['qty']

        new_data = Inventory(name, cost, qty)
        db.session.add(new_data)
        db.session.commit()

        return redirect(url_for('Index'))

@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        cost = request.form['cost']
        qty = request.form['qty']

        item = Inventory.query.get(id_data)
        item.name = name
        item.cost = cost
        item.qty = qty

        db.session.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('Index'))

@app.route('/delete/<string:id_data>', methods=['POST', 'GET'])
def delete(id_data):
    item = Inventory.query.get(id_data)
    db.session.delete(item)
    db.session.commit()
    flash('Data Deleted Successfully')
    return redirect(url_for('Index'))

@app.route('/download')
def download():
    data = Inventory.query.all()
    output = io.StringIO()
    writer = csv.writer(output)

    line = ['Id, Item Name, Cost, Qty']
    writer.writerow(line)
    
    for row in data:
        # try to not stringify it
        line = [str(row.id) + ',' + str(row.name) + ',' + str(row.cost) + ',' + str(row.qty)]
        writer.writerow(line)    
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=inventory_report.csv"})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=False)