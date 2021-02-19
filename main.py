from flask import Flask, request
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource, reqparse, inputs
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shifts.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('begin', type=inputs.datetime_from_iso8601)
parser.add_argument('end', type=inputs.datetime_from_iso8601)


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer)
    begin = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __repr__(self):
        return f"SHIFT: id:{self.id},worker_id:{self.worker_id}, begin:{self.begin},end:{self.end}"


class ShiftSchema(ma.Schema):
    class Meta:
        fields = ("id", "worker_id", "begin", "end")


shift_schema = ShiftSchema()
shifts_schema = ShiftSchema(many=True)


class ShiftListResourceByWorker(Resource):
    def get(self, worker_id):
        shifts = Shift.query.filter(Shift.worker_id == worker_id)
        return shifts_schema.dump(shifts)

    def post(self, worker_id):
        shift = Shift(worker_id=worker_id)
        args = parser.parse_args()
        if 'begin' in request.json:
            shift.begin = args['begin']
        if 'end' in request.json:
            shift.end = args['end']
        overlapping = Shift.query.filter(
            Shift.worker_id == worker_id,
            db.func.max(Shift.begin, shift.begin) <= db.func.min(Shift.end, shift.end))

        if overlapping.first() is not None:
            return 'Error: Requested shift overlaps or is adjacent to existing shift for this worker', 422

        db.session.add(shift)
        db.session.commit()
        return shift_schema.dump(shift)


class ShiftResourceByWorker(Resource):
    def get(self, shift_id, worker_id):
        shift = Shift.query.filter(Shift.worker_id == worker_id, Shift.id == shift_id)
        if shift.first() is None:
            return '', 404
        return shift_schema.dump(shift)

    def patch(self, shift_id, worker_id):
        shift = Shift.query.filter(Shift.worker_id == worker_id, Shift.id == shift_id)
        if shift.first() is None:
            return '', 404

        if 'begin' in request.json:
            shift.worker_id = request.json['begin']
        if 'end' in request.json:
            shift.worker_id = request.json['end']

        overlapping = Shift.query.filter(
            Shift.worker_id == worker_id,
            db.func.max(Shift.begin, shift.begin) <= db.func.min(Shift.end, shift.end))

        if overlapping.first() is not None:
            return 'Error: Requested shift overlaps or is adjacent to existing shift for this worker', 422
        db.session.commit()
        return shift_schema.dump(shift)

    def delete(self, shift_id, worker_id):
        shift = Shift.query.filter(Shift.worker_id == worker_id, Shift.id == shift_id)
        if shift.first() is None:
            return '', 404
        db.session.delete(shift)
        db.session.commit()
        return '', 204


api.add_resource(ShiftListResourceByWorker, '/shifts/<int:worker_id>')
api.add_resource(ShiftResourceByWorker, '/shifts/<int:worker_id>/<int:shift_id>')

if __name__ == '__main__':
    db.create_all()
    app.run()
