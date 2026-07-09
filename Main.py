#!/usr/bin/env python3
"""
Simplified Bank Management System
Sab kuch ek file mein mila hua hai taki samajhne mein aasaan ho.
"""

import random
import string
import hashlib
import psycopg2
import os
from Database import connect_to_database

# ==================== UTILITY FUNCTIONS ====================
def __hash_pin(pin):
    """
    PIN ko hash karta hai security ke liye.
    Ye private function hai sirf internal use ke liye.
    
    Arguments:
    - pin (str): Hash karne ke liye 4-digit PIN
    
    Returns:
    - str: SHA256 hashed PIN
    
    Kya karta hai:
    1. PIN ko SHA256 algorithm se hash karta hai
    2. Hashed PIN return karta hai
    
    Kaise help karta hai:
    - Database security enhance karta hai
    - Plain text PINs ko protect karta hai
    - Data breach protection provide karta hai
    """
    return hashlib.sha256(pin.encode()).hexdigest()

def __verify_pin(input_pin, stored_hash):
    """
    Input PIN ko stored hash ke saath verify karta hai.
    Ye private function hai sirf internal use ke liye.
    
    Arguments:
    - input_pin (str): User dwara diya gaya PIN
    - stored_hash (str): Database mein stored hashed PIN
    
    Returns:
    - bool: True agar PIN match karta hai, warna False
    
    Kya karta hai:
    1. Input PIN ko hash karta hai
    2. Hashed input ko stored hash ke saath compare karta hai
    3. Match/mismatch result return karta hai
    
    Kaise help karta hai:
    - User authentication karta hai
    - Security verification provide karta hai
    - Unauthorized access prevent karta hai
    """
    return __hash_pin(input_pin) == stored_hash

