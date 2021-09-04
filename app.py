from datetime import datetime
from flask import Flask,render_template,request,session,redirect,jsonify,flash
from flask.helpers import url_for
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

# Database connection
mydb = mysql.connector.connect(host="localhost",user="root",password="",database="vastu")
cursor = mydb.cursor()

# home page
@app.route("/")
def home():
    # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try : 
        current_user_id = int(session.get('user_id'))
        cursor.execute("SELECT users.college,products.*,users.name FROM users \
            JOIN products ON users.users_id = products.users_id WHERE NOT users.users_id=%s ORDER BY products.date DESC",(current_user_id,))
        result = cursor.fetchall()
        return render_template("index.html",session_user_name=session.get('user_name'),result=result)
    except Exception as e:
        return (str(e))

# profile page
@app.route("/profile")
def profile():
    # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try:
        # fetch user profile information
        cursor.execute("SELECT * FROM users where users_id = %s ",(session.get('user_id'),))
        result = cursor.fetchall()
        user_name = result[0][1]
        user_email = result[0][2]
        user_college = result[0][4]
        # Formatting the date
        user_joined_date = datetime.date(result[0][5])
        user_joined_date = str(user_joined_date.day)+ " "+ str(user_joined_date.strftime("%B"))+", "+str(user_joined_date.year)
        user_picture = result[0][6]
        return render_template("profile.html",
            session_user_name=session.get('user_name'),
            user_name=user_name,
            user_email=user_email,
            user_college=user_college,
            user_picture=user_picture,
            user_joined_date=user_joined_date)
    except Exception as e:
        return (str(e))

