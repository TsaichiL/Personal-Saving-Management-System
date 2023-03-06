### project3-GroupL.py
# MIT License
# 
# Copyright (c) 2022 Andrei Ivlev, Animesh Gautam, Arundhati Pillay, Jiayi Yang, Tsaichi Lee
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



import pandas as pd
import numpy as np 

#create data-processing function to process original balance dataset downloaded from N26
class Process:
    def __init__(self):
        df = pd.read_csv('statement-2022-06.csv')
        df.columns = ['Description', 'Date', 'Amount']

        #select the rows that contain the previous balance information
        previous_balance = df.loc[df['Description']=='Previous balance']['Date']

        #select the rows that describe the outgoing transaction
        outgoing_transactions = df.loc[df['Description']=='Outgoing transactions']['Date']

        #select the rows that descirbe the incoming transaction
        incoming_transactions = df.loc[df['Description']=='Incoming transactions']['Date']

        #select the rows that show the current balance
        new_balance = df.loc[df['Description']=='Your new balance']['Date']

        #get the row index of previous balance
        row = df[df['Description'] == 'Previous balance'].index.tolist()[0]

        #filter out the rows contain useless information
        df = df.iloc[:row]

        #drop out none values
        df = df[df['Description'].notna()]
        df = df.reset_index(drop=True)
        df = df.replace('Booking Date', np.nan)

        #get the indexes of the rows that contain useful transaction information
        first_list = df.index[df['Date'].notna() == True].tolist()
        second_list = [x+1 for x in first_list]
        index_list = first_list + second_list
        index_list = sorted(index_list)
        df = df.iloc[index_list]
        df = df.reset_index(drop=True)

        #change the form to get the number itself
        df['Description'] = np.where((df['Date'].isna() == True) & (df['Description'].str.contains(" • ", case=False) == False),
                                     np.nan,
                                     df['Description'])
        df['Description'] = np.where(df['Description'].str.contains(" • ", case=False) == True,
                                     df['Description'].str.split(' • ').str[1],
                                     df['Description'])
        df['Description'] = df['Description'].fillna('Other')

        #select the rows that contain category information
        df['Category'] = np.where(df['Date'].isna() == False,
                                  df['Description'].shift(-1),
                                  np.nan)
        df = df[df['Category'].notna()]
        df = df.reset_index(drop=True)

        #get the number of spending in the numeric form instead of string
        df['Amount'] = df['Amount'].str.replace(',', '.')
        df['Amount'] = df['Amount'].str.replace('€', '')
        df['Amount'] = pd.to_numeric(df['Amount'],errors = 'coerce')
        df['Category'] = np.where(df['Amount'] > 0, 
                                     'Income', 
                                     df['Category'])

        #get the income seperately 
        self.l_income = list(df[df['Category'] == 'Income']['Amount'])

        #select only spendings but not income
        df_cat = df[['Category', 'Amount']]
        df_cat = df_cat[df_cat['Category'] != 'Income']
        df_cat['Amount'] = abs(df_cat['Amount'])
        self.expense = df_cat.groupby('Category')['Amount'].apply(list).to_dict()