# ==================== DATABASE TABLE INITIALIZATION ====================
def initialize_tables():
    """
    Agar accounts aur audit tables nahi hai toh banata hai.
    Ye function database schema ko sahi tarah se set karta hai.
    
    Kya karta hai:
    1. Accounts table banata hai jo user accounts store karta hai
    2. Audit table banata hai jo sab transactions log karta hai
    3. Tables ke beech relationship establish karta hai
    
    Kaise help karta hai:
    - Database structure ready karta hai
    - Foreign key constraints lagata hai security ke liye
    - Error handling karta hai agar kuch galat ho jaye
    """
    connection = connect_to_database()
    if not connection:
        return False
        
    try:
        cursor = connection.cursor()
        
        # accounts table banata hai saare constraints ke saath
        # PIN column ko VARCHAR(64) kar diya gaya hai taaki hashed PINs fit ho sake
        create_accounts_table = """
        CREATE TABLE IF NOT EXISTS accounts (
            account_number VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            pin VARCHAR(64) NOT NULL,
            balance DECIMAL(15, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # audit table banata hai foreign key relationship aur holder_name column ke saath
        create_audit_table = """
        CREATE TABLE IF NOT EXISTS audit (
            id SERIAL PRIMARY KEY,
            account_number VARCHAR(50),
            holder_name VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            amount DECIMAL(15, 2) DEFAULT 0.00,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_number) REFERENCES accounts(account_number)
        );
        """
        
        cursor.execute(create_accounts_table)
        cursor.execute(create_audit_table)
        
        connection.commit()
        cursor.close()
        return True
    except Exception as error:
        print(f"Error initializing tables: {error}")
        return False

# ==================== AUDIT CLASS ====================
class Audit:
    """Bank system ke liye sab audit logging functionality handle karta hai"""
    
    @staticmethod
    def log_action(account_number, holder_name, action, amount = 0.0):
        """
        Audit table mein kisi action ko log karta hai.
        
        Arguments:
        - account_number (str): Jo account number track karna hai
        - holder_name (str): Account holder ka naam
        - action (str): Kya action hua (jaise "Amount deposited")
        - amount (float): Paise kitne lene diye gaye (default: 0.0)
        
        Returns:
        - bool: True agar logging successful ho, warna False
        
        Kya karta hai:
        1. Database connection establish karta hai
        2. Audit table mein naya record insert karta hai
        3. Transaction details save karta hai
        
        Kaise help karta hai:
        - Security ke liye sab actions track karta hai
        - Debugging ke liye transaction history provide karta hai
        - Compliance ke liye audit trail maintain karta hai
        """
        connection = connect_to_database()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO audit (account_number, holder_name, action, amount) VALUES (%s, %s, %s, %s)",
                (account_number, holder_name, action, amount)
            )
            connection.commit()
            cursor.close()
            return True
        except Exception as error:
            print(f"Error logging audit action: {error}")
            return False
    
    @staticmethod
    def get_audit_logs(account_number):
        """
        Kisi specific account ke liye audit logs nikalta hai.
        
        Arguments:
        - account_number (str): Jo account ka history chahiye
        
        Returns:
        - list: Audit log entries ki list details ke saath
        
        Kya karta hai:
        1. Database se specific account ke sab transactions nikalta hai
        2. Results ko descending order mein sort karta hai (latest first)
        3. Data ko readable format mein convert karta hai
        
        Kaise help karta hai:
        - User ko apni transaction history dikhata hai
        - Account activity tracking karta hai
        - Dispute resolution ke liye evidence provide karta hai
        """
        connection = connect_to_database()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, holder_name, action, amount, timestamp 
                FROM audit 
                WHERE account_number = %s 
                ORDER BY timestamp DESC
                """,
                (account_number,)
            )
            results = cursor.fetchall()
            cursor.close()
            
            logs = []
            for row in results:
                logs.append({
                    'id': row[0],
                    'holder_name': row[1],
                    'action': row[2],
                    'amount': float(row[3]),
                    'timestamp': row[4]
                })
            return logs
        except Exception as error:
            print(f"Error retrieving audit logs: {error}")
            return []
    
    @staticmethod
    def get_all_audit_logs():
        """
        Sab audit logs nikalta hai (admin function).
        
        Arguments:
        - Koi argument nahi leta (admin function hai)
        
        Returns:
        - list: Sab audit log entries ki list account details ke saath
        
        Kya karta hai:
        1. Database se sab accounts ki audit logs nikalta hai
        2. Results ko descending order mein sort karta hai
        3. Admin ko complete transaction overview deta hai
        
        Kaise help karta hai:
        - Admin ko system monitoring karna padta hai
        - Suspicious activity identify karta hai
        - Reporting aur analytics ke liye data provide karta hai
        """
        connection = connect_to_database()
        if not connection:
            return []
            
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, account_number, holder_name, action, amount, timestamp 
                FROM audit 
                ORDER BY timestamp DESC
                """
            )
            results = cursor.fetchall()
            cursor.close()
            
            logs = []
            for row in results:
                logs.append({
                    'id': row[0],
                    'account_number': row[1],
                    'holder_name': row[2],
                    'action': row[3],
                    'amount': float(row[4]),
                    'timestamp': row[5]
                })
            return logs
        except Exception as error:
            print(f"Error retrieving all audit logs: {error}")
            return []
    
    @staticmethod
    def clear_audit_logs():
        """
        Sab audit logs ko clear karta hai (admin function).
        
        Arguments:
        - Koi argument nahi leta (admin function hai)
        
        Returns:
        - bool: True agar clearing successful ho, warna False
        
        Kya karta hai:
        1. Audit table se sab records delete karta hai
        2. Database space free karta hai
        3. Privacy compliance ke liye old data remove karta hai
        
        Kaise help karta hai:
        - Database maintenance karta hai
        - Storage optimization karta hai
        - Data retention policies follow karta hai
        """
        connection = connect_to_database()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM audit")
            connection.commit()
            cursor.close()
            return True
        except Exception as error:
            print(f"Error clearing audit logs: {error}")
            return False

# ==================== ACCOUNT CLASS ====================
class Account:
    """Bank account ko represent karta hai OOP principles ke saath"""
    
    def __init__(self, name = "", pin = "", account_number = ""):
        """
        Naya Account object initialize karta hai.
        
        Arguments:
        - name (str): Account holder ka naam
        - pin (str): 4-digit PIN security ke liye (plain text)
        - account_number (str): Unique account identifier (agar nahi diya toh auto-generate hoga)
        
        Kya karta hai:
        1. Account object create karta hai
        2. Agar account_number nahi diya toh naya generate karta hai
        3. Initial values set karta hai (name, pin, balance)
        4. PIN ko hash kar deta hai storage ke liye
        
        Kaise help karta hai:
        - Account creation process ko streamline karta hai
        - Unique account numbers ensure karta hai
        - Data encapsulation provide karta hai
        - Security enhance karta hai PIN hashing se
        """
        # Private attributes taaki encapsulation ensure ho
        self.__account_number = account_number if account_number else self.__generate_account_number()
        self.__name = name
        # PIN ko hash kar diya jata hai storage ke liye
        self.__pin = __hash_pin(pin) if pin else ""
        self.__balance = 0.0
        
    @staticmethod
    def __generate_account_number():
        """
        Random alphanumeric account number generate karta hai.
        Ye uniqueness aur unpredictability ensure karta hai security ke liye.
        
        Arguments:
        - Koi argument nahi leta
        
        Returns:
        - str: 10-character random alphanumeric string
        
        Kya karta hai:
        1. Random 10-character string generate karta hai
        2. Letters aur digits ka combination use karta hai
        3. Unique account number create karta hai
        
        Kaise help karta hai:
        - Security enhance karta hai unpredictable numbers se
        - Collision avoidance karta hai
        - Professional account numbering system provide karta hai
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    # GETTER METHODS - Private attributes tak controlled access provide karta hai
    def get_account_number(self):
        """
        Account number deta hai.
        
        Arguments:
        - Koi argument nahi leta (instance method hai)
        
        Returns:
        - str: Account number
        
        Kya karta hai:
        1. Private __account_number attribute return karta hai
        2. Read-only access provide karta hai
        
        Kaise help karta hai:
        - Account identification ke liye use hota hai
        - Transactions linking ke liye zaroori hai
        - Security ke liye controlled access provide karta hai
        """
        return self.__account_number
    
    def get_name(self):
        """
        Account holder ka naam deta hai.
        
        Arguments:
        - Koi argument nahi leta (instance method hai)
        
        Returns:
        - str: Account holder ka naam
        
        Kya karta hai:
        1. Private __name attribute return karta hai
        2. Read-only access provide karta hai
        
        Kaise help karta hai:
        - Personalization ke liye use hota hai
        - Audit logs mein name display karne ke liye
        - User recognition ke liye helpful hai
        """
        return self.__name
    
    def get_balance(self):
        """
        Current account balance deta hai.
        
        Arguments:
        - Koi argument nahi leta (instance method hai)
        
        Returns:
        - float: Current account balance
        
        Kya karta hai:
        1. Private __balance attribute return karta hai
        2. Read-only access provide karta hai
        
        Kaise help karta hai:
        - User ko current balance dikhata hai
        - Transaction validation ke liye use hota hai
        - Financial awareness promote karta hai
        """
        return self.__balance
    
    def get_pin_hash(self):
        """
        Account PIN hash deta hai (storage ke liye use hota hai).
        
        Arguments:
        - Koi argument nahi leta (instance method hai)
        
        Returns:
        - str: Hashed account PIN
        
        Kya karta hai:
        1. Private __pin attribute return karta hai (jo already hashed hai)
        2. Read-only access provide karta hai
        
        Kaise help karta hai:
        - Database storage ke liye use hota hai
        - Security verification ke liye zaroori hai
        - Authentication ke liye helpful hai
        """
        return self.__pin
    
    # SETTER METHODS - Private attributes mein controlled modification karta hai
    def set_name(self, name):
        """
        Account holder ka naam update karta hai.
        
        Arguments:
        - name (str): Naya naam set karne ke liye
        
        Kya karta hai:
        1. Private __name attribute update karta hai
        2. Controlled modification provide karta hai
        
        Kaise help karta hai:
        - User profile updates ke liye use hota hai
        - Name corrections ke liye helpful hai
        - Personal information management karta hai
        """
        self.__name = name
    
    def set_pin(self, pin):
        """
        Account PIN update karta hai (plain text input leta hai aur hash karta hai).
        
        Arguments:
        - pin (str): Naya 4-digit PIN set karne ke liye (plain text)
        
        Kya karta hai:
        1. Input PIN ko hash karta hai
        2. Private __pin attribute update karta hai hashed value se
        3. Security credentials change karta hai
        
        Kaise help karta hai:
        - Security enhancement ke liye use hota hai
        - PIN changes ke liye zaroori hai
        - Account protection maintain karta hai
        """
        self.__pin = __hash_pin(pin)
    
    def set_balance(self, balance):
        """
        Account balance update karta hai.
        
        Arguments:
        - balance (float): Naya balance set karne ke liye
        
        Kya karta hai:
        1. Private __balance attribute update karta hai
        2. Financial state change karta hai
        
        Kaise help karta hai:
        - Internal balance management ke liye use hota hai
        - Transaction processing ke liye zaroori hai
        - Financial calculations ke liye important hai
        """
        self.__balance = balance
    
    def deposit(self, amount):
        """
        Account mein paise jama karta hai.
        Ye method balance update karta hai lekin database mein nahi save karta.
        
        Arguments:
        - amount (float): Jama karne ke liye paise ki amount
        
        Returns:
        - bool: True agar deposit successful ho, warna False
        
        Kya karta hai:
        1. Amount positive hone ki validation karta hai
        2. Balance mein amount add karta hai
        3. Success/failure return karta hai
        
        Kaise help karta hai:
        - Funds addition ke liye use hota hai
        - Balance validation karta hai
        - Transaction processing ko facilitate karta hai
        """
        if amount <= 0:
            return False
        self.__balance += amount
        return True
    
    def withdraw(self, amount):
        """
        Account se paise nikalta hai.
        Ye method balance update karta hai lekin database mein nahi save karta.
        
        Arguments:
        - amount (float): Nikalne ke liye paise ki amount
        
        Returns:
        - bool: True agar withdrawal successful ho, warna False
        
        Kya karta hai:
        1. Amount positive hone ki validation karta hai
        2. Sufficient funds available hone ki check karta hai
        3. Balance se amount deduct karta hai
        4. Success/failure return karta hai
        
        Kaise help karta hai:
        - Funds withdrawal ke liye use hota hai
        - Overdraft prevention karta hai
        - Transaction authorization karta hai
        """
        if amount <= 0 or amount > self.__balance:
            return False
        self.__balance -= amount
        return True
    
    @classmethod
    def load_from_db(cls, account_number, pin):
        """
        Database se account load karta hai.
        Ye class method hai jo database data se Account object banata hai.
        
        Arguments:
        - account_number (str): Load karne ke liye account number
        - pin (str): Authentication ke liye PIN (plain text)
        
        Returns:
        - Account object agar successful ho, warna None
        
        Kya karta hai:
        1. Database connection establish karta hai
        2. Account details database se fetch karta hai
        3. Account object create karta hai fetched data se
        4. PIN verification karta hai (hashed comparison)
        
        Kaise help karta hai:
        - Account persistence ke liye use hota hai
        - User authentication karta hai
        - Session management ke liye zaroori hai
        """
        connection = connect_to_database()
        if not connection:
            return None
            
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT account_number, name, pin, balance FROM accounts WHERE account_number = %s",
                (account_number,)
            )
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                # Stored PIN hash nikalta hai
                stored_pin_hash = result[2]
                
                # Input PIN ko verify karta hai stored hash ke saath
                if __verify_pin(pin, stored_pin_hash):
                    # Account object database data ke saath banata hai
                    account = cls(result[1], "", result[0])  # PIN ko empty rakha jata hai
                    account.set_balance(float(result[3]))
                    # Stored hash ko set karta hai
                    account.__pin = stored_pin_hash
                    return account
            return None
        except Exception as error:
            print(f"Error loading account: {error}")
            return None
    
    def save_to_db(self):
        """
        Account ko database mein save karta hai.
        Ye method naye accounts create karta hai aur existing ones update karta hai.
        
        Arguments:
        - Koi argument nahi leta (instance method hai)
        
        Returns:
        - bool: True agar save successful ho, warna False
        
        Kya karta hai:
        1. Database connection establish karta hai
        2. INSERT/UPDATE query execute karta hai
        3. Conflict resolution handle karta hai (ON CONFLICT)
        4. Transaction commit karta hai
        
        Kaise help karta hai:
        - Data persistence ensure karta hai
        - Account information ko durable banata hai
        - Concurrent access handle karta hai
        """
        connection = connect_to_database()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO accounts (account_number, name, pin, balance)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (account_number)
                DO UPDATE SET name = %s, pin = %s, balance = %s
                """,
                (self.__account_number, self.__name, self.__pin, self.__balance,
                 self.__name, self.__pin, self.__balance)
            )
            connection.commit()
            cursor.close()
            return True
        except Exception as error:
            print(f"Error saving account: {error}")
            return False
    
    def delete_from_db(self):
        """
        Account ko database se delete karta hai.
        Ye method account record ko permanent remove karta hai.
        
        Arguments:
        - Koi argument nahi leta (instance method hai)
        
        Returns:
        - bool: True agar delete successful ho, warna False
        
        Kya karta hai:
        1. Database connection establish karta hai
        2. DELETE query execute karta hai
        3. Account record permanently remove karta hai
        4. Transaction commit karta hai
        
        Kaise help karta hai:
        - Account closure ke liye use hota hai
        - Data privacy compliance karta hai
        - Storage cleanup karta hai
        """
        connection = connect_to_database()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM accounts WHERE account_number = %s", (self.__account_number,))
            connection.commit()
            cursor.close()
            return True
        except Exception as error:
            print(f"Error deleting account: {error}")
            return False

# ==================== BANK SYSTEM CLASS ====================
class BankSystem:
    """Main bank system jo CRUD operations aur audit integration handle karta hai"""
    
    def __init__(self):
        """
        BankSystem initialize karta hai aur database tables set karta hai.
        
        Arguments:
        - Koi argument nahi leta
        
        Kya karta hai:
        1. BankSystem object create karta hai
        2. Database tables initialize karta hai
        3. System setup complete karta hai
        
        Kaise help karta hai:
        - Application startup ke liye zaroori hai
        - Database readiness ensure karta hai
        - System initialization ko handle karta hai
        """
        initialize_tables()
    
    def create_account(self, name, pin):
        """
        Naya account banata hai aur action log karta hai.
        
        Arguments:
        - name (str): Account holder ka naam
        - pin (str): 4-digit security PIN (plain text)
        
        Returns:
        - Account object agar successful ho, warna None
        
        Kya karta hai:
        1. Naya Account object create karta hai
        2. Account ko database mein save karta hai
        3. Account creation ko audit trail mein log karta hai
        4. Created account return karta hai
        
        Kaise help karta hai:
        - New user onboarding ke liye use hota hai
        - Account provisioning karta hai
        - Audit compliance maintain karta hai
        """
        account = Account(name, pin)
        if account.save_to_db():
            # Account creation ko audit trail mein log karta hai
            Audit.log_action(account.get_account_number(), account.get_name(), "Account Created", 0.0)
            return account
        return None
    
    def read_account(self, account_number, pin):
        """
        Database se account read/load karta hai.
        
        Arguments:
        - account_number (str): Load karne ke liye account number
        - pin (str): Authentication ke liye PIN (plain text)
        
        Returns:
        - Account object agar successful ho, warna None
        
        Kya karta hai:
        1. Account database se load karta hai
        2. PIN verification karta hai (hashed comparison)
        3. Balance check ko audit trail mein log karta hai
        4. Loaded account return karta hai
        
        Kaise help karta hai:
        - User authentication karta hai
        - Account access provide karta hai
        - Security verification karta hai
        """
        account = Account.load_from_db(account_number, pin)
        if account:
            # Balance check ko audit trail mein log karta hai
            Audit.log_action(account_number, account.get_name(), "Balance checked", 0.0)
        return account
    
    def update_account(self, account):
        """
        Account information update karta hai.
        
        Arguments:
        - account (Account): Update karne ke liye Account object
        
        Returns:
        - bool: True agar update successful ho, warna False
        
        Kya karta hai:
        1. Account object ko database mein save karta hai
        2. Changes ko persistent banata hai
        
        Kaise help karta hai:
        - Account modifications ke liye use hota hai
        - Data synchronization karta hai
        - Information updates ko handle karta hai
        """
        return account.save_to_db()
    
    def delete_account(self, account_number, pin):
        """
        Account delete karta hai aur action log karta hai.
        
        Arguments:
        - account_number (str): Delete karne ke liye account number
        - pin (str): Authentication ke liye PIN (plain text)
        
        Returns:
        - bool: True agar delete successful ho, warna False
        
        Kya karta hai:
        1. Account load karta hai verification ke liye
        2. Account ko database se delete karta hai
        3. Account deletion ko audit trail mein log karta hai
        4. Success/failure return karta hai
        
        Kaise help karta hai:
        - Account closure process ko handle karta hai
        - Security verification karta hai
        - Audit compliance maintain karta hai
        """
        account = Account.load_from_db(account_number, pin)
        if account:
            success = account.delete_from_db()
            if success:
                # Account deletion ko audit trail mein log karta hai
                Audit.log_action(account_number, account.get_name(), "Account Deleted", 0.0)
                return True
        return False
    
    def deposit(self, account_number, pin, amount):
        """
        Account mein paise jama karta hai aur action log karta hai.
        
        Arguments:
        - account_number (str): Target account number
        - pin (str): Authentication ke liye PIN (plain text)
        - amount (float): Jama karne ke liye paise ki amount
        
        Returns:
        - bool: True agar deposit successful ho, warna False
        
        Kya karta hai:
        1. Account load karta hai verification ke liye
        2. Amount deposit karta hai account mein
        3. Changes ko database mein save karta hai
        4. Deposit ko audit trail mein log karta hai
        5. Success/failure return karta hai
        
        Kaise help karta hai:
        - Funds addition process ko manage karta hai
        - Transaction logging karta hai
        - Security verification karta hai
        """
        account = Account.load_from_db(account_number, pin)
        if account and account.deposit(amount):
            if account.save_to_db():
                # Deposit ko audit trail mein log karta hai
                Audit.log_action(account_number, account.get_name(), "Amount deposited", amount)
                return True
        return False
    
    def withdraw(self, account_number, pin, amount):
        """
        Account se paise nikalta hai aur action log karta hai.
        
        Arguments:
        - account_number (str): Target account number
        - pin (str): Authentication ke liye PIN (plain text)
        - amount (float): Nikalne ke liye paise ki amount
        
        Returns:
        - bool: True agar withdrawal successful ho, warna False
        
        Kya karta hai:
        1. Account load karta hai verification ke liye
        2. Amount withdraw karta hai account se
        3. Changes ko database mein save karta hai
        4. Withdrawal ko audit trail mein log karta hai
        5. Success/failure return karta hai
        
        Kaise help karta hai:
        - Funds withdrawal process ko manage karta hai
        - Transaction logging karta hai
        - Security verification karta hai
        """
        account = Account.load_from_db(account_number, pin)
        if account and account.withdraw(amount):
            if account.save_to_db():
                # Withdrawal ko audit trail mein log karta hai
                Audit.log_action(account_number, account.get_name(), "Amount withdrawn", amount)
                return True
        return False
    
    def get_account_balance(self, account_number, pin):
        """
        Account balance deta hai aur action log karta hai.
        
        Arguments:
        - account_number (str): Target account number
        - pin (str): Authentication ke liye PIN (plain text)
        
        Returns:
        - float: Account balance agar successful ho, warna None
        
        Kya karta hai:
        1. Account load karta hai verification ke liye
        2. Account balance return karta hai
        3. Balance check ko audit trail mein log karta hai
        
        Kaise help karta hai:
        - Financial information provide karta hai
        - User inquiry ko satisfy karta hai
        - Audit compliance maintain karta hai
        """
        account = self.read_account(account_number, pin)
        return account.get_balance() if account else None
    
    def get_audit_logs(self, account_number):
        """
        Account ke liye audit logs deta hai.
        
        Arguments:
        - account_number (str): Target account number
        
        Returns:
        - list: Audit logs ki list
        
        Kya karta hai:
        1. Audit class se account logs fetch karta hai
        2. Transaction history return karta hai
        
        Kaise help karta hai:
        - Transaction transparency provide karta hai
        - User activity tracking karta hai
        - Accountability maintain karta hai
        """
        return Audit.get_audit_logs(account_number)
    
    def get_all_audit_logs(self):
        """
        Sab audit logs deta hai (admin function).
        
        Arguments:
        - Koi argument nahi leta (admin function hai)
        
        Returns:
        - list: Sab audit logs ki list
        
        Kya karta hai:
        1. Audit class se sab logs fetch karta hai
        2. Admin ko complete overview deta hai
        
        Kaise help karta hai:
        - System monitoring ke liye use hota hai
        - Administrative oversight provide karta hai
        - Compliance reporting karta hai
        """
        return Audit.get_all_audit_logs()
    
    def clear_audit_logs(self):
        """
        Sab audit logs clear karta hai (admin function).
        
        Arguments:
        - Koi argument nahi leta (admin function hai)
        
        Returns:
        - bool: True agar clearing successful ho, warna False
        
        Kya karta hai:
        1. Audit class se sab logs clear karta hai
        2. Database maintenance karta hai
        
        Kaise help karta hai:
        - Data management ke liye use hota hai
        - Storage optimization karta hai
        - Privacy compliance maintain karta hai
        """
        return Audit.clear_audit_logs()

# ==================== UTILITY FUNCTIONS ====================
def get_valid_amount(prompt):
    """
    User input se valid amount le leta hai
    
    Arguments:
    - prompt (str): User se input maangne ke liye message
    
    Returns:
    - float: Valid amount
    
    Kya karta hai:
    1. User se amount input maangta hai
    2. Input validation karta hai
    3. Positive number ensure karta hai
    4. Valid amount return karta hai
    
    Kaise help karta hai:
    - Input sanitization karta hai
    - Error handling provide karta hai
    - User experience improve karta hai
    """
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return amount
        except ValueError:
            print("Please enter a valid number.")

# ==================== CLI MENU FUNCTIONS ====================
def create_account_cli(bank):
    """
    Account creation handle karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    
    Kya karta hai:
    1. User se account details collect karta hai
    2. Validation karta hai input ki
    3. Naya account create karta hai
    4. Success/error messages dikhata hai
    
    Kaise help karta hai:
    - User onboarding ko facilitate karta hai
    - Data collection karta hai
    - Feedback provide karta hai
    """
    print("=" * 40)
    print("        CREATE NEW ACCOUNT")
    print("=" * 40)
    
    name = input("Enter your name: ").strip()
    if not name:
        print("Naam khali nahi ho sakta.")
        input("Press Enter to continue...")
        return
    
    # PIN le leta hai bina masking ke
    pin = input("4-digit PIN daalo: ").strip()
    if len(pin) != 4 or not pin.isdigit():
        print("PIN ek 4-digit number hona chahiye.")
        input("Press Enter to continue...")
        return
    
    confirm_pin = input("Apna PIN confirm karo: ").strip()
    if pin != confirm_pin:
        print("PINs match nahi ho rahe.")
        input("Press Enter to continue...")
        return
    
    account = bank.create_account(name, pin)
    if account:
        print(f"\nAccount successfully ban gaya!")
        print(f"Account Number: {account.get_account_number()}")
        print("Apna account number aur PIN securely save karo.")
    else:
        print("\nAccount banana fail ho gaya. Kripya fir se try karein.")
    
    input("Press Enter to continue...")

def login_to_account_cli(bank):
    """
    Account login aur operations handle karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    
    Kya karta hai:
    1. User credentials collect karta hai
    2. Authentication karta hai
    3. Account dashboard display karta hai
    4. User operations handle karta hai
    
    Kaise help karta hai:
    - Secure access provide karta hai
    - Session management karta hai
    - User interaction ko handle karta hai
    """
    print("=" * 40)
    print("          ACCOUNT LOGIN")
    print("=" * 40)
    
    account_number = input("Apna account number daalo: ").strip()
    if not account_number:
        print("Account number khali nahi ho sakta.")
        input("Press Enter to continue...")
        return
    
    pin = input("Apna PIN daalo: ").strip()
    
    account = bank.read_account(account_number, pin)
    if not account:
        print("Galat account number ya PIN.")
        input("Press Enter to continue...")
        return
    
    # Account operations menu
    while True:
        print("=" * 40)
        print(f"        WELCOME, {account.get_name()}!")
        print(f"        ACCOUNT: {account.get_account_number()}")
        print("=" * 40)
        print("1. Balance Check karo")
        print("2. Paise jama karo")
        print("3. Paise nikalo")
        print("4. Transaction History dekho")
        print("5. Account Info update karo")
        print("6. Account delete karo")
        print("7. Logout")
        print("=" * 40)
        
        choice = input("Apna choice daalo (1-7): ").strip()
        
        if choice == '1':
            check_balance_cli(bank, account)
        elif choice == '2':
            deposit_money_cli(bank, account)
        elif choice == '3':
            withdraw_money_cli(bank, account)
        elif choice == '4':
            view_transaction_history_cli(bank, account)
        elif choice == '5':
            update_account_info_cli(bank, account)
        elif choice == '6':
            if delete_account_cli(bank, account):
                break  # Deletion ke baad main menu par wapas jaao
        elif choice == '7':
            break  # Logout
        else:
            print("Galat choice. Kripya fir se try karein.")
            input("Press Enter to continue...")

def check_balance_cli(bank, account):
    """
    Account balance check karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    - account (Account): Current logged-in account
    
    Kya karta hai:
    1. Account balance fetch karta hai
    2. Balance display karta hai user ko
    3. User input wait karta hai continue karne ke liye
    
    Kaise help karta hai:
    - Financial awareness promote karta hai
    - Account information provide karta hai
    - User inquiry satisfy karta hai
    """
    print("=" * 40)
    print("         ACCOUNT BALANCE")
    print("=" * 40)
    
    balance = bank.get_account_balance(account.get_account_number(), account.get_pin_hash())
    if balance is not None:
        print(f"Current Balance: ${balance:.2f}")
    else:
        print("Balance nikalne mein error aaya.")
    
    input("Press Enter to continue...")

def deposit_money_cli(bank, account):
    """
    Paise jama karne ka kaam handle karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    - account (Account): Current logged-in account
    
    Kya karta hai:
    1. User se amount collect karta hai
    2. Deposit operation perform karta hai
    3. Success/error messages dikhata hai
    4. Updated balance display karta hai
    
    Kaise help karta hai:
    - Funds addition process ko manage karta hai
    - Transaction feedback provide karta hai
    - User experience enhance karta hai
    """
    print("=" * 40)
    print("          Paise Jama Karo")
    print("=" * 40)
    
    amount = get_valid_amount("Jitne paise jama karne hain wo daalo: $")
    
    if bank.deposit(account.get_account_number(), account.get_pin_hash(), amount):
        print(f"${amount:.2f} successfully jama ho gaye!")
        # Display ke liye account balance update karo
        account = bank.read_account(account.get_account_number(), account.get_pin_hash())
        if account:
            print(f"Naya Balance: ${account.get_balance():.2f}")
    else:
        print("Paise jama karne mein problem aayi. Kripya fir se try karein.")
    
    input("Press Enter to continue...")

def withdraw_money_cli(bank, account):
    """
    Paise nikalne ka kaam handle karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    - account (Account): Current logged-in account
    
    Kya karta hai:
    1. User se amount collect karta hai
    2. Withdrawal operation perform karta hai
    3. Success/error messages dikhata hai
    4. Updated balance display karta hai
    
    Kaise help karta hai:
    - Funds withdrawal process ko manage karta hai
    - Transaction feedback provide karta hai
    - User experience enhance karta hai
    """
    print("=" * 40)
    print("         Paise Nikalo")
    print("=" * 40)
    
    amount = get_valid_amount("Kitne paise nikalne hain wo daalo: $")
    
    if bank.withdraw(account.get_account_number(), account.get_pin_hash(), amount):
        print(f"${amount:.2f} successfully nikal diye gaye!")
        # Display ke liye account balance update karo
        account = bank.read_account(account.get_account_number(), account.get_pin_hash())
        if account:
            print(f"Naya Balance: ${account.get_balance():.2f}")
    else:
        print("Paise nikalne mein problem aayi. Kam paise hain ya galat amount.")
    
    input("Press Enter to continue...")

def view_transaction_history_cli(bank, account):
    """
    Transaction history dekhata hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    - account (Account): Current logged-in account
    
    Kya karta hai:
    1. Account ke audit logs fetch karta hai
    2. Transaction history format mein display karta hai
    3. User input wait karta hai continue karne ke liye
    
    Kaise help karta hai:
    - Transparency provide karta hai
    - Account activity track karta hai
    - Dispute resolution ke liye helpful hai
    """
    print("=" * 40)
    print("      TRANSACTION HISTORY")
    print("=" * 40)
    
    logs = bank.get_audit_logs(account.get_account_number())
    if not logs:
        print("Koi transaction history nahi mili.")
    else:
        print(f"{'ID':<5} {'Naam':<15} {'Action':<20} {'Amount':<10} {'Time':<20}")
        print("-" * 70)
        for log in logs:
            amount_str = f"${log['amount']:.2f}" if log['amount'] > 0 else ""
            print(f"{log['id']:<5} {log['holder_name']:<15} {log['action']:<20} {amount_str:<10} {log['timestamp']:<20}")
    
    input("Press Enter to continue...")

def update_account_info_cli(bank, account):
    """
    Account information update karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    - account (Account): Current logged-in account
    
    Kya karta hai:
    1. Update options dikhata hai (name/PIN)
    2. User choice ke according update karta hai
    3. Changes ko database mein save karta hai
    4. Success/error messages dikhata hai
    
    Kaise help karta hai:
    - Account management ko facilitate karta hai
    - User preferences accommodate karta hai
    - Data accuracy maintain karta hai
    """
    print("=" * 40)
    print("      ACCOUNT INFO UPDATE KARO")
    print("=" * 40)
    print("1. Naam badlo")
    print("2. PIN badlo")
    print("3. Account Menu par wapas jao")
    print("=" * 40)
    
    choice = input("Apna choice daalo (1-3): ").strip()
    
    if choice == '1':
        new_name = input("Naya naam daalo: ").strip()
        if new_name:
            account.set_name(new_name)
            if bank.update_account(account):
                print("Naam successfully update ho gaya!")
            else:
                print("Naam update karne mein problem aayi.")
        else:
            print("Naam khali nahi ho sakta.")
    elif choice == '2':
        old_pin = input("Current PIN daalo: ").strip()
        if __verify_pin(old_pin, account.get_pin_hash()):
            new_pin = input("Naya 4-digit PIN daalo: ").strip()
            if len(new_pin) == 4 and new_pin.isdigit():
                confirm_pin = input("Naya PIN confirm karo: ").strip()
                if new_pin == confirm_pin:
                    account.set_pin(new_pin)
                    if bank.update_account(account):
                        print("PIN successfully update ho gaya!")
                    else:
                        print("PIN update karne mein problem aayi.")
                else:
                    print("PINs match nahi ho rahe.")
            else:
                print("PIN ek 4-digit number hona chahiye.")
        else:
            print("Galat current PIN.")
    elif choice != '3':
        print("Galat choice.")
    
    input("Press Enter to continue...")

def delete_account_cli(bank, account):
    """
    Account deletion handle karta hai
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    - account (Account): Current logged-in account
    
    Returns:
    - bool: True agar deletion successful ho, warna False
    
    Kya karta hai:
    1. Deletion confirmation maangta hai
    2. Security verification karta hai
    3. Account delete karta hai
    4. Success/error messages dikhata hai
    
    Kaise help karta hai:
    - Account closure process ko manage karta hai
    - Security compliance maintain karta hai
    - User control provide karta hai
    """
    print("=" * 40)
    print("        ACCOUNT DELETE KARO")
    print("=" * 40)
    print("WARNING: Ye action wapas nahi kiya ja sakta!")
    print("Confirmation ke liye aapko dena hoga:")
    print(f"1. Account Number: {account.get_account_number()}")
    print("2. Apka PIN")
    print("=" * 40)
    
    confirmation = input("Kya aap sach mein apna account delete karna chahte hain? (yes/no): ").strip().lower()
    if confirmation != 'yes':
        print("Account deletion cancel ho gaya.")
        input("Press Enter to continue...")
        return False
    
    # Security ke liye account number aur PIN verify karo
    acc_num_input = input("Apna account number fir se daalo: ").strip()
    pin_input = input("Apna PIN daalo: ").strip()
    
    if acc_num_input == account.get_account_number() and __verify_pin(pin_input, account.get_pin_hash()):
        if bank.delete_account(account.get_account_number(), pin_input):
            print("Account successfully delete ho gaya!")
            input("Press Enter to continue...")
            return True
        else:
            print("Account delete karne mein problem aayi.")
    else:
        print("Account number ya PIN galat hai. Deletion cancel ho gaya.")
    
    input("Press Enter to continue...")
    return False

def admin_view_audit_logs_cli(bank):
    """
    Admin function sab audit logs dekhne ke liye
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    
    Kya karta hai:
    1. Sab accounts ki audit logs fetch karta hai
    2. Admin ko complete transaction overview deta hai
    3. Formatted display karta hai logs ka
    
    Kaise help karta hai:
    - System monitoring ke liye use hota hai
    - Administrative oversight provide karta hai
    - Compliance reporting karta hai
    """
    print("=" * 40)
    print("       SAB AUDIT LOGS")
    print("=" * 40)
    
    # Security ke liye real system mein iski protection password se ki ja sakti hai
    logs = bank.get_all_audit_logs()
    if not logs:
        print("Koi audit logs nahi mili.")
    else:
        print(f"{'ID':<5} {'Account':<12} {'Naam':<15} {'Action':<20} {'Amount':<10} {'Time':<20}")
        print("-" * 85)
        for log in logs:
            amount_str = f"${log['amount']:.2f}" if log['amount'] > 0 else ""
            print(f"{log['id']:<5} {log['account_number']:<12} {log['holder_name']:<15} {log['action']:<20} {amount_str:<10} {log['timestamp']:<20}")
    
    input("Press Enter to continue...")

def admin_clear_audit_logs_cli(bank):
    """
    Admin function sab audit logs clear karne ke liye
    
    Arguments:
    - bank (BankSystem): BankSystem object operations ke liye
    
    Kya karta hai:
    1. Admin se confirmation maangta hai
    2. Sab audit logs clear karta hai
    3. Success/error messages dikhata hai
    
    Kaise help karta hai:
    - Database maintenance ke liye use hota hai
    - Storage optimization karta hai
    - Privacy compliance maintain karta hai
    """
    print("=" * 40)
    print("      AUDIT LOGS CLEAR KARO")
    print("=" * 40)
    print("WARNING: Ye sab audit logs ko permanent delete kar dega!")
    print("=" * 40)
    
    confirmation = input("Kya aap sach mein sab audit logs clear karna chahte hain? (yes/no): ").strip().lower()
    if confirmation == 'yes':
        if bank.clear_audit_logs():
            print("Sab audit logs successfully clear ho gayi!")
        else:
            print("Audit logs clear karne mein problem aayi.")
    else:
        print("Operation cancel ho gaya.")
    
    input("Press Enter to continue...")

def main_menu_cli():
    """
    Main menu display karta hai aur user choices handle karta hai
    
    Arguments:
    - Koi argument nahi leta
    
    Kya karta hai:
    1. Main menu display karta hai
    2. User input collect karta hai
    3. Selected operation execute karta hai
    4. Program flow manage karta hai
    
    Kaise help karta hai:
    - User navigation ko facilitate karta hai
    - System access provide karta hai
    - Application control manage karta hai
    """
    bank = BankSystem()
    
    while True:
        print("=" * 40)
        print("        BANK MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. Naya Account Banayein")
        print("2. Account Par Login Karein")
        print("3. Admin - Sab Audit Logs Dekhein")
        print("4. Admin - Audit Logs Clear Karein")
        print("5. Exit")
        print("=" * 40)
        
        choice = input("Apna choice daalo (1-5): ").strip()
        
        if choice == '1':
            create_account_cli(bank)
        elif choice == '2':
            login_to_account_cli(bank)
        elif choice == '3':
            admin_view_audit_logs_cli(bank)
        elif choice == '4':
            admin_clear_audit_logs_cli(bank)
        elif choice == '5':
            print("Hamare Bank Management System ka istemal karne ke liye dhanyavaad!")
            break
        else:
            print("Galat choice. Kripya fir se try karein.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main_menu_cli()