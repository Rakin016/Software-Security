from flask import Flask, render_template, request, redirect, url_for, session, flash, json
import pymongo
from mongosanitizer.sanitizer import sanitize
#from pymongo import ReturnDocument
import certifi
from datetime import timedelta
from werkzeug.exceptions import HTTPException
import os
import bcrypt
from bson.objectid import ObjectId

ca = certifi.where()
from urllib.parse import quote_plus

# Replace 'username' and 'password' with your actual MongoDB username and password
username = 'rakin016'
password = 'r@kin016'

escaped_username = quote_plus(username)
escaped_password = quote_plus(password)

# Now use escaped_username and escaped_password in your MongoDB URI
uri = f"mongodb+srv://{escaped_username}:{escaped_password}@atlascluster.zydvgbs.mongodb.net/?retryWrites=true&w=majority"
#with open(r'C:\Users\mdrak\Downloads\SS_Project\Project_1\venv\pystring.txt') as f:
    #lines = f.readlines()
#uri = f'mongodb+srv://rakin016:r@kin016@atlascluster.zydvgbs.mongodb.net/?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri, tlsCAFile=ca, )
mydb = client["Buyer_Seller_db"]
mycol = mydb["user_details"]

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(30)
app.permanent_session_lifetime = timedelta(minutes=5)


@app.route("/")
def home():
    return render_template("reg.html")