class Budget(Process):
    def __init__(self):
        #self.expense = { 'Shopping' : [10,20], 'Other' : [30,40], 'Entertainment' : [50,60]}
        #self.l_income = [100,200,300]
        super().__init__()
        #get the total income and expense by suming they up and round them to 2 digits
        self.total_income = sum(self.l_income)
        self.total_income = round(self.total_income,2)
        self.total_expense = 0
        for x in self.expense.values():
            for y in x:
                self.total_expense += y
        self.total_expense = round(self.total_expense,2)

        #calculate the balance 
        self.balance = self.total_income - self.total_expense
        self.balance = round(self.balance,2)
    
    #create display function to show the result
    def display_income(self):
        print("\nTotal income: {}".format(self.total_income))
    
    def display_expense(self):
        print("\nTotal expenses: {}".format(self.total_expense))
    
    def user_balance(self):
        print("\nUser balance: {}".format(self.balance))
    
    #get a report of the total expense of different categories 
    def expense_distribution(self):
        for category,l in self.expense.items():
            cat_sum = 0 
            for i in l:
                cat_sum += i      
            print("\n{} : {} %".format(category, round((cat_sum / self.total_expense)*100,2)))

    #create a function to query the expense of a certain category
    def cat_expense(self):
        self.cat = {}
        for category,l in self.expense.items():
            cat_sum = 0 
            for i in l:
                cat_sum += i
            self.cat[category] = cat_sum
        cat_required = input('Please enter the category expense you want to query ')
        if cat_required in self.cat.keys():
            print(round(self.cat[cat_required],2))
        else:
            print('Sorry, there is no such category')

    #create the fucntion for users' saving plan in amount of money
    def savings_basic(self):
        #ask about the saving goal
        self.basic_goal = int(input('\nEnter amount you want to save over the next year: '))

        #calculate the saving goal per month
        self.basic_monthly_amount = self.basic_goal / 12

        #get the percentage that have to be saved from the income
        self.basic_percent = (self.basic_monthly_amount * 100) / self.total_income
        print("You must save {} {} of your income per month".format(round(self.basic_percent,2),'%'))
        print("i.e. {} / month".format(round(self.basic_monthly_amount,2)))

        #compare to see if the balance can meet the saving goal per month
        if(self.basic_monthly_amount > self.balance):
            print("Based on your balance, you need to reduce expenses or increase income to reach your savings goals")
        else:
            print("Based on your balance, you are on track to reach your savings goals")

    #create a function to make a saving plan based in percentage of income
    def savings_advanced(self):
        self.adv_percent = int(input('\nEnter % ' + 'of income you want to save: '))
        self.adv_monthly_amount = (self.adv_percent * self.total_income) / 100
        print("You must save {} / month".format(self.adv_monthly_amount))
        #compare to see if the balance can meet the saving goal per month
        if(self.adv_monthly_amount > self.balance):
            print("Based on your balance, you need to reduce expenses or increase income to reach your savings goals")
        else:
            print("Based on your balance, you are on track to reach your savings goals")

    #we also created functions for those who don't have a balance sheet and want to input income and expense manually
    '''
    def add_income(self):
        while True:
            income_amount = int(input('Enter income amount: '))
            self.l_income.append(income_amount)
            income_name = input('Enter source of income: ')
            self.l_income_name.append(income_name)
            result = input('Add income? (y/n): ')
            if result == 'n' or result == 'N':
                break
        self.total_income = sum(self.l_income)
        self.total_expense = sum(self.l_expense)
        self.balance = self.total_income - self.total_expense
    
    def add_expense(self):
        while True:
            expense_amount = int(input('Enter expense amount: '))
            self.l_expense.append(expense_amount)
            expense_name = input('Enter expense type: ')
            self.l_expense_name.append(expense_name)
            result = input('Add expense? (y/n): ')
            if result == 'n' or result =='N':
                break
        self.total_income = sum(self.l_income)
        self.total_expense = sum(self.l_expense)
        self.balance = self.total_income - self.total_expense
    
    def income_distribution(self):
        for i in range(len(self.l_income)):
            print("{} : {} %".format(self.l_income_name[i],round((self.l_income[i] / self.total_income)*100, 2)))
    '''
    
#the gate to call the function
if __name__ == '__main__':
    
    b = Budget()
    while True:
        #offers choices to get corresponding function
        print("1. Display total income")
        print("2. Display total expenses")
        print("3. Display user balance")
        print("4. Category wise distribution of expenses")
        print("5. Query the expense of a certain category")
        print("6. Savings suggestion")
        print("7. Monthly savings plan")
        choice = int(input("\nSelect option: "))
        #call the corresponding fucntion according to the request
        if choice == 1:
            b.display_income()
        elif choice == 2:
            b.display_expense()
        elif choice == 3:
            b.user_balance()
        elif choice == 4:
            b.expense_distribution()
        elif choice == 5:
            b.cat_expense()
        elif choice == 6:
            b.savings_basic()
        elif choice == 7:
            b.savings_advanced()

        print()
        x = input("\nDo you want to continue? (y/n)")
        if x == 'N' or x == 'n':
            break
