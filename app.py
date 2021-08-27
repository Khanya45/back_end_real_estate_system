from flask import Flask, request, jsonify, render_template, url_for, json
from flask_jwt import JWT, jwt_required, current_identity
import hmac, datetime
import sqlite3
from flask import redirect
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from flask_cors import CORS, cross_origin


# MksT6Y2F8TRbC2w

app = Flask(__name__)
app.debug = True
CORS(app, resources={r"/api/*": {"origins": "*"}})


def create_tables():
    # CREATING A DATABASE
    conn = sqlite3.connect('dbFindProperty.db')
    print("Opened database successfully")
    # CREATING TABLES
    conn.execute('CREATE TABLE IF NOT EXISTS tblUser (user_id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, email TEXT, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS tblProperty (property_id INTEGER PRIMARY KEY AUTOINCREMENT, property_type TEXT, description TEXT, price REAL,agent_id INTEGER, listing_type TEXT, address TEXT, image TEXT, user_id INTEGER, date DATETIME, FOREIGN KEY (agent_id) REFERENCES tblAgent (agent_id))')
    conn.execute('CREATE TABLE IF NOT EXISTS tblAgent (agent_id INTEGER PRIMARY KEY AUTOINCREMENT, estate_agent TEXT, location TEXT, image TEXT,fullname TEXT, password TEXT, email TEXT, mobile TEXT)')
    print("Table created successfully")
    conn.close()


# create_tables()
# with sqlite3.connect('dbFindProperty.db') as conn:
#             cur = conn.cursor()
#             cur.execute('DROP TABLE tblAgent ')
#             conn.commit()


# VALIDATION FOR STRINGS
def is_string(*args):
    for arg in args:
        if arg.isdigit() == False:
            flag = True
        else:
            flag = False
    return flag


# VALIDATION FOR INTEGERS
def is_number(*args):
    for arg in args:
        if arg.isdigit() == True:
            flag = True
        else:
            flag = False
    return flag


# VALIDATION FOR LENGTH OF MOBILE
def length(*args):
    for arg in args:
        if len(arg) > 0:
            flag = True
        else:
            flag = False
    return flag


# create_tables()


#  ================================================= FUNCTIONS FOR USER, AGENT AND PROPERTY REGISTRATION =============================================
class clsUser:
    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        self.password = password


    def user_registration(self):

            with sqlite3.connect("dbFindProperty.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tblUser("
                               "fullname,"
                               "email,"
                               "password) VALUES(?, ?, ?)", (self.fullname, self.email, self.password))
                conn.commit()


@app.route('/user-registration/', methods=["POST"])
@cross_origin()
def user_register():
    response = {}
    if request.method == "POST":
        fullname = request.json['fullname']
        email = request.json['email']
        password = request.json['password']
        if is_string(fullname) == True and length(fullname, email, password) == True:

            objUser = clsUser(fullname, email, password)
            objUser.user_registration()
            response["message"] = "success"
            response["status_code"] = 201
        else:
            response["message"] = "Unsuccessful. Incorrect credentials"
            response["status_code"] = 400
        return response


class clsAgent:
    def __init__(self, fullname, password, email, estate_agent, location, image, mobile):
        self.fullname = fullname
        self.password = password
        self.email = email
        self.estate_agent = estate_agent
        self.location = location
        self.image = image
        self.mobile = mobile


    def agent_registration(self):

        with sqlite3.connect("dbFindProperty.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tblAgent("
                           "fullname,"
                           "password,"
                           "email,"
                           "estate_agent,"
                           "location,"
                           "image,"
                           "mobile) VALUES(?,?,?,?,?,?,?)", (self.fullname, self.password, self.email, self.estate_agent, self.location, self.image, self.mobile))
            conn.commit()


# ADDING THE NEW AGENTS ON THE TABLE
@app.route('/agent-registration/', methods=["POST"])
@cross_origin()
# @jwt_required()
def agent_registration():
    response = {}
    if request.method == "POST":
        fullname = request.json['fullname']
        password = request.json['password']
        email = request.json['email']
        estate_agent = request.json['estate_agent']
        location = request.json['location']
        mobile = request.json['mobile']
        image = request.json['image']
        if is_string(fullname) == True or length(fullname, password, email, estate_agent, location, mobile, image) == True:
            objAgent = clsAgent(fullname, password, email, estate_agent, location, image, mobile)
            objAgent.agent_registration()
            response["message"] = "agent successfully added"
            response["status_code"] = 201
        else:
            response['message'] = "Invalid characters"
            response['status_code'] = 400

        return response


