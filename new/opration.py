from mysql.connector import MySQLConnection, Error
from read_config import read_db_config

def query_login(username, password):
    query = "SELECT * FROM user WHERE username = %s AND password = %s"
    args = (username, password,)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Error as e:
        print('Error:', e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def query_username(username):
    query = "SELECT * FROM user WHERE username = %s"
    args = (username,)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Error as e:
        print('Error:', e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_user(username, password):
    query = "INSERT INTO user(username, password) " \
            "VALUES(%s,%s)"
    args = (username, password)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
        return cursor.lastrowid
    except Error as error:
        print(error)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_user(id):
    query = "DELETE FROM user WHERE id = %s"  # 修复SQL语法错误：FROM不是FORM
    args = (id,)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_picture(url, num, createtime):
    query = "INSERT INTO picture(url, num, createtime) " \
            "VALUES(%s,%s,%s)"
    args = (url, num, createtime)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
        return cursor.lastrowid
    except Error as error:
        print(error)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_pictures(pictures):
    query = "INSERT INTO picture(url, num, createtime) " \
            "VALUES(%s,%s,%s)"
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.executemany(query, pictures)

        conn.commit()
    except Error as e:
        print('Error:', e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_picture(id, url, num, createtime):
    query = "UPDATE picture SET url=%s,num=%s,createtime=%s WHERE id = %s"
    args = (url, num, createtime, id)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_picture(id):
    query = "DELETE FROM picture WHERE id = %s"  # 修复SQL语法错误：FROM不是FORM
    args = (id,)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_defect(ficid, url, cla, prob, location, createtime):
    query = "INSERT INTO defect(ficid, url, cla, prob, location, createtime) " \
            "VALUES(%s,%s,%s,%s,%s,%s)"
    args = (ficid, url, cla, prob, location, createtime)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_defect(id, ficid, url, cla, prob, location, createtime):
    query = "UPDATE defect SET ficid=%s,url=%s,cla=%s,prob=%s,location=%s," \
            "createtime=%s WHERE id = %s"
    args = (ficid, url, cla, prob, location, createtime, id)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_defect(id):
    query = "DELETE FROM defect WHERE id = %s"  # 修复SQL语法错误：FROM不是FORM
    args = (id,)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print(error)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_defects(defects):
    query = "INSERT INTO defect(ficid, url, cla, prob, location, createtime) " \
            "VALUES(%s,%s,%s,%s,%s,%s)"
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.executemany(query, defects)

        conn.commit()
    except Error as e:
        print('Error:', e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def queryAll_picture():
    query = "SELECT * FROM picture"
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Error as e:
        print('数据库查询错误:', e)
        print('注意: 如果您没有配置MySQL数据库，请忽略此错误。程序将继续运行。')
        return []  # 返回空列表，避免程序崩溃
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def queryAll_defect():
    query = "SELECT * FROM defect"
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Error as e:
        print('数据库查询错误:', e)
        print('注意: 如果您没有配置MySQL数据库，请忽略此错误。程序将继续运行。')
        return []  # 返回空列表，避免程序崩溃
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def query_defect(fid):
    query = "SELECT * FROM defect WHERE ficid = %s"
    args = (fid,)
    
    conn = None
    cursor = None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)
        results = cursor.fetchall()
        conn.commit()
        return results
    except Error as e:
        print('数据库查询错误:', e)
        print('注意: 如果您没有配置MySQL数据库，请忽略此错误。程序将继续运行。')
        return []  # 返回空列表，避免程序崩溃
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    # results = queryAll_picture()
    # print(results)
    # for index, value in enumerate(results):
    #     print(index)
    #     print(value)

    # results = query_defect(3)
    # print(results)

    results = query_login("admin", "123")
    if len(results) == 0:
        print("用户名或密码错误")
    else:
        print("登录成功")

    # for row in results:
    #     # print(row)
    #     id = row[0]
    #     name = row[1]
    #     age = row[2]
    #     print('id: ' + str(id) + '  url: ' + name + '  num: ' + str(age))
    #     pass

    # update_picture('1','D:\LanMoDE\detect\lm1.png','25','2023-05-02 14:54:18')

    # x = insert_picture('test', '14', '2021-01-01')
    # print(x)
    # insert_defect('1', 'test', '1-划痕', '0.96', '[299,2324,214,45]', '2021-01-01')
    # defects = [('1', 'test', '1', '0.92', '[299,2324,214,45]', '2021-01-01'),
    #            ('2', 'test', '2', '0.93', '[299,2324,214,45]', '2021-01-01')]
    # insert_defects(defects)


if __name__ == '__main__':
    main()
