import mysql.connector
connect=mysql.connector.connect(host='localhost',database='medicaldb',user='root',password='root')
cursor=connect.cursor(buffered=True)

def mysqlcheck(username1,password1):
    cursor.execute('SELECT * FROM accounts WHERE username = %s AND pass = %s', (username1, password1,))
    account = cursor.fetchone()
    return account

def mysqlacccheck(username):
    cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
    account=cursor.fetchone()
    return account

def mysqlregister(username,password,email):
    cursor.execute('SELECT ID FROM accounts ORDER BY id DESC LIMIT 1')
    id=cursor.fetchone()
    userid=id[0]
    userid+=1
    cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s, %s)', (userid, username, password, email,))
    cursor.execute('COMMIT')
    return

def mysqlretrieve(id):
    medicine_history={}
    cursor.execute('SELECT * FROM medicine_history WHERE pid = %s', (id,))
    history = cursor.fetchall()
    for row in history:
        cursor.execute('SELECT mname from pharmacy WHERE mid = %s',(row[1],))
        mentity=cursor.fetchone()
        medicine_history[mentity[0]]=row[2]
    return medicine_history

def mysqlmedlistretrieve():
    medicine_dict={}
    cursor.execute('SELECT * FROM pharmacy')
    mlist=cursor.fetchall()
    for row in mlist:
        temp = [row[1], row[2]]
        medicine_dict[row[0]]=temp
    return medicine_dict

def mysqlprodstock(mid):
    cursor.execute('SELECT stock FROM pharmacy where mid = %s',(mid,))
    stock=cursor.fetchone()
    return stock[0]

def mysqlcart(accid,product_id,product_quant,order_id):
    cursor.execute('INSERT INTO med_cart VALUES (%s,%s,%s,%s)', (accid, product_id, product_quant,order_id))
    cursor.execute(('COMMIT'))
    return True

def mysqlcartretrieve():
    cursor.execute('SELECT * FROM med_cart')
    cartdata=cursor.fetchall()
    return cartdata

def mysqlaccnameretrieve(pid):
    cursor.execute('SELECT username from accounts where id = %s',(pid,))
    accname=cursor.fetchone()
    return accname

def mysqlmnameretrieve(mid):
    cursor.execute('SELECT mname from pharmacy where mid = %s', (mid,))
    mname = cursor.fetchone()
    return mname

def mysqlplaceorder(rid):
    cursor.execute('SELECT order_id from med_cart')
    order_id=cursor.fetchall()
    for i in range(0,len(order_id)):
        cursor.execute('INSERT INTO order_delivery VALUES(%s, %s)', (order_id[i][0], rid,))
    cursor.execute('COMMIT')
    emptycart()
    return True

def emptycart():
    cursor.execute('DELETE FROM MED_CART')
    cursor.execute('COMMIT')
    return

def mysqladdtohistory():
    cursor.execute('SELECT * from med_cart')
    contents=cursor.fetchall()
    for order in contents:
        pid=order[0]
        mid=order[1]
        stock=order[2]
        cursor.execute('INSERT into medicine_history values(%s,%s,%s,current_timestamp)',(pid,mid,stock))
    return

def mysqldeleteitemfromcart(order_id):
    cursor.execute('DELETE FROM med_cart WHERE order_id = %s',(order_id,))
    cursor.execute('COMMIT')
    return

def mysqlretrieveprice(medicine_id):
    cursor.execute('SELECT price_per_unit FROM pharmacy WHERE mid = %s',(medicine_id,))
    medicine_price=cursor.fetchone()
    return medicine_price