class clsProperty:
    def __init__(self, property_type, description, price, listing_type, address, image):
        self.property_type = property_type
        self.description = description
        self.price = price
        self.image = image
        self.listing_type = listing_type
        self.address = address


    def add_property(self):
            with sqlite3.connect('dbFindProperty.db') as conn:
                cur = conn.cursor()
                cur.execute('SELECT DATE()')
                date = cur.fetchone()
                cur.execute('INSERT INTO tblProperty ( date, property_type, description, price, listing_type, address, image) VALUES(?,?,?,?,?,?,?)', (date, self.property_type, self.description, self.price, self.listing_type, self.address, self.image))
                conn.commit()


# ADDING PROPERTY ON THE TABLE
@app.route('/add_property/', methods=["POST"])
@cross_origin()
# @jwt_required()
def add_property():
    response = {}

    if request.method == 'POST':
        property_type = request.json['property_type']
        description = request.json['description']
        price = request.json['price']
        image = request.json['image']
        listing_type = request.json['listing_type']
        address = request.json['address']
        if is_string(property_type) == True or length(property_type, description, listing_type, address, image) == True or is_number(price):
            objProperty = clsProperty(property_type, description, price, listing_type, address, image)
            objProperty.add_property()
            response["status_code"] = 201
            response['description'] = "Book added succesfully"

        else:
            response["message"] = "Unsuccessful. Incorrect credentials"
            response["status_code"] = 400

        return response


# ============================================== ALL FUNCTIONS FOR GETTING ALL ITEMS ======================================