# upload image on profile
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/profileimage",methods=['POST'])
def profile_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        try:
            current_user_id = int(session.get('user_id'))
            filename = secure_filename(str(datetime.now())+" "+file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("UPDATE users SET picture=%s WHERE users_id=%s",(filename,current_user_id))
            mydb.commit()
            return redirect('/profile')
        except Exception as e:
            return str(e)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

# category page
@app.route("/category")
def category():
     # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("category.html",session_user_name=session.get('user_name'))

# show category page
@app.route("/showcategory/<cat>")
def show_category(cat):
    # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try:
        current_user_id = int(session.get('user_id'))
        cursor.execute("SELECT users.college,products.*,users.name FROM users \
            JOIN products ON users.users_id = products.users_id WHERE NOT users.users_id=%s \
                AND products.p_category=%s",(current_user_id,cat))
        result = cursor.fetchall()
        if cat=="sportandhobbies":
            cat = "Sport and Hobbies"
        elif cat=="computerandelectronics":
            cat = "Computer and Electronics"
        return render_template("showcategory.html",session_user_name=session.get('user_name'),category=cat.capitalize(),result=result)
    except Exception as e:
        return (str(e))

# myads page
@app.route("/myads")
def my_ads():
    # if the user is logged in
    if 'user_id' not in session:
            return redirect('/login')
    try:
        current_user_id = int(session.get('user_id'))
        cursor.execute("SELECT users.college,products.* FROM users \
                        JOIN products ON users.users_id = products.users_id \
                        WHERE users.users_id=%s ORDER BY products.date DESC",(current_user_id,))
        result = cursor.fetchall()
        return render_template("myads.html",session_user_name=session.get('user_name'),result=result)
    except Exception as e:
        return (str(e))

# delete post endpoints
@app.route("/deletemyads/<int:p_id>")
def delete_my_ads(p_id):
    # if the user is logged in
    if 'user_id' not in session:
            return redirect('/login')
    try:
        current_user_id = int(session.get('user_id'))
        cursor.execute("DELETE FROM products WHERE p_id=%s AND users_id=%s",(p_id,current_user_id))
        mydb.commit()
        return redirect("/myads")
    except Exception as e:
        return str(e)

# View products
@app.route("/view/<int:p_id>")
def view(p_id):
    # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try:
        cursor.execute("SELECT users.name,users.college,products.* FROM users \
                        JOIN products ON users.users_id = products.users_id \
                        WHERE products.p_id = %s",(p_id,))
        result = cursor.fetchall()
        current_user_id = int(session.get('user_id'))
        return render_template("view.html",session_user_name=session.get('user_name'),result=result,current_user_id=current_user_id)      
    except Exception as e:
        return (str(e))

        
# sell
@app.route('/sell')
def sell():
    # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('sell.html',session_user_name=session.get('user_name'))
    

# product submit page
@app.route('/postsubmit',methods=['POST'])
def post_submit():
    # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try :
        current_user_id = int(session.get('user_id'))
        if request.method=='POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No image selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                name = request.form.get('p_name')
                title = request.form.get('p_title')
                description = request.form.get('p_description')
                price = int(request.form.get('p_price'))
                category = request.form.get('p_category')
                pType = request.form.get('p_type')
                now = datetime.now()
                filename = secure_filename(str(datetime.now())+" "+file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute("INSERT INTO products(users_id,p_name,p_title,p_description,p_price,p_category,date,p_type,p_picture) \
                                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(current_user_id,name,title,description,price,category,now,pType,filename))
                mydb.commit()
                return redirect('/myads')
            else:
                flash('Allowed image types are - png, jpg, jpeg, gif')
                return redirect(request.url)
        return render_template('sell.html',session_user_name=session.get('user_name'))
    except Exception as e:
        return (str(e))

# chat page
@app.route("/chat")
def chat():
     # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try:
        current_user_id = int(session.get('user_id'))
        # name , users_id , chat_id , p_id , last_message , p_name
        cursor.execute("SELECT users.name,users.users_id,chat.chat_id,chat.p_id, chat.last_message,products.p_name,users.picture,products.p_picture FROM users \
                    JOIN chat ON users.users_id = chat.sender_id OR users.users_id = chat.receiver_id \
                    JOIN products ON products.p_id = chat.p_id\
                    WHERE chat.sender_id = %s OR chat.receiver_id = %s ORDER BY chat.date DESC",(current_user_id,current_user_id))
        result = cursor.fetchall()
        res = []
        # removing the data of current user
        for x in result:
            if x[1]!=current_user_id:
                res.append(x)
        return render_template("chat.html",session_user_name=session.get('user_name'),result=res)
    except Exception as e:
        return (str(e))

# offer post page
@app.route('/offer',methods=['POST'])
def offer():
     # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try:
        current_user_id = int(session.get('user_id'))
        if request.method =="POST":
            p_id = int(request.form.get("p_id"))
            message = request.form.get("message")
            receiver_id = int(request.form.get("receiver_id"))
            cursor.execute("SELECT chat_id FROM chat WHERE ((sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s)) \
                            AND  p_id=%s",(current_user_id,receiver_id,receiver_id,current_user_id,p_id))
            result = cursor.fetchall()
            if len(result)==0:
                cursor.execute("INSERT INTO chat(p_id,sender_id,receiver_id,last_message,date) VALUES(%s,%s,%s,%s,%s)",
                                (p_id,current_user_id,receiver_id,message,datetime.now()))
                last_id = cursor.lastrowid
                mydb.commit()
                cursor.execute("INSERT INTO message(chat_id,m_body,m_from,date) VALUES(%s,%s,%s,%s)",(last_id,message,current_user_id,datetime.now()))
                mydb.commit()
                return redirect('/chat')
            res = str(result[0][0])
            cursor.execute("INSERT INTO message(chat_id,m_body,m_from,date) VALUES(%s,%s,%s,%s)",(int(res),message,current_user_id,datetime.now()))
            mydb.commit()
            cursor.execute("UPDATE chat SET last_message=%s,date=%s WHERE chat_id=%s",(message,datetime.now(),int(res)))
            mydb.commit()
            return redirect("/showchat/"+res)
    except Exception as e:
        return (str(e))

# Showcase of specific chat page
@app.route('/showchat/<int:chat_id>')
def show_chat(chat_id):
     # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    current_user_id = int(session.get('user_id'))
    try:
        cursor.execute("SELECT users.users_id,users.name,users.college,products.p_name,products.p_picture,users.picture FROM users \
                        JOIN chat ON users.users_id = chat.sender_id OR users.users_id = chat.receiver_id \
                        JOIN products ON chat.p_id = products.p_id \
                        WHERE chat.chat_id = %s",(chat_id,))
        result = cursor.fetchall()
        res = []
        # removing the data of current user
        for x in result:
            if x[0]!=current_user_id:
                res.append(x)
        print(res)
        return render_template("showchat.html",session_user_name=session.get('user_name'),chat_id=chat_id,current_user_id=current_user_id,result=res)
    except Exception as e:
        return (str(e))

# Fetching message page
@app.route('/fetchMessage',methods=['POST'])
def fetch_message():
     # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try:
        chat_id = int(request.form.get('chat_id'))
        cursor.execute("SELECT m_body,m_from,date FROM message WHERE chat_id=%s ORDER BY date ASC",(chat_id,))
        result = cursor.fetchall()
        return jsonify({'result' :  result})
    except Exception as e:
        return (str(e))

# send messgae post page
@app.route('/sendMessage',methods=['POST'])
def send_message():
     # if the user is logged in
    if 'user_id' not in session:
        return redirect('/login')
    try :
        message = request.form.get('message')
        chat_id = request.form.get('chat_id')
        current_user_id = int(session.get('user_id'))
        cursor.execute("INSERT INTO message(chat_id,m_body,m_from,date) VALUES(%s,%s,%s,%s)",(chat_id,message,current_user_id,datetime.now()))
        mydb.commit()
        cursor.execute("UPDATE chat SET last_message=%s,date=%s WHERE chat_id=%s",(message,datetime.now(),chat_id))
        mydb.commit()
        return jsonify({'message': "done"})
    except Exception as e:
        return (str(e))

# login page
@app.route("/login",methods=['GET','POST'])
def login():
    # if the user is already logged in 
    if 'user_id' in session:
        return redirect('/')
    try:
        if request.method=='POST':
            email = request.form.get('email')
            password = request.form.get('password')
            cursor.execute('''SELECT * FROM users where email=%s and password=%s LIMIT 1''',(email,password))
            users = cursor.fetchall()
            if len(users)>0:
                session['user_id'] = users[0][0]
                session['user_name'] = users[0][1]
                return redirect('/')
            else :
                return redirect(url_for('login',q="email or password not found"))
        return render_template('login.html',message=request.args.get("q", ""))
    except Exception as e:
        return (str(e))

@app.route("/logout")
def logout():
    session.pop('user_id',default=None)
    session.pop('user_name',default=None)
    return redirect('/login')

@app.route("/register",methods=['GET','POST'])
def register():
    # if the user is already logged in 
    if 'user_id' in session:
        return redirect('/')
    try:
        if request.method=='POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            college = request.form.get('college')
            now = datetime.now()
            cursor.execute("SELECT email FROM users where email = %s ",(email,))
            myresult = cursor.fetchall()
            if len(myresult)==0:
                cursor.execute(''' INSERT INTO users(name,email,password,college,date) VALUES(%s,%s,%s,%s,%s) ''',(name,email,password,college,now))
                mydb.commit()
                cursor.execute("SELECT * FROM users where email = %s ",(email,))
                myresult = cursor.fetchall()
                session['user_id'] = myresult[0][0]
                session['user_name'] = myresult[0][1]

                return redirect('/')
            else : 
                return redirect(url_for('register',q="email already registered"))
        return render_template('register.html',message=request.args.get("q", ""))
    except Exception as e:
        return (str(e))

if __name__=="__main__":
    app.run(host='localhost', debug=True)