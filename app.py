from flask import Flask, request, jsonify, make_response,render_template,redirect,url_for
from  flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv
import violation
import os

# initialising the database 

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
mysql=MySQL(app)

#bcrypt for securing the password
bcrypt=Bcrypt(app)
CORS(app,supports_credentials=True)

app.config["JWT_SECRET_KEY"] = "5298552117"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False


# root 

@app.route("/")
def home():
    return render_template('home.html')

# create account api

@app.route("/createAccount",methods=["GET","POST"])
def addUser():
    if  request.method=='GET':
        return render_template('signup.html')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')        
    cur=mysql.connection.cursor()
    if not email or not username or not password or not role:
        return render_template('signup.html',message="missing fields")
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    if role == "user":
        user_status="Good"
        user_score=100
        cur.execute("select * from users where username=%s",(username,))
        if cur.fetchone():
            return render_template('signup.html',message="an account with this username already exists")
        cur.execute("select * from users where email_id=%s",(email,))
        if cur.fetchone():
            return render_template('signup.html',message="an account exists with this email, please login instead")
        cur.execute("insert into users(username,email_id,user_status,user_score,user_password) values (%s,%s,%s,%s,%s)",(username,email,user_status,user_score,hashed_password))
    else:
        cur.execute("select * from admins where admin_name = %s",(username,))
        if cur.fetchone():
            return render_template('signup.html',message="an account with this username already exists")
        
        cur.execute("select * from admins where admin_email = %s",(email,))
        if cur.fetchone():
            return render_template('signup.html',message="an account exists with this email, please login instead")
        cur.execute(
        "INSERT INTO admins (admin_name, admin_email,admin_password) VALUES (%s, %s,%s)",
        (username, email,hashed_password)
        )
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('login_user'))


# login api 

@app.route("/login", methods=["GET","POST"])
def login_user():
    if request.method=="GET":
        return render_template('login.html')
    emailorname = request.form['emailorname']
    password = request.form['password']
    role = request.form['role']

    cur = mysql.connection.cursor()

    if role == "user":
        cur.execute("SELECT * FROM users WHERE username = %s OR email_id = %s", (emailorname, emailorname))
    else:
        cur.execute("SELECT * FROM admins WHERE admin_name = %s OR admin_email = %s", (emailorname, emailorname))
    
    user = cur.fetchone()
    if not user:
        return render_template("login.html",message="Invalid username or email")

    stored_password = user[5] if role == "user" else user[3]

    if not bcrypt.check_password_hash(stored_password, password):
        return render_template("login.html",message="incorrect password")

    user_id = user[0]

    response = make_response(jsonify({
        "message": "Login successful",
    }))

    if role=="user":
        return redirect(url_for('user_dashboard',id=user_id))
    else:
        return redirect(url_for('display_pending', id=user_id))
    

# user dashboard api

@app.route("/user/<int:id>/dashboard")
def user_dashboard(id):
    cur = mysql.connection.cursor()
    cur.execute("select * from users where user_id=%s",(id,))
    rows = cur.fetchone()
    if not rows:
        return jsonify({"message": "display failed, user doesn't exist"})
    column_names = [ desc[0] for desc in cur.description ]
    user_data = dict(zip(column_names, rows))
    cur.execute("select * from posts where poster_id=%s",(id,))
    rows = cur.fetchall()
    post_columns = [ desc[0] for desc in cur.description ]
    post_data = [ dict(zip(post_columns,row)) for row in rows]
    new_columns = [ 'post_id' , 'post_content' , 'post_status' ]
    return render_template('dashboard.html',user_data = user_data,columns = column_names,posts = post_data, post_columns = new_columns)

# create post api

@app.route("/user/<int:id>/createPost", methods=["GET","POST"])
def create_post(id):
    if request.method == 'GET':
        return render_template('createpostos.html',id=id,posted=False)
    user_id = id
    post_content = request.form.get("post_content", "").strip()
    cur = mysql.connection.cursor()
    li = violation.analyze_post(post_content)
    post_Score=int(li['sentiment_score']*10)
    post_status=li['final_thought']
    cur.execute(
        """
        INSERT INTO posts (
            post_content,
            poster_id,
            post_status,
            post_score
        ) VALUES (%s, %s, %s, %s)
        """,
        (post_content, user_id, post_status, post_Score)
    )
    if post_status=="good" or post_status=="deleted":
        cur.execute("select user_Score from users where user_id=%s",(user_id,))
        user_score=cur.fetchone()[0]
        user_score=violation.change_score(post_Score,post_status,user_score)
        cur.execute("update users set user_score=%s where user_id=%s",(user_score,user_id))
        print(user_score)
    mysql.connection.commit()
    return render_template('createpostos.html',id=user_id,posted=True)


