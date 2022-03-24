import mysql.connector as mycon
import datetime as dt
from tabulate import tabulate

mydb = mycon.connect(
    host='localhost',
    user='root',
    password='INCORRECT')

mycursor = mydb.cursor()
mycursor.execute('CREATE DATABASE IF NOT EXISTS LIBRARY')
mycursor.execute('USE LIBRARY')


def createTables():
    mycursor.execute('CREATE TABLE IF NOT EXISTS BOOKLIST(SRNO INT PRIMARY KEY,\
        BOOKNAME VARCHAR(50) NOT NULL,\
        AUTHOR VARCHAR(20) NOT NULL,\
        ISBN VARCHAR(13) NOT NULL,\
        COPIES INT NOT NULL DEFAULT 1)')

    mycursor.execute('CREATE TABLE IF NOT EXISTS LENDERS(SRNO INT PRIMARY KEY,\
        NAME VARCHAR(20) NOT NULL,\
        BOOKS_LENDED INT NOT NULL DEFAULT 0,\
        FINES INT NOT NULL DEFAULT 0)')

    mycursor.execute('CREATE TABLE IF NOT EXISTS LENDED(LEND_ID INT PRIMARY KEY,\
        BOOKNO INT NOT NULL,\
        LENDERNO INT NOT NULL,\
        LENDING_DATE DATE NOT NULL,\
        RETURN_DATE DATE NOT NULL,\
        FOREIGN KEY(BOOKNO) REFERENCES BOOKLIST(SRNO),\
        FOREIGN KEY(LENDERNO) REFERENCES LENDERS(SRNO))')
    mydb.commit()


def addBook():
    mycursor.execute('SELECT SRNO FROM BOOKLIST')
    res = mycursor.fetchall()
    if mycursor.rowcount == 0:
        srno = 0
    else:
        srno = res[-1][0]
    bookName = input("Enter Book Name :-")
    author = input('Enter Author Name :-')
    isbn = input('Enter ISBN of Book :-')
    copies = int(input('Enter No. of Copies :-'))
    mycursor.execute(
        f'INSERT INTO BOOKLIST VALUES({srno} + 1, "{bookName}", "{author}", "{isbn}", {copies})')
    mydb.commit()


def removeBook():
    srno = int(input('Enter Sr. No. to be deleted :-'))
    mycursor.execute(f'DELETE FROM BOOKLIST WHERE SRNO = {srno}')
    mydb.commit()


def modBook():
    srno = int(input('Enter Sr. No. of book to be updated :-'))
    print('1. Book Name\t2. Author')
    print('3. ISBN\t4. Copies')
    ch = int(input('What do you want to update ?'))
    if ch == 1:
        name = input('Enter New Book Name :-')
        mycursor.execute(
            f'UPDATE BOOKLIST SET BOOKNAME = "{name}" where SRNO = {srno}')
    elif ch == 2:
        name = input('Enter New Author Name :-')
        mycursor.execute(
            f'UPDATE BOOKLIST SET AUTHOR = "{name}" where SRNO = {srno}')
    elif ch == 3:
        isbn = input('Enter New ISBN :-')
        mycursor.execute(
            f'UPDATE BOOKLIST SET ISBN = "{isbn}" where SRNO = {srno}')
    elif ch == 4:
        copies = int(input('Enter New Number of Copies :-'))
        mycursor.execute(
            f'UPDATE BOOKLIST SET COPIES = {copies} where SRNO = {srno}')
    else:
        print('Invalid Choice!')
    mydb.commit()


def showBooks():
    mycursor.execute('SELECT * FROM BOOKLIST')
    res = mycursor.fetchall()
    print(tabulate(res, headers=[
          'Sr. No.', 'Book Name', 'Author', 'ISBN', 'No. Of Copies'], tablefmt='fancy_grid'))


def showLenders():
    mycursor.execute('SELECT * FROM LENDERS')
    res = mycursor.fetchall()
    print(tabulate(res, headers=[
          'Sr. No.', 'Name', 'Books Lended', 'Fine'], tablefmt='fancy_grid'))


