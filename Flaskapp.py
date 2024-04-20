from flask import Flask,render_template,url_for,request,session,redirect
from datetime import timedelta
import mssqlconn
import random
import re


app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.permanent_session_lifetime= timedelta(hours=1)


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/",methods=['POST','GET'])
def getval():
    global username,accid
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        session.permanent=True
        username = request.form['username']
        password = request.form['password']
        account=mssqlconn.mysqlcheck(username,password)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            accid = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg, username=username)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))

@app.route("/register", methods=['POST','GET'])#to be completed
def register():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            account=mssqlconn.mysqlacccheck(username)
            if account:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
                mssqlconn.mysqlregister(username, password, email)
                msg = 'You have successfully registered !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template('register.html', msg=msg)

@app.route('/main')
def main():
        medicine_history=mssqlconn.mysqlretrieve(session['id'])
        return render_template("orderslist.html",username=session['username'],medicine_history=medicine_history)

@app.route('/product_list')
def product_list():
    medicine_dict=mssqlconn.mysqlmedlistretrieve()
    return render_template('medlist.html',medicine_dict=medicine_dict)

@app.route('/product_list', methods=['POST','GET'])
def addCart():
    try:
        order_id=random.randint(3260,4260)
        request.form.to_dict(flat=False)
        product_id=request.form.get('button_id')
        product_quantity=request.form.get('button_quantity')
        mname=mssqlconn.mysqlmnameretrieve(product_id)
        if(product_quantity and product_id and request.method=="POST"):
            insert=mssqlconn.mysqlcart(session['id'], product_id[4:8],product_quantity,order_id)
            if(insert):
                return redirect(request.referrer)
        else:
            #print("passing2")
            stock = mssqlconn.mysqlprodstock(product_id)
            return render_template('quantity.html', stock=stock, product_id=product_id,mname=mname[0])
    except Exception as e:
        print(e)

@app.route('/cart')
def cart():
    orders=[]
    order_total=0
    cartdata=mssqlconn.mysqlcartretrieve()
    if cartdata==[]:
        return render_template('emptycart.html')
    username=mssqlconn.mysqlaccnameretrieve(cartdata[0][0])
    for i in range(len(cartdata)):
        mname = mssqlconn.mysqlmnameretrieve(cartdata[i][1])
        medicine_price=mssqlconn.mysqlretrieveprice(cartdata[i][1])
        total_medicine_price=medicine_price[0]*cartdata[i][2]
        order_total+=total_medicine_price
        an_order=dict(order_id=cartdata[i][3],mname=mname[0],order_stock=cartdata[i][2],medicine_price=medicine_price[0],total_medicine_price=total_medicine_price)
        orders.append(an_order)
        continue
    return render_template('cart.html',username=username[0],orders=orders,order_total=order_total)

@app.route('/removefromcart/<int:order_id>',methods=['POST','GET'])
def removefromcart(order_id):
    orders=[]
    order_total=0
    mssqlconn.mysqldeleteitemfromcart(order_id)
    cartdata=mssqlconn.mysqlcartretrieve()
    if cartdata == []:
        return render_template('emptycart.html')
    username = mssqlconn.mysqlaccnameretrieve(cartdata[0][0])
    for i in range(len(cartdata)):
        mname = mssqlconn.mysqlmnameretrieve(cartdata[i][1])
        medicine_price = mssqlconn.mysqlretrieveprice(cartdata[i][1])
        total_medicine_price = medicine_price[0] * cartdata[i][2]
        order_total += total_medicine_price
        an_order = dict(order_id=cartdata[i][3], mname=mname[0], order_stock=cartdata[i][2],
                        medicine_price=medicine_price[0], total_medicine_price=total_medicine_price)
        orders.append(an_order)
        continue
    return render_template('cart.html', username=username[0], orders=orders, order_total=order_total)

@app.route('/place_order')
def place_order():
    rid=random.randint(9401,9410)
    mssqlconn.mysqladdtohistory()
    order_placed=mssqlconn.mysqlplaceorder(rid)
    if order_placed:
        return redirect(url_for('main'))
if __name__ == "__main__":
    app.run(debug=True)

