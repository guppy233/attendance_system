import mysql.connector
from datetime import datetime

# 数据库连接
db = mysql.connector.connect(
    host="localhost",
    user="user02",
    password="123457",
    database="attendance"
)

cursor = db.cursor()


# 验证用户
def authenticate(username, password):
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    return cursor.fetchone()

# 验证root用户
def authenticate_root(username, password):
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND is_root = TRUE", (username, password))
    return cursor.fetchone()

# 用户签到
def sign_in(username):
    now = datetime.now()
    late = (now.hour > 8 and now.hour < 14) or (now.hour == 8 and now.minute > 0) or (now.hour == 14 and now.minute > 0) or (now.hour > 19)
    cursor.execute("INSERT INTO attendance_records (user_id, sign_in_time, is_late) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s)",
                   (username, now, late))
    db.commit()
    if late:
        print("你迟到了。")
    else:
        print("签到成功。")

# 用户签出
def sign_out(username):
    now = datetime.now()
    early = now.hour < 12 or (now.hour > 12 and now.hour < 18) or (now.hour > 18 and now.hour < 21)
    cursor.execute("UPDATE records SET sign_out_time = %s, is_early = %s WHERE user_id = (SELECT id FROM users WHERE username = %s) AND sign_out_time IS NULL",
                   (now, early, username))
    db.commit()
    if early:
        print("你早退了。")
    else:
        print("签出成功。")

# 缺勤信息查询
def check_records(username):
    cursor.execute("SELECT sign_in_time, sign_out_time, is_late, is_early FROM records WHERE user_id = (SELECT id FROM users WHERE username = %s)",
                   (username,))
    records = cursor.fetchall()
    for record in records:
        print(f"签到时间: {record[0]}, 签出时间: {record[1]}, 迟到: {'是' if record[2] else '否'}, 早退: {'是' if record[3] else '否'}")

# 用户添加
def add_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone() is not None:
        return False
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    return True

# 用户删除
def delete_user(username):
    cursor.execute("DELETE FROM records WHERE user_id = (SELECT id FROM users WHERE username = %s)", (username,))
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    db.commit()
    print("用户删除成功。")

# 从文件读取界面
def read_menu(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 主程序界面
def main():
    main_menu = read_menu("menu.txt").split('———————————————————————————————')[0]
    maintenance_menu = read_menu("menu.txt").split('———————————————————————————————')[1]

    while True:
        print(main_menu)
        choice = input("请选择功能: ")

        if choice == '1':
            username = input("用户名: ")
            password = input("密码: ")
            user = authenticate(username, password)
            if user:
                sign_in(username)
            else:
                print("用户名或密码错误。")

        elif choice == '2':
            username = input("用户名: ")
            password = input("密码: ")
            user = authenticate(username, password)
            if user:
                sign_out(username)
            else:
                print("用户名或密码错误。")

        elif choice == '3':
            username = input("用户名: ")
            password = input("密码: ")
            user = authenticate(username, password)
            if user:
                check_records(username)
            else:
                print("用户名或密码错误。")

        elif choice == '4':
            root_username = input("请输入root用户名: ")
            root_password = input("请输入root密码: ")
            root_user = authenticate_root(root_username, root_password)
            if root_user:
                while True:
                    print(maintenance_menu)
                    sub_choice = input("请选择功能: ")

                    if sub_choice == '1':
                        while True:
                            username = input("新用户名: ")
                            password = input("新密码: ")
                            if add_user(username, password):
                                print("用户添加成功。")
                                break
                            else:
                                print("用户已存在，请重新输入。")

                    elif sub_choice == '2':
                        username = input("要删除的用户名: ")
                        delete_user(username)

                    elif sub_choice == '4':
                        break

                    elif sub_choice == '3':
                        sub_sub_choice = input("请选择功能: 1. 查看某个用户 2. 显示全部用户: ")
                        if sub_sub_choice == '1':
                            username = input("输入用户名: ")
                            check_records(username)
                        elif sub_sub_choice == '2':
                            cursor.execute("SELECT username FROM users WHERE is_root = FALSE")
                            users = cursor.fetchall()
                            for user in users:
                                print(f"用户名: {user[0]}")
                                check_records(user[0])
                        else:
                            print("无效选择，请重新选择。")

                    else:
                        print("无效选择，请重新选择。")
            else:
                print("root用户名或密码错误。")

        elif choice == '5':
            break

        else:
            print("无效选择，请重新选择。")

if __name__ == "__main__":
    main()