def showLendDetails():
    mycursor.execute('SELECT LEND_ID, BOOKNO, BOOKNAME, LENDERNO, NAME, LENDING_DATE, RETURN_DATE FROM LENDERS, BOOKLIST, LENDED WHERE BOOKNO = BOOKLIST.SRNO AND LENDERNO = LENDERS.SRNO')
    res = mycursor.fetchall()
    if res == []:
        print('No Current Lendings!')
    else:
        print(tabulate(res, headers=['Lend ID', 'Book No.', 'Book Name', 'Lender No.',
              'Lender Name', 'Lending Date', 'Return Date'], tablefmt='fancy_grid'))


def addLender():
    mycursor.execute('SELECT SRNO FROM LENDERS')
    res = mycursor.fetchall()
    if mycursor.rowcount == 0:
        srno = 0
    else:
        srno = res[-1][0]
    name = input('Enter Your Name :-')
    mycursor.execute(
        f'INSERT INTO LENDERS(SRNO, NAME) VALUES({srno} + 1,"{name}")')
    mydb.commit()


def issueBook():
    lender = input('Enter your Name :-')
    mycursor.execute(f'SELECT SRNO FROM LENDERS WHERE NAME = "{lender}"')
    res = mycursor.fetchall()
    lender_no = res[0][0]
    mycursor.execute('SELECT SRNO, BOOKNAME, COPIES FROM BOOKLIST')
    res = mycursor.fetchall()
    print(tabulate(res, headers=['Sr. No.',
          'Book Name', 'Copies Left'], tablefmt='fancy_grid'))
    sr = int(input('Enter Sr. No. of Book you want to Issue :-'))
    for x in res:
        if sr == x[0]:
            if x[2] > 0:
                idate = input('Enter Issue Date (yyyy/mm/dd) :-')
                rdate = input('Enter Expected Return Date (yyyy/mm/dd) :-')
                mycursor.execute('SELECT LEND_ID FROM LENDED')
                res = mycursor.fetchall()
                if mycursor.rowcount == 0:
                    lend_id = 0
                else:
                    lend_id = res[-1][0]
                print('You Issued', x[1], 'successfully!')
                mycursor.execute(
                    f'UPDATE BOOKLIST SET COPIES = COPIES - 1 WHERE SRNO = {sr}')
                mycursor.execute(
                    f'INSERT INTO LENDED VALUES({lend_id} + 1, {sr}, {lender_no}, "{idate}", "{rdate}")')
                mycursor.execute(
                    f'UPDATE LENDERS SET BOOKS_LENDED = BOOKS_LENDED + 1 WHERE NAME = "{lender}"')
            else:
                print(
                    f'We Dont have enough Copies of "{x[1]}" available right now!')
    mydb.commit()


def returnBook():
    lName = input('Enter your Name :-')
    bName = input('Enter the name of Book you want to return :-')
    date = input('Enter Returning Date (yyyy/mm/dd) :-').split('/')
    date = dt.date(int(date[0]), int(date[1]), int(date[2]))
    mycursor.execute(
        f'UPDATE BOOKLIST SET COPIES = COPIES + 1 WHERE BOOKNAME = "{bName}"')
    mycursor.execute(
        f'UPDATE LENDERS SET BOOKS_LENDED = BOOKS_LENDED - 1 WHERE NAME = "{lName}"')
    mycursor.execute(f'SELECT SRNO FROM LENDERS WHERE NAME = "{lName}"')
    lSr = mycursor.fetchall()
    mycursor.execute(f'SELECT SRNO FROM BOOKLIST WHERE BOOKNAME = "{bName}"')
    bSr = mycursor.fetchall()
    mycursor.execute(
        f'SELECT EXTRACT(YEAR FROM RETURN_DATE),EXTRACT(MONTH FROM RETURN_DATE),EXTRACT(DAY FROM RETURN_DATE) FROM LENDED WHERE BOOKNO = {bSr[0][0]} AND LENDERNO = {lSr[0][0]}')
    diff = mycursor.fetchall()
    Diff = dt.date(diff[0][0], diff[0][1], diff[0][2])
    dateDiff = int((date - Diff).total_seconds()/86400)
    print(dateDiff)
    print(date)
    if dateDiff > 0:
        fine = dateDiff * 5
        mycursor.execute(
            f'UPDATE LENDERS SET FINES = {fine} WHERE SRNO = {lSr[0][0]}')
        print(
            f'You are charged a Fine of Rs. {fine} as you returned the book {dateDiff} days late.')
    else:
        print('Book returned successfully!')
    mycursor.execute(
        f'DELETE FROM LENDED WHERE BOOKNO = {bSr[0][0]} AND LENDERNO = {lSr[0][0]}')
    mydb.commit()