# update post api ( pending )

""""
@app.route("/user/<int:id>/updatePost",methods=['PATCH'])
def update_post(id):
    cur = mysql.connection.cursor()
    cur.execute("select * from users where user_id=%s",(id,))
    if not cur.fetchone():
        cur.execute("select * from admins where admin_id=%s",(id,))
        if not cur.fetchone():
            return jsonify({"message": "user not found, please enter a valid userid"}),404
    data = request.json
    content = data['post_content']
    cur.execute(
        \"""
        UPDATE posts
        SET post_content = %s
        WHERE poster_id = %s
        \""",
        (content, id)
    )
    mysql.connection.commit()
    return jsonify({"message": "updated post successfully"}),200
"""

# pending posts api 

@app.route("/admin/<int:id>/getall",methods=['GET'])
def display_pending(id):
    admin_id = id
    cur = mysql.connection.cursor()
    cur.execute("select * from posts where post_status='admin'")
    rows = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    data = [ dict(zip(column_names,row)) for row in rows]
    new_column_names = [ 'post_id' , 'post_content' ]
    return render_template("adminspace.html",rows=data,columns = new_column_names,admin_id=id)


# admin validated post api

@app.route("/admin/<int:id>/validate",methods=['POST'])
def validate_post(id):
    cur = mysql.connection.cursor()
    post_id = request.form.get('post_id')
    decision = request.form.get('decision')
    print()
    cur.execute("select * from posts where post_id=%s",(post_id,))
    row = cur.fetchone()

    cur.execute("UPDATE posts SET post_status = %s, admin_id = %s WHERE post_id = %s", (decision, id, post_id))
    if decision == "delete":
        user_id = row[2]
        post_score = row[4]
        cur.execute("select user_score from users where user_id = %s",(user_id,))
        user_row = cur.fetchone()
        user_score = user_row[0]
        modified_score = violation.change_score(post_score , "delete" , user_score)
        cur.execute("update users set user_score = %s where user_id = %s",(modified_score,user_id))
    mysql.connection.commit()
    return redirect(url_for('display_pending',id=id))

# get all posts api

@app.route("/posts",methods=['GET'])
def viewallposts():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT u.username,p.post_content FROM users u JOIN posts p ON u.user_id = p.poster_id WHERE p.post_status NOT IN (%s, %s, %s)",
        ("admin", "delete", "deleted")
    )
    rows = cur.fetchall()
    post_columns = [ desc[0] for desc in cur.description ]
    post_data = [ dict(zip(post_columns,row)) for row in rows]
    new_columns = [ 'username' , 'post_content']
    return render_template('getallposts.html',posts=post_data,post_columns = new_columns)


'''
@app.route("/user/<int:id>/update_user", methods=["GET", "PUT", "POST"])
def update_user(id):
    if request.method == "GET":
        return render_template('update_user1.html', user_id=id)
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username=%s, email_id=%s, user_password=%s WHERE user_id=%s", (name, email, hashed_password, id))
        mysql.connection.commit()
        if cur.rowcount == 0:
            return render_template('update_user1.html',user_id = id ,message='Failed to Update the details')
        
        return render_template('login.html',user_id = id ,message='User details updated succesfully')
'''

'''
@app.route("/user/<int:id>/update_user", methods=["GET", "PUT", "POST"])
def update_user(id):
    if request.method == "GET":
        return render_template('update_user.html', user_id=id)
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM users WHERE email_id=%s", (email,))
        existing = cur.fetchone()
        if existing:
            return render_template('update_user1.html', user_id=id, message="Email already in use by another account")
        cur.execute("UPDATE users SET username=%s, email_id=%s, user_password=%s WHERE user_id=%s", (name, email, hashed_password, id))
        mysql.connection.commit()
        if cur.rowcount == 0:
            return render_template('update_user1.html',user_id = id ,message='Failed to Update the details')
        
        return render_template('login.html',user_id = id ,message='User details updated succesfully')
'''
    
@app.route("/user/logout")
def logout():
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)