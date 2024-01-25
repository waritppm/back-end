from flask import request, Flask, jsonify
from flask_basicauth import BasicAuth
from pymongo import MongoClient

uri = "mongodb+srv://yuiDB:Uri_nisit_1@cluster0.tuktswl.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["students"]
students_collection = db["std_info"]

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'username'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
app.config['BASIC_AUTH_FORCE'] = True

auth = BasicAuth(app)

@app.route("/")
def greet():
    return "<p>Welcome to Student Management API</p>"

@app.route("/students", methods=["GET"])
@auth.required
def get_all_students():
    students = list(students_collection.find({}, {"_id": 1, "fullname": 1, "major": 1, "gpa": 1}))
    return jsonify({"Students": students})

@app.route("/students/<string:std_id>", methods=["GET"])
@auth.required
def get_student_by_id(std_id):
    student = students_collection.find_one({"_id": std_id})
    if student:
        return jsonify(student)
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route("/students", methods={"POST"})
@auth.required
def create_student():
    data = request.get_json()
    student_id = data.get("_id")
    existing_student = students_collection.find_one({"_id": student_id})
    if existing_student:
        return jsonify({"error": "Cannot create a new student with the same _id"}), 500

    new_student = {
        "_id": student_id,
        "fullname": data["fullname"],
        "major": data["major"],
        "gpa": data["gpa"]
    }

    students_collection.insert_one(new_student)
    return jsonify(new_student)

@app.route("/students/<string:std_id>", methods=["DELETE"])
@auth.required
def delete_student(std_id):
    result = students_collection.delete_one({"_id": std_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Student deleted successfully"}), 200
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route("/students/<string:std_id>", methods=["PUT"])
@auth.required
def update_student(std_id):
    student = students_collection.find_one({"_id": std_id})
    if student:
        data = request.get_json()
        students_collection.update_one({"_id": std_id}, {"$set": data})
        updated_student = students_collection.find_one({"_id": std_id})
        return jsonify(updated_student), 200
    else:
        return jsonify({"message": "Student not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