def payFine():
    name = input('Enter Your name :-')
    mycursor.execute(f'SELECT FINES FROM LENDERS WHERE NAME = "{name}"')
    fine = mycursor.fetchone()
    if fine[0] > 0:
        print(f'You need to pay Rs. {fine[0]} as Fine.')
        print('Do You Want To\n1. Pay Now\t2. Pay Later')
        print('*Note* :- You will be charged Rs. 10 extra if you choose to pay later!')
        ch = int(input('Enter Your Choice :-'))
        if ch == 1:
            mycursor.execute(
                f'UPDATE LENDERS SET FINES = 0 WHERE NAME = "{name}"')
        elif ch == 2:
            mycursor.execute(
                f'UPDATE LENDERS SET FINES = FINES + 10 WHERE NAME = "{name}"')
        else:
            print('Invalid input!')
    else:
        print('You dont have any pending Fines!')
    mydb.commit()


def librarianMenu():
    while True:
        print('='*25, 'WELCOME TO LIBRARY', '='*25)
        print('\t\t\t1. ADD BOOK')
        print('\t\t\t2. REMOVE BOOK')
        print('\t\t\t3. MODIFY BOOK DETAILS')
        print('\t\t\t4. SHOW BOOKS')
        print('\t\t\t5. ADD LENDER')
        print('\t\t\t6. SHOW LENDERS')
        print('\t\t\t7. SHOW LENDING DETAILS')
        print('\t\t\t8. EXIT')
        print('='*70)
        ch = int(input('Enter your Choice:- '))
        if ch == 1:
            addBook()
        elif ch == 2:
            removeBook()
        elif ch == 3:
            modBook()
        elif ch == 4:
            showBooks()
        elif ch == 5:
            addLender()
        elif ch == 6:
            showLenders()
        elif ch == 7:
            showLendDetails()
        elif ch == 8:
            break
        else:
            print('Invalid Input! Please Enter a correct choice.')


def lenderMenu():
    while True:
        print('='*25, 'WELCOME TO LIBRARY', '='*25)
        print('\t\t\t1. ISSUE A BOOK')
        print('\t\t\t2. RETURN A BOOK')
        print('\t\t\t3. SHOW BOOKS')
        print('\t\t\t4. PAY FINE')
        print('\t\t\t5. EXIT')
        print('='*70)
        ch = int(input('Enter Your Choice:-'))
        if ch == 1:
            issueBook()
        elif ch == 2:
            returnBook()
        elif ch == 3:
            showBooks()
        elif ch == 4:
            payFine()
        elif ch == 5:
            break
        else:
            print('Invalid Input! Please Enter a correct choice.')


def menu():
    createTables()
    while True:
        print('='*25, 'WELCOME TO LIBRARY', '='*25)
        print('\t\t\t1. LOGIN AS LIBRARIAN')
        print('\t\t\t2. LOGIN AS LENDER')
        print('\t\t\t3. EXIT')
        print('='*70)
        ch = int(input('Enter Your Choice:-'))
        if ch == 1:
            librarianMenu()
        elif ch == 2:
            lenderMenu()
        elif ch == 3:
            break
        else:
            print('Invalid Input! Please Enter a correct choice.')


menu()
