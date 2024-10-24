from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the User model (table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hobby = db.Column(db.String(100), nullable=False)
    education = db.Column(db.String(100), nullable=False)
    interest = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(100), nullable=False)
    happiness = db.Column(db.Integer, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        hobby = request.form.get("hobby")
        education = request.form.get("education")
        interest = request.form.get("interest")
        job = request.form.get("job")
        happiness = request.form.get("happiness")

        # Create a new user record
        new_user = User(name=name, hobby=hobby, education=education, interest=interest, job=job, happiness=happiness)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to the same page to show the updated table
        return redirect("/")

    # Read all users from the database
    all_users = User.query.all()

    return render_template("index.html", user_data=all_users)

@app.route("/download")
def download():
    # Fetch all users from the database
    all_users = User.query.all()

    # Create a list of dictionaries for each user's data
    data = [{
        'Name': user.name,
        'Hobby': user.hobby,
        'Education': user.education,
        'Interest': user.interest,
        'Job': user.job,
        'Happiness': user.happiness
    } for user in all_users]

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')
        # No need to call writer.save() here, as it's done automatically when using 'with'
    
    # Seek to the beginning of the stream
    output.seek(0)

    # Send the file as an attachment to be downloaded
    return send_file(output, as_attachment=True, download_name="user_data.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Clear All Route
@app.route("/clear", methods=["GET"])
def clear():
    User.query.delete()  # Delete all entries
    db.session.commit()  # Commit the changes to the database
    return redirect("/")  # Redirect back to the main page

if __name__ == "__main__":
    app.run(debug=True)
