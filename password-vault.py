import mysql.connector
import string
import random
from cryptography.fernet import Fernet

def main():
    key = ""

    with open('key.txt', 'r') as file:
        key = file.read()
        
    cipher_suite = Fernet(key)

    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "AdrishMitra@4",
        "database": "password_vault"
    }

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS passwords (
        id INT AUTO_INCREMENT PRIMARY KEY,
        website VARCHAR(255) NOT NULL UNIQUE,
        encrypted_password TEXT NOT NULL
    )
    """
    cursor.execute(create_table_query)
    connection.commit()

    # Check if username and master password exist, if not, take input and store them
    select_master_query = "SELECT COUNT(*) FROM Master"
    cursor.execute(select_master_query)
    count = cursor.fetchone()[0]

    if count == 0:
        print("Please create USER")
        username = input("Enter a username: ")
        master_password = input("Enter a master password: ")
        encrypted_master_password = cipher_suite.encrypt(master_password.encode())

        insert_master_query = "INSERT INTO Master (username, password) VALUES (%s, %s)"
        cursor.execute(insert_master_query, (username, encrypted_master_password))
        connection.commit()
        print("Username and master password stored.")

    def add_password():
        website = input("\nEnter the website: ")
        password = ""
        choice = int(input("1. Enter your password\n2.Generate strong password: "))
        if(choice == 2):
            length = int(input("Enter length (8-16)"))
            if(8<= length <= 16):
                password = generate_strong_password(length=length)
                print(f"Password for {website} generated: {password}")
            else:
                print("Invalid length")
                add_password()
        else:
            password = input("Enter the password: ")
        encrypted_password = cipher_suite.encrypt(password.encode())

        insert_password_query = "INSERT INTO passwords (website, encrypted_password) VALUES (%s, %s) ON DUPLICATE KEY UPDATE encrypted_password = %s"
        cursor.execute(insert_password_query, (website, encrypted_password, encrypted_password))
        connection.commit()
        print("Password added successfully!")

    def view_password():
        website = input("\nEnter the website: ")

        select_password_query = "SELECT encrypted_password FROM passwords WHERE website = %s"
        cursor.execute(select_password_query, (website,))
        row = cursor.fetchone()

        if row:
            stored_password = cipher_suite.decrypt(bytes(row[0], 'utf-8')).decode()
            print(f"Password for {website}: {stored_password}")
        else:
            print(f"No password found for {website}")

    def generate_strong_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    def login():
        entered_username = input("Enter your username: ")
        entered_master_password = input("Enter your master password: ")

        select_master_query = "SELECT password FROM Master WHERE username = %s"
        cursor.execute(select_master_query, (entered_username,))
        row = cursor.fetchone()
        if row:
            stored_master_password = cipher_suite.decrypt(bytes(row[0], 'utf-8')).decode()

            if entered_master_password == stored_master_password:
                print("\nLogin successful!")
                while True:
                    print("\nOptions:")
                    print("1. Add Password")
                    print("2. View Password")
                    print("3. Quit")
                    choice = input("Enter your choice: ")
                    if choice == "1":
                        add_password()
                    elif choice == "2":
                        view_password()
                    elif choice == "3":
                        break
                    else:
                        print("Invalid choice. Please select a valid option.")
            else:
                print("Login failed!")
        else:
            print("Username not found.")

    login()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()