# ============ GET ALL AGENTS ================
@app.route('/get-agents/', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_agents():
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblAgent")
        agents = cursor.fetchall()
    response['status_code'] = 200
    response['data'] = agents
    return response


# =========== GET ALL USERS ===============
@app.route('/get-users/', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_users():
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblUser")
        users = cursor.fetchall()
    response['status_code'] = 200
    response['data'] = users
    return response


# ========= GET ALL PROPERTIES =================
@app.route('/get-properties/', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_properties():
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblProperty")
        properties = cursor.fetchall()
    response['status_code'] = 200
    response['data'] = properties
    return response


#  ==================================== SENDING EMAIL TO THE AGENT ==========================
@app.route('/send-email/<int:agent_id>', methods=['POST'])
@cross_origin()
def send_email(agent_id):
    response = {}
    if request.method == "POST":
        email = request.json['email']
        try:
            with sqlite3.connect("dbFindProperty.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM tblAgent WHERE agent_id=", agent_id)
                agent_email = cursor.fetchone()
            sender_email_id = email
            receiver_email_id = agent_email
            password = "GETRICHWITHLOTTO"
            subject = "I am interested on the property"
            msg = MIMEMultipart()
            msg['From'] = sender_email_id
            msg['To'] = receiver_email_id
            msg['Subject'] = subject
            body = f'I would love to check out the property. Call me when you have time'
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(sender_email_id, password)
            s.sendmail(sender_email_id, receiver_email_id, text)
            s.quit()
            response['message'] = "Successfully sent an email"
        except:
            response['message'] = "Invalid email"
        return response


# =================== FUNCTION FOR GETTING LISTINGS OF  AN AGENT ===================

@app.route('/get-listings/<int:agent_id>/', methods=["GET"])
@cross_origin()
# @jwt_required()
def get_listings(agent_id):
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tblProperty WHERE agent_id =? GROUP BY listing_type', [agent_id])
        listings = cursor.fetchall()
        rental = listings[0][0]
        sale = listings[1][0]
        response["sale_listing"] = sale
        response["rental_listing"] = rental
    return response


# ================================== FUNCTION FOR GETTING LIST OF PROPERTIES BY AGENT_ID AND USER_ID =============================

@app.route('/property-by-agent/<int:agent_id>/')
@cross_origin()
def filter_by_agent(agent_id):
    response = {}

    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblProperty WHERE agent_id=?", agent_id)
        response["data"] = cursor.fetchall()
    return response


@app.route('/property-by-user/<int:user_id>/')
@cross_origin()
def filter_by_user(user_id):
    response = {}

    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblProperty WHERE agent_id=?", user_id)
        response["data"] = cursor.fetchall()
    return response


# ================= FUNCTIONS FOR FILTERING =======================
@app.route('/property-by-suburb/<suburb>/')
@cross_origin()
def filter_by_suburb(suburb):
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblProperty WHERE address LIKE'%"+suburb+"%'")
        response["data"] = cursor.fetchall()
    return response


@app.route('/property-by-listingtype/<type>/')
@cross_origin()
def filter_by_listingtype(type):
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblProperty WHERE listing_type=?", type)
        response["data"] = cursor.fetchall()
    return response


@app.route('/property-by-type/<type>/')
@cross_origin()
def filter_by_type(type):
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tblProperty WHERE property_type=?", type)
        response["data"] = cursor.fetchall()
    return response

# ========================================== FUNCTIONS FOR UPDATING AGENT, USER AND PROPERTY ============================================================


# =========== UPDATING USER =============
@app.route('/edit-user/<id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def edit_user(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('dbFindProperty.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}
            # ===================== UPDATING FULLNAME =================================
            if incoming_data.get("fullname") is not None:
                put_data["fullname"] = incoming_data.get("fullname")
                if is_number(put_data["fullname"]) == False:
                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblUser SET fullname =? WHERE user_id=?", (put_data["fullname"], id))
                        conn.commit()
                        response['message'] = "successful"
                        response['status_code'] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING EMAIL =================================
            if incoming_data.get("email") is not None:
                put_data['email'] = incoming_data.get('email')
                if is_string(put_data["email"]) == True or length(put_data["email"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblUser SET email =? WHERE user_id=?", (put_data["email"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING PASSWORD =================================
            if incoming_data.get("password") is not None:
                put_data['password'] = incoming_data.get('password')
                if length(put_data["password"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblUser SET password =? WHERE user_id=?", (put_data["password"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400

    return response


# ======================================= UPDATING AGENT =============================================== ======
@app.route('/edit-agent/<id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def edit_agent(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('dbFindProperty.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}
            # ===================== UPDATING FULLNAME =================================
            if incoming_data.get("fullname") is not None:
                put_data["fullname"] = incoming_data.get("fullname")
                if is_number(put_data["fullname"]) == False:
                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblUser SET fullname =? WHERE agent_id=?", (put_data["fullname"], id))
                        conn.commit()
                        response['message'] = "successful"
                        response['status_code'] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING EMAIL =================================
            if incoming_data.get("email") is not None:
                put_data['email'] = incoming_data.get('email')
                if is_string(put_data["email"]) == True or length(put_data["email"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblUser SET email =? WHERE agent_id=?", (put_data["email"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING PASSWORD =================================
            if incoming_data.get("password") is not None:
                put_data['password'] = incoming_data.get('password')
                if length(put_data["password"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblUser SET password =? WHERE agent_id=?", (put_data["password"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            #  ===================== UPDATING ESTATE AGENT ==========================
            if incoming_data.get("estate_agent") is not None:
                put_data["estate_agent"] = incoming_data.get("estate_agent")
                if is_number(put_data["estate_agent"]) == False:
                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblAgent SET estate_agent =? WHERE agent_id=?", (put_data["estate_agent"], id))
                        conn.commit()
                        response['message'] = "successful"
                        response['status_code'] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING MOBILE =================================
            if incoming_data.get("mobile") is not None:
                put_data['mobile'] = incoming_data.get('mobile')
                if is_string(put_data["mobile"]) == True or length(put_data["mobile"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblAgent SET mobile =? WHERE agent_id=?", (put_data["mobile"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING LOCATION =================================
            if incoming_data.get("location") is not None:
                put_data['location'] = incoming_data.get('location')
                if length(put_data["location"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblAgent SET location =? WHERE agent_id=?", (put_data["location"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING IMAGE =================================
            if incoming_data.get("image") is not None:
                put_data['image'] = incoming_data.get('image')
                if length(put_data["image"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblAgent SET image =? WHERE agent_id=?", (put_data["image"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400

    return response


# ======================================= UPDATING PROPERTY =====================================================
@app.route('/edit-agent/<id>/', methods=["PUT"])
@cross_origin()
# @jwt_required()
def edit_property(id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('dbFindProperty.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}
            # ===================== UPDATING FULLNAME =================================
            if incoming_data.get("property_type") is not None:
                put_data["property_type"] = incoming_data.get("property_type")
                if is_number(put_data["property_type"]) == False:
                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblProperty SET property_type =? WHERE property_id=?", (put_data["property_type"], id))
                        conn.commit()
                        response['message'] = "successful"
                        response['status_code'] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING EMAIL =================================
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')
                if is_string(put_data["price"]) == True or length(put_data["price"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblProperty SET price =? WHERE property_id=?", (put_data["price"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING PASSWORD =================================
            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')
                if length(put_data["description"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblProperty SET description =? WHERE property_id=?", (put_data["description"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            #  ===================== UPDATING ESTATE AGENT ==========================
            if incoming_data.get("listing_type") is not None:
                put_data["listing_type"] = incoming_data.get("listing_type")
                if is_number(put_data["listing_type"]) == False:
                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblProperty SET listing_type =? WHERE property_id=?", (put_data["listing_type"], id))
                        conn.commit()
                        response['message'] = "successful"
                        response['status_code'] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING LOCATION =================================
            if incoming_data.get("address") is not None:
                put_data['address'] = incoming_data.get('address')
                if length(put_data["address"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblProperty SET address =? WHERE property_id=?", (put_data["address"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400
            # ===================== UPDATING IMAGE =================================
            if incoming_data.get("image") is not None:
                put_data['image'] = incoming_data.get('image')
                if length(put_data["image"]) == True:

                    with sqlite3.connect('dbFindProperty.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE tblProperty SET image =? WHERE property_id=?", (put_data["image"], id))
                        conn.commit()

                        response["content"] = "successful"
                        response["status_code"] = 200
                else:
                    response['message'] = "Invalid characters"
                    response['status_code'] = 400

    return response


# ====================================== FUNCTIONS FOR DELETING AGENT,USER OR PROPERTY =====================================

# DELETE USER
@app.route("/delete-user/<id>/")
@cross_origin()
# @jwt_required()
def delete_user(id):
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tblUser WHERE user_id=?", id)
        conn.commit()
        response['status_code'] = 200
        response['message'] = "blog post deleted successfully."
    return response


# DELETE AGENT
@app.route("/delete-agent/<id>/")
@cross_origin()
# @jwt_required()
def delete_agent(id):
    response = {}
    with sqlite3.connect("dbFindProperty.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tblAgent WHERE agent_id=?", id)
        conn.commit()
        response['status_code'] = 200
        response['message'] = "blog post deleted successfully."
    return response


# # DELETE PROPERTY
# @app.route("/delete-property/<id>/")
# @cross_origin()
# # @jwt_required()
# def delete_property(id):
#     response = {}
#     with sqlite3.connect("dbFindProperty.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM tblProperty WHERE property_id=?", id)
#         conn.commit()
#         response['status_code'] = 200
#         response['message'] = "blog post deleted successfully."
#     return response


@app.route("/delete-property/<id>/")
@cross_origin()
# @jwt_required()
def delete_property(id):
    with sqlite3.connect('dbFindProperty.db') as conn:
                cur = conn.cursor()
                cur.execute('UPDATE tblProperty SET agent_id = 1 WHERE property_id=3')
                conn.commit()


# description = f'Very Neat 3 bedroom house to rent close to Beaumont Primary School in Morningside Somerset West.\
#               This tiled family home offers a spacious lounge with fire place, open plan dining area and newly  \
#               renovated kitchen, 3 bedrooms, 2 with build in cupboards, 2 bathrooms, full family bathroom with  \
#               separate toilet and main en-suite. Double garage and outside toilet, enclosed garden and is pet friendly \
#               to maximum of 2 dogs or 2 cats. Walking distance from Beaumont Primary School and Radloff Park Sports Grounds.'
#
# with sqlite3.connect('dbFindProperty.db') as conn:
#             cur = conn.cursor()
#             cur.execute('SELECT DATE()')
#             dates = cur.fetchone()
#             for i in dates :
#                 date = i
#             cur.execute('INSERT INTO tblProperty (property_type,'
#                         ' description,'
#                         ' price, '
#                         'listing_type,'
#                         ' address, '
#                         'image,'
#                         'date) VALUES(?,?,?,?,?,?,?)', ("house", description, 15000, "rental", "Morningside", "https://prppublicstore.blob.core.windows.net/live-za-images/property/1469/36/4973469/images/property-4973469-22447277_sd.jpg", date))
#             conn.commit()


# with sqlite3.connect('dbFindProperty.db') as conn:
#             cur = conn.cursor()
#             cur.execute('SELECT DATE()')
#             date = cur.fetchone()
#             print(date)

# with sqlite3.connect('dbFindProperty.db') as conn:
#             cur = conn.cursor()
#             cur.execute('UPDATE tblProperty SET agent_id = 1 WHERE property_id=3')
#             conn.commit()

# with sqlite3.connect('dbFindProperty.db') as conn:
#             cur = conn.cursor()
#             cur.execute('SELECT COUNT(*) FROM tblProperty WHERE agent_id = 1 GROUP BY listing_type')
#             listings = cur.fetchall()
#             rental = listings[0][0]
#             sale = listings[1][0]
#

#
# with sqlite3.connect("dbFindProperty.db") as conn:
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM tblProperty WHERE property_id=4")
#     conn.commit()

# response = {}
# suburb = "Morningside"
# with sqlite3.connect("dbFindProperty.db") as conn:
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM tblProperty WHERE address LIKE'%"+suburb+"%'")
#     response["data"] = cursor.fetchall()
# print(response)