@app.route("/reg", methods=["POST", "GET"])
def reg():
    if request.method == 'POST':
        s_radio = request.form["s_radio"]
        s_radio = str(s_radio)
        ss_fname = request.form["fname"]
        ss_fname = str(ss_fname)
        ss_lname = request.form["lname"]
        ss_lname = str(ss_lname)
        ss_email = request.form["email"]
        ss_email = str(ss_email)
        ss_pword = request.form["password"]
        ss_pword = str(ss_pword)
        ss_hashed_password = bcrypt.hashpw(ss_pword.encode('utf-8'), bcrypt.gensalt())
        if s_radio != " " and ss_email != " " and ss_fname != " " and ss_lname != " " and ss_hashed_password != " ":
            reg_query = {
                'r_type': s_radio,
                'email': ss_email,
                'firstname': ss_fname,
                'lastname': ss_lname,
                'password': ss_hashed_password
            }
            sanitize(reg_query)
            try:
                mycol.insert_one(reg_query)
                return redirect(url_for("login"))
            except Exception as error:
                #print(error)
                flash("Fields cannot be empty", "info")
                assert error not in reg_query
                return render_template("reg.html")

        else:
            flash("Fields cannot be empty", "info")
            return render_template("reg.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        s_radio = request.form["s_radio"]
        s_radio = str(s_radio)
        s_email = request.form["email"]
        s_email = str(s_email)
        s_pword = request.form["password"].encode('utf-8')
        #s_pword = str(s_pword)
        session["email"] = s_email
        #session["rtype"] = s_radio
        se_query = {'r_type': s_radio,
                    'email': s_email}
        sanitize(se_query)
        user_doc = mycol.find_one(se_query)
        if user_doc:
            stored_hash = user_doc['password']
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            if user_doc['r_type'] == "Customer":
                r_fname = user_doc['firstname']
                r_lname = user_doc['lastname']
                session["fname"] = r_fname
                session["lname"] = r_lname
                return redirect(url_for("page2"))
            else:
                return redirect(url_for("page1"))
        else:
            #print(error)
            flash("Enter a valid username", "info")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")


@app.route("/reg1")
def reg1():
    return render_template("reg.html")


col1 = mydb["p_cat"]
col2 = mydb["product_details"]
feed = mydb["feedback"]

@app.route("/page1", methods=["GET", "POST"])
def page1():
    if "email" in session:
        email = session["email"]
        email = str(email)
        s_dict = {"p_name": [], "p_cat": [], "p_quantity": [], "p_price": []}
        count = 0
        try:
           v_query = col1.find({'email': email})
           doc = list(v_query)
           print('main_doc',doc)
           for docs in doc:
               # Access variables within each dictionary
               _id = docs['_id']
               email = docs['email']
               product = docs['product']
               # Do something with the variables, for example, print them
               print(f"ID: {_id}, Email: {email}, Product: {product}")
               dis_query = {'p_name':product}
               found_doc = col2.find_one(dis_query)    
               print(found_doc)
               if found_doc:
                   s_dict['p_name'].append(found_doc['p_name'])
                   s_dict['p_cat'].append(found_doc['p_cat'])
                   s_dict['p_quantity'].append(found_doc['p_quantity'])
                   s_dict['p_price'].append(found_doc['p_price'])
                   count += 1
        except Exception as error:
            #print(error)
            flash("No Assignment", "info")

        #products = [{'p_name': s_dict['p_name'], 'p_cat': s_dict['p_cat'], 'p_quantity': s_dict['p_quantity'], 'p_price': s_dict['p_price']} for s_dict in cursor]
        #return render_template("page1.html", email=email, val=val, **s_dict, count=count)
        return render_template("page1.html", email=email, s_dict = s_dict , count=count)    
    else:
        flash("User Does not Exist", "info")
        return render_template("login.html")


@app.route("/page2", methods=['GET'])
def page2():
    if "fname" in session:
        fname = session["fname"]
        fname = str(fname)
        lname = session["lname"]
        lname = str(lname)
        email = session["email"]
        email = str(email)
        #x_que = {'st_fname': fname, 'st_lname': lname}
        r_que = col2.find()
        r_dict = {"p_name": [], "p_cat": [], "p_origin": [], "p_quantity": [], "p_price": [],"p_id":[]}
        s_count = 0
        for xj in r_que:
            r_dict['p_name'].append(xj['p_name'])
            r_dict['p_cat'].append(xj['p_cat'])
            r_dict['p_origin'].append(xj['p_origin'])
            r_dict['p_quantity'].append(xj['p_quantity'])
            r_dict['p_price'].append(xj['p_price'])
            r_dict['p_id'].append(str(xj['_id']))
            s_count += 1
        print(r_dict)
        f_dict = {"f_feed":[]}
        x_que = {'email':email}
        f_que = feed.find(x_que)
        for fd in f_que:
            f_dict['f_feed'].append(fd['feedback'])
        return render_template("page2.html", feedback=f_dict['f_feed'],fname=fname, lname=lname, **r_dict, count=s_count)
    else:
        flash("User Does not Exist", "info")
        return render_template("login.html")
    
@app.route('/feedback_initial')
def feedback_initial():
    # Ensure the user is logged in before submitting feedback
    if 'email' in session:
        return render_template('feedback.html')
    else:
        flash('You must be logged in to submit feedback.')
        return redirect(url_for('login'))
    
@app.route("/feedback", methods=['POST'])
def feedback():
    if 'email' in session:
        email = session['email']
        email = str(email)
        fname = session["fname"]
        fname = str(fname)
        lname = session["lname"]
        lname = str(lname)
        f_email = request.form['f_email']
        f_email = str(f_email)
        feedback = request.form['feedback']
        email = str(email)
        feedback_document = {
            'email': email,
            'feedback': feedback
        }
        feed.insert_one(feedback_document)
        return redirect(url_for('page2'))
    else:
        flash("User Does not Exist", "info")
        return render_template("login.html")

@app.route('/add_to_cart/<product_id>')
def update_prod(product_id):
    print('product',product_id)
    if 'email' not in session:
        flash("Not permitted","error")
        return render_template("page2.html")
    try:
        object_id = ObjectId(product_id)
        res = col2.find_one({'_id':object_id})
        if res:
            i_quantity = res['p_quantity']
            i_quantity = int(i_quantity)
            f_quantity = (i_quantity - 1)
        res = col2.update_one({'_id': object_id},{'$set': {'p_quantity': f_quantity}})
        if res.modified_count == 0:
            flash("Product not found or quantity update failed.", "error")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("page2"))    
    
