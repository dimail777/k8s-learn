import os, socket, datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "echo": True,
    "echo_pool": "debug",
    "pool_pre_ping": True,
}

db = SQLAlchemy(app)


class Transactions(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(100))
    amount = db.Column(db.Integer)

    def __init__(self, client_id, amount):
        self.client_id = client_id
        self.amount = amount

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'amount': self.amount,
        }


@app.route("/ping")
def hello():
    return "pong"


@app.route("/add", methods=['POST'])
def add_transaction():
    client_id = request.args.get('client_id')
    amount = request.args.get('amount')
    try:
        transaction = Transactions(
            client_id=client_id,
            amount=amount,
        )
        db.session.add(transaction)
        db.session.commit()

        log_to_file(client_id, amount, os.environ['LOG_FILE'])
        return "Transaction added. transaction id={}".format(transaction.id)
    except Exception as e:
        return (str(e))


@app.route("/getall")
def get_all():
    try:
        transactions = Transactions.query.all()
        return jsonify([e.serialize() for e in transactions])
    except Exception as e:
        return (str(e))


@app.route("/get/<id_>")
def get_by_id(id_):
    try:
        transaction = Transactions.query.filter_by(id=id_).first()
        return jsonify(transaction.serialize())
    except Exception as e:
        return (str(e))


def log_to_file(client_id, amount, filename):
    hostname = socket.gethostname()
    time_now = datetime.datetime.now()
    time_format = "%Y-%m-%d %H:%M:%S"
    with open(filename, 'a+') as f:
        f.write(f"{time_now.strftime(time_format)}: host {hostname}, client {client_id}, amount {amount} \n")


if __name__ == '__main__':
    db.create_all()
    app.run("0.0.0.0", 8080)