@app.route('/update_pass')
def update_pass():
    # Ensure the user is logged in before updating password
    if 'email' in session:
        return render_template('update_pass.html')
    else:
        flash('You must be logged in to change password.')
        return redirect(url_for('login'))
    
@app.route("/update_pass", methods=['POST'])
def update_p():
    if 'email' in session:
        #email = session['email']
        f_email = request.form['f_email']
        f_email = str(f_email)
        old_pass = request.form['old_pass']
        old_pass = str(old_pass)
        #old_pass_hashed_password = bcrypt.hashpw(old_pass.encode('utf-8'), bcrypt.gensalt())
        new_pass = request.form['new_pass']
        new_pass = str(new_pass)
        #new_pass_hashed_password = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
        user_doc = mycol.find_one({'email': f_email})
        if user_doc:
            stored_hash = user_doc['password']
            if old_pass == stored_hash or bcrypt.checkpw(old_pass.encode('utf-8'), stored_hash):
                new_pass = request.form['new_pass']
                new_pass_hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
                # Update the database with the hashed new password
                mycol.update_one({"email": f_email}, {"$set": {"password": new_pass_hashed}})
        
            return render_template("login.html")             
        else:
            print("No user or invalid inputs")
            return render_template("page2.html")

@app.route("/insert", methods=["GET", "POST"])
def insert():
    if 'email' in session and request.method == "POST":
        email = session['email']
        s_fname = request.form["p_name"]
        s_fname = str(s_fname)
        s_lname = request.form["p_cat"]
        s_lname = str(s_lname)
        s_grade = request.form["p_origin"]
        s_grade = str(s_grade)
        s_sub = request.form["p_quantity"]
        s_sub = str(s_sub)
        s_marks = request.form["p_price"]
        s_marks = float(s_marks)
        if s_fname != " " and s_lname != " " and s_grade != " " and s_sub != " " and s_marks != " ":
            i_query = {'p_name': s_fname,
                       'p_cat': s_lname,
                       'p_origin': s_grade,
                       'p_quantity': s_sub,
                       'p_price': s_marks}
            sanitize(i_query)
            try:
                col2.insert_one(i_query)
                col1.insert_one({'email': email,'product':s_fname})
                return redirect(url_for("page1"))
            except Exception as error:
                print(error)
                assert error not in i_query
    else:
        return render_template("insert.html")


@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        s_fname = request.form["p_name"]
        s_fname = str(s_fname)
        s_lname = request.form["p_cat"]
        s_lname = str(s_lname)
        s_grade = request.form["p_quantity"]
        s_grade = int(s_grade)
        s_sub = request.form["p_price"]
        s_sub = str(s_sub)
        fil = {'p_name': s_fname,
               'p_cat': s_lname,
               'p_quantity': s_grade,
               'p_price': s_sub}
        print("Fil")
        newvalues = {"$set": {'p_quantity': s_grade}}
        newvalues = {"$set": {'p_price': s_sub}}
        print(newvalues)
        try:
            col2.update_one(fil, newvalues)
            return redirect(url_for("page1"))
        except Exception as error:
            print(error)
            assert error not in newvalues
    else:
        return render_template("update.html")


@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        s_fname = request.form["p_name"]
        s_fname = str(s_fname)
        s_lname = request.form["p_cat"]
        s_lname = str(s_lname)
        d_query = {'p_name': s_fname,
                   'p_cat': s_lname,}
        sanitize(d_query)
        try:
            col2.find_one_and_delete(d_query)
            return redirect(url_for("page1"))
        except Exception as error:
            print(error)
            assert error not in d_query
    else:
        return render_template("delete.html")


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route("/logout", methods=["GET"])
def logout():
    session.pop('email', None)
    message = 'You were logged out'
    resp = app.make_response(render_template('login.html', message=message))
    resp.set_cookie('s_email', expires=0)
    return resp


if __name__ == "__main__":
    app.run(debug=True, port=5050)
    # 218 lines
