import pandas as pd
import numpy
import itertools as it
import tkinter as tk
LARGE_FONT = ('Verdana', 24)
from tkinter import messagebox
import tkinter.ttk as ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_pdf import PdfPages
from pylab import *
from PIL import Image, ImageTk
from tkinter import filedialog
import time
import datetime

### Used in Capital Gains Audit
from datetime import datetime
from dateutil.relativedelta import relativedelta

""" Overall Ideas::
1. Add in Performance net of Fees program to adjust returns based on value of portfolio.
2. Produce ReportGenerator output in Tkinter window. Allow for a save button.
3. Print out all input information into a window that allows the user to confirm if the info is correct
   A. Eventually make it a one page window that will allow you to dynamically change info without having to go through all the steps.
4. Make program into .exe file.
5. Make it a web application.
6. Put Tkinter in it's own class to organize code.
7. Allow input of state and gross income to create a dynamic income tax rate.
8. Savings account is currently only allowed 1 account. Probably should allow for more than one savings accounts.
9. Make a single GUI that contains buttons for every input section. Once Submit is clicked it still remains open. Then a button when clicked shows the report that was run in a new window with a save button.
   Maybe hide buttons when information is not clicked yet (i.e. no names input yet, so button that allows age input is not available. This will allow for easier UI that can be dynamically changed (ie switching between 1 year til retirmenent and 7
   will be much easier. Submit could always be find best portfolio, or create a second custom portfolio draw order option. radio buttons that allow user to select number.
10.Make a BWM Command Center GUI. This portfolio Projection will be one component of the command center. Another could be calculate avg.fee. Third could be the quarterly fee trade generator. Just requires specific input. Could come up with many options
11.Add in a Social Security calculator for income."""

""" Simulator improvement:
1. Allow for entry of pension information."""

"""2/13/2017 - 2/17/2017 All input sections complete in the GUI. Now I need to create the modeling into a Class that is evaluated in the background.
 After that I will create a tkinter that shows the matplotlib plots and information. I will add a save file button. The save file should save
 the following: csv for DataFrame values, and a pdf of the output."""

"""2/17/2017 GUI is producing the correct output and creating the correct dataFrame. Next step is to add in all models for performance. Maybe only grab the ones
that go back far enough and then adjust the radiobutton options accordingly. Next major process will be to create the simulator into a class. Cleanup the input it needs
and then go through every step to correct the variables it will need.
1. Add in models for performance into Returns csv.
2. Adjust radio buttons to match available models.
3. Make the simulator a class.
4. Clean up simulator input requirements.
5. Replace all areas that need new variables."""

"""2/21/2017 Model simulator is now a class. The findbestportfolio is now a function of that class. First run with my personal information worked. Need to audit this with Tillman data. Allow for the
pension section to be available or else numbers won't match. Once I make sure it is producing good information I can move onto the report class, with the hopes of having it show in a GUI."""

"""2/27/2017 I've finished the initial information page. I am able to grab all variables needed for the model now. To allow for the variables to be used throughout the program I had to create a dictionary in the
BWMCommandCenterApp() class tying it to the controller that is passed to all classes. The input page can still be improved to allow better useability, but for now it works. Next step is to create the run projection
page that will show a printout of all information that was input. Then the user will have the option to run the report. I'd like to have a pop-up that shows how close it is to being complete. One it finishes it will take you
directly to the graphs page, which will be updated upon completion. """

"""2/28/2017 I've ccnnected the input to the model. I skipped making a detailed information review page. This is something I can complete once the first pass of the program is complete. The next and final step for the functionality will
be to update the graphs from the model. Once this is complete I can make it into a .exe file to see if it works. """

"""3/1/2017 Everything is complete for the first go at the program. Before going live I will need to test the results to make sure they are correct. Now it's time to make it a .exe"""

"""3/2/2017-3/14/2017 Created the .exe and took a break from the project to focus on investment research."""

"""3/15/2017 I've made some minor edits to various text in the program. I added the final value annotations to the total portfolio and individual account graphs.
This will make it easier to read the number on the graph. I created new returns using an NYU spreadsheet tracking the historical performance of the S&P500
and the 10 year TBill. These are used to create various stock/bond portfolios. These are the furthest stretching returns I could find. Finally I've added in
the initial functionality for contributions. I will need to improve these so that they stop when you retire, and they also account for inocme issues with IRA
contributions."""


class dataframeCreation():
    def __init__(self):
        self.df = pd.read_csv('StockBondPerformance.csv')
        self.returns = [x for x in self.df.columns if x != 'Year']
        self.dfValuesOrig = pd.DataFrame(self.df['Year'])
        self.dfValuesOrig.fillna(0,inplace=True)
        self.dfReturns = self.df[self.returns].copy() # Original Return information
        #self.dfReturns = self.df[['TE Select','NS ML']].copy() # SP500 returns. NS ML is equal to 0.
        self.dfReturns['Cash'] = 0
        self.RMDValues = pd.read_csv('UniformLifeRMD.csv')

class projection(tk.Frame,dataframeCreation):
    def __init__(self, controller):
        self.controller = controller
        self.sharedVariables = controller.shared_data
        dataframeCreation.__init__(self)
        # Create models dictionary that contains all information for the accounts
        print(self.sharedVariables['accountOwners'])
        index = 0
        for owner in self.sharedVariables['accountOwners']:
            if owner == self.sharedVariables['name1']:
                self.sharedVariables['accountOwners'][index] = '0'
            elif owner == self.sharedVariables['name2']:
                self.sharedVariables['accountOwners'][index] = '1'
            elif owner == 'Both':
                self.sharedVariables['accountOwners'][index] = 'B'
            else:
                print('there was an issue with giving values to the owners.')
            index += 1
        print(self.sharedVariables['accountOwners'])

        self.models = dict()
        whatAccount = 0
        for name in self.sharedVariables['listOfAccounts']:
            self.models[name] = dict()
            self.models[name]['Owner'] = self.sharedVariables['accountOwners'][whatAccount]
            self.models[name]['Type'] = self.sharedVariables['accountTypes'][whatAccount]
            self.models[name]['Model'] = self.sharedVariables['accountModels'][whatAccount]
            self.models[name]['Value'] = self.sharedVariables['accountValues'][whatAccount]
            self.models[name]['Contrib'] = self.sharedVariables['contribValues'][whatAccount]
            whatAccount += 1



        # Create the starting values for the dataframe for each account.
        for name in self.sharedVariables['listOfAccounts']:
            self.dfValuesOrig.loc[0,name] = self.models[name]['Value']
        self.dfValuesOrig.fillna(0,inplace=True)

        self.modelComboList = [x for x in list(self.models.keys()) if self.models[x]['Type'] != 'Savings Account']
        try:
            self.savingsAccount = [x for x in list(self.models.keys()) if self.models[x]['Type'] == 'Savings Account'][0]
        except:
            self.savingsAccount = ''
        accountPermutations = 0
        for account in self.modelComboList:
            accountPermutations += 1

        self.accountCombos = list(it.permutations(self.modelComboList,accountPermutations))
        print(self.models)

    def getReturns(self, accountCom):
        ## acccount Com is the order of accounts that will be drawn from. This allows the iteration to find the best portfolio. For single use cases you can use self.modelComboList
        accountCom = accountCom
        savingsAccount = self.savingsAccount
        yearsTilRetirementCountdown = 0
        self.dfValues = self.dfValuesOrig.copy()
        l = len(self.dfValues.index.values)

        p1Age = self.sharedVariables['age1'] + 1
        p2Age = self.sharedVariables['age2']
        if self.sharedVariables['isCouple'] == 'Yes':
            p2Age = self.sharedVariables['age2'] + 1
        p1RMD = [0]
        p2RMD = [0]

        age1List = [self.sharedVariables['age1']]
        if self.sharedVariables['isCouple'] == 'Yes':
            age2List = [self.sharedVariables['age2']]

        self.dfReturns.to_csv('ReturnsUsed.csv', index = False)

        YearsInflation = 0
        accountNum = 0
        cashNeededList = [0]

        if min(self.sharedVariables['yearsTilRetirement']) > l-1:
            for i in range(1,l):
                cashNeededList.append(0)
        else:
            for i in range(0,min(self.sharedVariables['yearsTilRetirement'])):
                cashNeededList.append(0)

        """Yearly expenses are paid with money earned previous year. Therefore accounts will be reduced at beginning of year
        This will result in the final year showing a positive cash amount from the pension due to the fact that the pension is earned
        at the end of year, not beginning when expenses are need."""

        for i in range(1,l):
            yearsRMDInformation = self.rmdCalculation(p1Age,p2Age,i)
            p1RMDAfterTax = yearsRMDInformation['afterTaxRMDP1']
            p1RMD.append(yearsRMDInformation['rmdP1'])
            print('years RMD Information {}'.format(yearsRMDInformation))
            print('P1 RMD {}'.format(p1RMDAfterTax))
            if self.sharedVariables['isCouple'] == 'Yes':
                p2RMD.append(yearsRMDInformation['rmdP2'])
                p2RMDAfterTax = yearsRMDInformation['afterTaxRMDP2']
                print('P2 RMD {}'.format(p2RMD))
            if yearsTilRetirementCountdown >= min(self.sharedVariables['yearsTilRetirement']):
                cashNeeded = self.sharedVariables['cashNeededStart'] * (1 + self.sharedVariables['inflation'])**YearsInflation
                cashNeededList.append(cashNeeded)
                cashNeeded = cashNeeded - p1RMDAfterTax
                if self.sharedVariables['isCouple'] == 'Yes':
                    cashNeeded = cashNeeded - p2RMDAfterTax
                if savingsAccount == '':
                    SavingsAccount = 0
                else:
                    SavingsAccount = self.dfValues.loc[i-1, savingsAccount]
                if cashNeeded > 0:
                    if SavingsAccount > cashNeeded:
                        self.dfValues.loc[i-1, savingsAccount] = self.dfValues.loc[i-1, savingsAccount] - cashNeeded
                        cashNeeded = 0.0

                    elif (SavingsAccount > 0.0) and (SavingsAccount < cashNeeded):
                        cashNeeded -= SavingsAccount
                        self.dfValues.loc[i-1, savingsAccount] = 0
                        cashNeeded, accountNum = self.subtractCash(i, cashNeeded, accountNum, accountCom, p1Age, p2Age)

                    else:
                        cashNeeded, accountNum = self.subtractCash(i, cashNeeded, accountNum, accountCom, p1Age, p2Age)
            for column in self.dfValues:
                if column != 'Year':
                    if self.models[column]['Model'] != 'Cash':
                        print('{} contribution is {}'.format(column, self.models[column]['Contrib']))
                        self.dfValues.loc[i,column] = self.dfValues.loc[i-1,column] * (1 + self.dfReturns.loc[i,self.models[column]['Model']]/100) + self.models[column]['Contrib']

                    else:

                        """  Pension information that I can add into the GUI. """
                        '''
                        if p2Age > 64:
                            pension = 17616
                            self.dfValues.loc[i,savingsAccount] = self.dfValues.loc[i-1,savingsAccount] * (1 + self.dfReturns.loc[i,self.models[savingsAccount]['Model']]/100) + pension
                        else:
                            self.dfValues.loc[i,savingsAccount] = self.dfValues.loc[i-1,savingsAccount] * (1 + self.dfReturns.loc[i,self.models[savingsAccount]['Model']]/100)'''
                else:
                    pass
            yearsTilRetirementCountdown += 1
            age1List.append(p1Age)
            p1Age += 1

            if self.sharedVariables['isCouple'] == 'Yes':
                age2List.append(p2Age)
                p2Age += 1
            YearsInflation += 1

        preTaxPortValue = []
        afterTaxPortValue = []
        for i in range(0,l):
            afterTax = 0
            for column in self.dfValues:
                if column != 'Year':
                    multiplier = self.taxMultiplier(column, p1Age, p2Age)
                    afterTax = afterTax + self.dfValues.loc[i,column] * multiplier
            afterTaxPortValue.append(afterTax)
            preTaxPortValue.append(self.dfValues.loc[i][1:].sum())

        endAfterTaxPortValue = afterTaxPortValue[-1]
        endPreTaxPortValue = preTaxPortValue[-1]
        self.endPortValue = [endPreTaxPortValue,endAfterTaxPortValue,accountCom]

        print('CashNeeded lsit {}'.format(len(cashNeededList)))
        self.dfValues['CashNeeded'] = cashNeededList
        self.dfValues['{}TotalRMD'.format(self.sharedVariables['name1'])] = p1RMD
        self.dfValues['{}AfterTaxRMD'.format(self.sharedVariables['name1'])] = self.dfValues['{}TotalRMD'.format(self.sharedVariables['name1'])] * (1 - self.sharedVariables['incomeTaxRate'])
        self.dfValues['BeforeTaxPortValue'] = preTaxPortValue
        self.dfValues['AfterTaxPortValue'] = afterTaxPortValue
        self.dfValues['{}\'s Age'.format(self.sharedVariables['name1'])] = age1List
        if self.sharedVariables['isCouple'] == 'Yes':
            self.dfValues['{}\'s Age'.format(self.sharedVariables['name2'])] = age2List
            self.dfValues['{}TotalRMD'.format(self.sharedVariables['name2'])] = p2RMD
            self.dfValues['{}AfterTaxRMD'.format(self.sharedVariables['name2'])] = self.dfValues['{}TotalRMD'.format(self.sharedVariables['name2'])] * (1 - self.sharedVariables['incomeTaxRate'])






        self.sharedVariables['dfValues'] = self.dfValues
        self.sharedVariables['dfReturns'] = self.dfReturns
        print('age {}'.format(p1Age))
        return self.dfValues.copy(), self.dfReturns.copy(), self.endPortValue

    def taxMultiplier(self,nameOfAccount, age1, age2):
        owner = self.models[nameOfAccount]['Owner']
        type = self.models[nameOfAccount]['Type']
        try:
            owner = int(owner)
            if owner == 0:
                age = age1
            else:
                age = age2
        except:
            owner = owner
        if type == 'Tax-Deferred IRA/401k':
            if owner != 'B':
                if age < 60:
                    multiplier = 1 - self.sharedVariables['incomeTaxRate'] - .1  #10% early withdrawal fee calculation.
                else:
                    multiplier = 1 - self.sharedVariables['incomeTaxRate']
        elif type == 'After-Tax IRA/401k':
            if age < 60:
                multiplier = 1 - .1 #10% early withdrawal penalty. Doesn't add in income taxes on gains. Need to figure out best way to do that.
            else:
                multiplier = 1
        elif type == 'Taxable':
            multiplier = 1 - self.sharedVariables['capitalGainsTaxRate']
        else:
            multiplier = 1
        return multiplier

    def getRMDValues(self,yearsTilRMD, returnLength):
        values = [0]
        if yearsTilRMD > returnLength:
            for i in range(0,returnLength):
                values.append(0)
        else:
            for i in range(0,yearsTilRMD):
                values.append(0)
        return values

    def rmdCalculation(self,age1,age2,iterator):
        rmdP1 = 0
        rmdP2 = 0
        afterTaxRMDP1 = 0
        afterTaxRMDP2 = 0
        for account in self.models:
            if self.models[account]['Owner'] == '0' and self.models[account]['Type'] == 'Tax-Deferred IRA/401k' and age1 > 70:
                print('RMD information: Iteration {}, Age {}, account {}, owner {}'.format(iterator, age1, account, self.models[account]['Owner']))
                p1AccountRMD = self.dfValues.loc[iterator-1,account] / self.RMDValues[self.RMDValues['Age']==age1].iloc[0]['Distribution Period']
                self.dfValues.loc[iterator-1,account] = self.dfValues.loc[iterator-1,account] - p1AccountRMD
                rmdP1 += p1AccountRMD
            elif self.models[account]['Owner'] == '1' and self.models[account]['Type'] == 'Tax-Deferred IRA/401k' and age2 > 70:
                print('RMD information: Iteration {}, Age {}, account {}, owner {}'.format(iterator, age2, account, self.models[account]['Owner']))
                p2AccountRMD = self.dfValues.loc[iterator-1,account] / self.RMDValues[self.RMDValues['Age']==age2].iloc[0]['Distribution Period']
                self.dfValues.loc[iterator-1,account] = self.dfValues.loc[iterator-1,account] - p2AccountRMD
                rmdP2 += p2AccountRMD
            else:
                pass
        print('afterTax RMD P2 {}'.format(afterTaxRMDP2))
        afterTaxRMDP1 = rmdP1 * (1 - self.sharedVariables['incomeTaxRate'])
        afterTaxRMDP2 = rmdP2 * (1 - self.sharedVariables['incomeTaxRate'])
        print('afterTax RMD P2 {}'.format(afterTaxRMDP2))
        return {'rmdP1': rmdP1, 'rmdP2': rmdP2, 'afterTaxRMDP1': afterTaxRMDP1, 'afterTaxRMDP2': afterTaxRMDP2}


    ### Cash Subtraction Function

    def subtractCash(self,iterator,cashNeeded, accountNum, accountCom, age1, age2):
        while cashNeeded > 0:
            print(accountCom[0])
            try:
                afterTaxMultiplier = self.taxMultiplier(accountCom[accountNum], age1, age2)
            except:
                if cashNeeded > self.dfValues.loc[iterator-1, [x for x in list(accountCom)]].sum()*.7:
                    print('''Bankrupt1! Cash needed is = {}\nYou can\'t cover living expenses.\nRemaining balance not adjusted for taxes = {}'''.format(
                    cashNeeded,self.dfValues.loc[iterator-1,[x for x in list(self.models.keys())]].sum()))
                    for account in list(accountCom):
                        self.dfValues.loc[iterator-1, account] = 0
                        accountNum = 0
                        afterTaxMultiplier = self.taxMultiplier(accountCom[accountNum], age1, age2)
                    break
                else:
                    accountNum = 0
                    afterTaxMultiplier = self.taxMultiplier(accountCom[accountNum], age1, age2)
            print(accountNum)
            AccountToPullFrom = self.dfValues.loc[iterator-1,accountCom[accountNum]]
            print('Account Being pulled from {}'.format(accountCom[accountNum]))
            cashNeeded = cashNeeded / afterTaxMultiplier

            print('Account to pull form {}'.format(AccountToPullFrom))
            if AccountToPullFrom > cashNeeded:
                self.dfValues.loc[iterator-1, accountCom[accountNum]] = self.dfValues.loc[iterator-1, accountCom[accountNum]] - cashNeeded
                cashNeeded = 0

            elif (AccountToPullFrom > 0) and (AccountToPullFrom < cashNeeded):
                self.dfValues.loc[iterator-1, accountCom[accountNum]] = 0
                cashNeeded -= AccountToPullFrom

                cashNeeded = cashNeeded * afterTaxMultiplier

                accountNum += 1

                if cashNeeded > self.dfValues.loc[iterator-1, [x for x in list(accountCom)]].sum()*.7:
                    print('''Bankrupt! Cash needed is = {}\nYou can\'t cover living expenses.\nRemaining balance not adjusted for taxes = {}'''.format(
                        cashNeeded,self.dfValues.loc[iterator-1,[x for x in list(self.models.keys())]].sum()))
                    for account in list(accountCom):
                        self.dfValues.loc[iterator-1, account] = 0
                        accountNum = 0
                        afterTaxMultiplier = self.taxMultiplier(accountCom[accountNum], age1, age2)
                    break
            elif AccountToPullFrom == 0:
                accountNum += 1
            else:
                print('Something Wrong Happened')
                break
        return cashNeeded, accountNum


    def findBestPort(self):
        self.finalPreTaxPortValue = []
        self.finalAfterTaxPortValue = []
        self.finalBestAccountCombo = []
        for accountGroup in self.accountCombos:
            print('Group of account {}'.format(accountGroup))
            portfolioCalculation = self.getReturns(accountGroup)
            print(portfolioCalculation[2])
            print('-'*50)
            self.finalPreTaxPortValue.append(portfolioCalculation[2][0])
            self.finalAfterTaxPortValue.append(portfolioCalculation[2][1])
            self.finalBestAccountCombo.append(portfolioCalculation[2][2])
        return(self.finalPreTaxPortValue,self.finalAfterTaxPortValue,self.finalBestAccountCombo)

class projectionReport(tk.Frame):

    def __init__(self, controller):
        self.controller = controller
        inputDataFrame = self.controller.shared_data['dfValues']
        incomeTaxRate = self.controller.shared_data['incomeTaxRate']
        capitalGainsRate = self.controller.shared_data['capitalGainsTaxRate']
        inflationRate = self.controller.shared_data['inflation']
        figures = [None,None,None,None]
        xLength = len(inputDataFrame.index.values)
        rmdColumnNames = []
        for columnName in inputDataFrame.columns.values:
            if 'TotalRMD' in columnName:
                rmdColumnNames.append(columnName)
        inputDataFrame['RMD%OfPort'] = inputDataFrame[rmdColumnNames].sum()/inputDataFrame['BeforeTaxPortValue']


        accountNames = []
        for columnName in inputDataFrame.columns[1:]:
            if columnName != 'CashNeeded':
                accountNames.append(columnName)
            else:
                break


        inputDataFrame['Draw%OfPort'] = inputDataFrame['CashNeeded']/inputDataFrame['AfterTaxPortValue'] * 100


        textFields = dict()
        textFields['Income Tax Rate'] = str(incomeTaxRate * 100) + '%'
        textFields['Capital Gains Rate'] = str(capitalGainsRate * 100) + '%'
        textFields['Inflation'] = str(inflationRate * 100) + '%'
        textFields['Final Account Values'] = dict()
        for account in accountNames:
            textFields['Final Account Values'][account] = '${:,}'.format(int(round(inputDataFrame[account].tail(1),0)))
        textFields['Final Account Values']['After Tax PortfolioValue'] = '${:,}'.format(int(round(inputDataFrame['AfterTaxPortValue'].tail(1),0)))
        textFields['Final Account Values']['Before Tax PortfolioValue'] = '${:,}'.format(int(round(inputDataFrame['BeforeTaxPortValue'].tail(1),0)))

        """ Plot 1. Total account Value with % Draw barchart in background"""
        self.fig1, ax1 = plt.subplots()
        plt.tight_layout(pad=5)
        ax2 = ax1.twinx()
        ax1.plot(inputDataFrame.index.values,inputDataFrame['AfterTaxPortValue'],lw = 5)
        yValue = int(textFields['Final Account Values']['After Tax PortfolioValue'].replace("$","").replace(',',''))
        print("x {}, y {}".format(xLength, yValue))
        ax1.annotate('${:,}'.format(yValue), xy = (xLength, yValue), textcoords='data', xytext = (xLength - 12, yValue))
        ax1.get_yaxis().get_major_formatter().set_scientific(False)
        ax1.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        ax2.bar(inputDataFrame.index.values,inputDataFrame['Draw%OfPort'],alpha = .5,color='gold')

        """ Find a better way to create ylims"""
        #ax1.set_ylim([0,6000000])
        #ax2.set_ylim([0,10])

        plt.title('Total Portfolio Value')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total After-Tax Value of Portfolio ($\'s)')
        ax2.set_ylabel('% of Portfolio (After-tax) Needed For Draw (in %)',rotation=270,labelpad=15)
        ax2.grid('off')
        self.controller.shared_data['fig1'] = self.fig1
        figures[0] = self.fig1


        """ Plot 2. Individual account Value Line Graphs"""
        self.fig2, ax1 = plt.subplots()
        plt.tight_layout(pad=5)
        for account in accountNames:
            ax1.plot(inputDataFrame[account],label=account + '-' + '{}'.format(textFields['Final Account Values'][account]),lw = 5)
        plt.xlabel('Year')

        """ Find a better way to create ylim"""
        #ax1.set_ylim([0,7000000])

        plt.ylabel('Pre-Tax Account Value ($\'s)')
        plt.legend(loc='upper left',fontsize = 8,framealpha = .5,frameon = False)
        plt.title('Individual Account Values')
        ax1.get_yaxis().get_major_formatter().set_scientific(False)
        ax1.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        self.controller.shared_data['fig2'] = self.fig2
        figures[1] = self.fig2

        """ Plot 3. Bar chart showing the growth in cash needed per year."""
        self.fig3, ax1 = plt.subplots()
        plt.tight_layout(pad=5)
        plt.bar(inputDataFrame.index.values,inputDataFrame['CashNeeded'])
        plt.title('Inflation Adjusted Cash Needed for Living Expenses')
        plt.xlabel('Year')
        plt.ylabel('Cash Needed for Living Expenses ($\'s)')
        ax1.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        self.controller.shared_data['fig3'] = self.fig3
        figures[2] = self.fig3

        """ Plot 4. Information Page"""
        self.fig4, ax1 = plt.subplots()
        plt.text(0,1,'Assumptions:',fontsize = 25)
        plt.text(0,.95,'Capital Gains Rate' + ' - ' + str(textFields['Capital Gains Rate']))
        plt.text(0,.9,'Income Tax Rate' + ' - ' + str(textFields['Income Tax Rate']))
        plt.text(0,.85,'Inflation Rate' + ' - ' + str(textFields['Inflation']))
        plt.text(0,.75,'Final Account Values:',fontsize = 25)
        total = .70
        for i in textFields['Final Account Values']:
            if i != 'After Tax Portfolio Value':
                plt.text(0, total,i + ' - ' + textFields['Final Account Values'][i])
                total -= .05
        plt.text(0, total,'After Tax Portfolio Value' + ' - ' + textFields['Final Account Values']['After Tax PortfolioValue'])
        plt.text(0, total-.05,'Before Tax Portfolio Value' + ' - ' + textFields['Final Account Values']['Before Tax PortfolioValue'])

        """ Need to figure out a better way to create the order of acoounts to draw from, so that it is clear and concise."""
        #plt.text(0, total - .10, 'Order of Accounts to Draw From:', fontsize = 25)
        #plt.text(0, total - .15, PortFirstHalf)
        #plt.text(0, total - .20, PortSecondHalf)
        #plt.text(0, total - .25, 'After Tax Savings - ${}'.format(int(bestpost-worstpost)))
        plt.grid(False)
        plt.axis('off')
        self.controller.shared_data['fig4'] = self.fig4
        figures[3] = self.fig4
        self.controller.shared_data['figurelist'] = figures


        print('this {}'.format(self.controller.shared_data['figurelist']))
        controller.show_frame(GraphPageHome)

def runModel(controller):
    start = time.time()
    new = projection(controller = controller)

    preValue, postValue, bestCombo = new.findBestPort()

    bestpre = max(preValue)
    worstpre = min(preValue)
    print('The best pretax value is {} and the worst is {} a difference of {}\nthe distribution order is {}'.format(
        bestpre,worstpre,bestpre-worstpre,new.accountCombos[preValue.index(bestpre)]))

    bestpost = max(postValue)
    worstpost = min(postValue)
    print('The best aftertax value is {} and the worst is {} a difference of {}\nthe distribution order is {}'.format(
        bestpost,worstpost,bestpost-worstpost,new.accountCombos[postValue.index(bestpost)]))

    best = new.getReturns(new.accountCombos[postValue.index(bestpost)])[0]
    best.to_csv('dfValues.csv',index=False)
    graphs = projectionReport(new.controller)

    end = time.time()
    print('How long runModel takes {}'.format(end-start))


def Review(controller):
    '''review.wm_title("Information Review")
    reviewWindow = tk.Text(review, width=100, height=30)
    reviewWindow.grid(row=0, columnspan=2)
    row = 1.5
    for i in controller.shared_data:
        print(row)
        reviewWindow.insert(tk.END,'{}\n'.format(i))
        row+=1
    confirmButton = ttk.Button(review, text='Confirm',command= runModel(controller=controller))
    confirmButton.grid(row=1,column=0)
    denyButton = ttk.Button(review, text='Deny', command=lambda: print('Nope'))
    denyButton.grid(row=1,column=1)
    review.geometry("500x500")'''
    runModelConfirm = messagebox.askyesno('Run Report',"Would you like to run the report?\nFYI, the more accounts there are the longer the program takes to run.")
    if runModelConfirm == True:
        runModel(controller=controller)
    else:
        pass
        #messagebox.showwarning("Error", "There was an issue running the model.\nPlease double-check you're information.\nMake sure everthing is filled out.")




class BWMCommandCenterApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.shared_data = {

            'isCouple' : None,
            'cashNeededStart' : None,
            'howManyAccounts' : None,
            'yearsTilRetirement' : [],
            'inflation' : None,
            'incomeTaxRate' : 0,
            'capitalGainsTaxRate' : 0,
            'name1' : None,
            'age1' : None,
            'name2' : None,
            'age2' : None,
            'names' : [],
            'ages' : [],
            'fig1' : Figure(),
            'fig2' : Figure(),
            'fig3' : Figure(),
            'fig4' : Figure(),
            'figurelist' : [],
            'accountOwners' : [],
            'listOfAccounts' : [],
            'accountModels' : [],
            'accountTypes' : [],
            'accountValues' : [],
            'contribValues' : [],
            'finalPreTaxPort' : [],
            'finalAfterTaxPortValue' : [],
            'finalBestAccountCombo' : [],
            'dfValues' : None,
            'dfReturns' : None,
            'endPortValue' : None,

        }

        self.shared_graphs = {
            'graph1' : None,
            'graph2' : None,
            'graph3' : None,
            'graph4' : None
        }

        tk.Tk.iconbitmap(self, default='BWMIcon.ico')
        tk.Tk.wm_title(self, "BWM Command Center")
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        # All pages need to be listed here
        for F in (StartPage, GraphPageHome, InitialInfoInput, QuarterlyBilling, CapitalGainsAudit): # Need to add ReviewPage back in once I complete it.

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)


    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


    def createReview(self):
        textWindow = tk.Text(self, width = 100, height = 100)
        line = 1.0
        print(self.shared_data)
        try:
            textWindow.insert(str(line), self.shared_data['name1'])
            textWindow.update()
            textWindow.grid(row=1,column=1)
        except:
            pass
        return textWindow

class StartPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        photo = Image.open("StartPageBackground.jpg")
        self.background_image = ImageTk.PhotoImage(photo)
        background_label = tk.Label(self, image=self.background_image)
        background_label.image = photo
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #label = ttk.Label(self, text = 'BWM Command Center', font=LARGE_FONT)
        #label.place(x = -300, y = 0, relwidth = 1, relx = .6)

        button1Frame = tk.Frame(self, width = 150, height = 150)
        button1 = tk.Button(button1Frame, text='Graphs',
                            command = lambda:controller.show_frame(GraphPageHome), width = 34, bg = '#c1bb64', relief = tk.GROOVE)
        button1Frame.grid_propagate(False)
        button1Frame.columnconfigure(0, weight = 1)
        button1Frame.rowconfigure(0, weight =1)
        button1Frame.place(x=-350,y=125, relx = .5, relheight = .2)
        button1.grid(sticky='wens')

        button2Frame = tk.Frame(self, width = 150, height = 150)
        button2 = tk.Button(button2Frame, text='Information Input',
                            command = lambda: controller.show_frame(InitialInfoInput), bg = '#0b0ea3', foreground = 'white', relief = tk.GROOVE)
        button2Frame.grid_propagate(False)
        button2Frame.columnconfigure(0, weight = 1)
        button2Frame.rowconfigure(0, weight =1)
        button2Frame.place(x=-200,y=125, relx = .5, relheight = .2)
        button2.grid(sticky='wens')

        button3Frame = tk.Frame(self, width = 150, height = 150)
        button3 = tk.Button(button3Frame, text='Quarterly Billing',
                            command = lambda: controller.show_frame(QuarterlyBilling), bg = '#0b0ea3', foreground = 'white', relief = tk.GROOVE)
        button3Frame.grid_propagate(False)
        button3Frame.columnconfigure(0, weight = 1)
        button3Frame.rowconfigure(0, weight = 1)
        button3Frame.place(x=-350, y = 0, relx = .5, relheight = .2)
        button3.grid(sticky='wens')

        button4Frame = tk.Frame(self, width = 150, height = 150)
        button4 = tk.Button(button4Frame, text='Capital Gains',
                            command = lambda: controller.show_frame(CapitalGainsAudit), bg = '#c1bb64', foreground = 'white', relief = tk.GROOVE)
        button4Frame.grid_propagate(False)
        button4Frame.columnconfigure(0, weight = 1)
        button4Frame.rowconfigure(0, weight = 1)
        button4Frame.place(x=-200, y = 0, relx = .5, relheight = .2)
        button4.grid(sticky='wens')

class GraphPageHome(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text = 'Portfolio Graphs', font=LARGE_FONT)
        label.place(x = 0, y = 0, relwidth = 1, relx = .4)

        def graph1():
            graph(self.controller.shared_data['fig1'])

        def graph2():
            graph(self.controller.shared_data['fig2'])

        def graph3():
            graph(self.controller.shared_data['fig3'])

        def graph4():
            graph(self.controller.shared_data['fig4'])

        def graph(figure):
            lengthOfRefresh = len(self.winfo_children()) - self.numberOfWidgets
            print('len {}'.format(lengthOfRefresh))
            print(self.winfo_children())
            if lengthOfRefresh > 0:
                for widget in self.winfo_children()[self.numberOfWidgets:len(self.winfo_children())]:
                    print('{} this is widget'.format(widget))
                    widget.destroy()
            self.canvas = FigureCanvasTkAgg(figure, self)
            self.canvas.show()
            self.canvas.get_tk_widget().place(relheight = .95, relwidth = 1, rely = .14)
            self.canvas._tkcanvas.place(relheight = .95, relwidth = 1, rely = .14)



        def saveGraphs():
            fileName = filedialog.asksaveasfile(mode='w', defaultextension='.pdf')
            with PdfPages(fileName.name) as pdf:
                for fig in self.controller.shared_data['figurelist']:
                    fig.set_size_inches(12,7)
                    pdf.savefig(fig)

        def exportData():
            fileName = filedialog.asksaveasfile(mode='w', defaultextension='.csv')
            self.controller.shared_data['dfValues'].to_csv(fileName, index = False)


        appSize = 1045
        buttonWidth = 24
        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage), width=buttonWidth )
        button1.place(x = appSize/7*-1, y = 60, relx = 1/7)

        button2 = ttk.Button(self, text='Total Portfolio', command=graph1, width=buttonWidth )
        button2.place(x = appSize/7*0, y = 60, relx = 1/7)

        button3 = ttk.Button(self, text='Individual Accounts',command=graph2, width=buttonWidth )
        button3.place(x = appSize/7*1, y = 60, relx = 1/7)

        button4 = ttk.Button(self, text='Needed Cash',command=graph3, width=buttonWidth )
        button4.place(x = appSize/7*2, y = 60, relx = 1/7)

        button5 = ttk.Button(self, text='Information',command=graph4, width=buttonWidth )
        button5.place(x = appSize/7*3, y = 60, relx = 1/7)

        button6 = ttk.Button(self, text='Save all Graphs', command=saveGraphs, width=buttonWidth )
        button6.place(x = appSize/7*4, y = 60, relx = 1/7)

        button7 = ttk.Button(self, text='Export Data', command=exportData, width=buttonWidth )
        button7.place(x = appSize/7*5, y = 60, relx = 1/7)

        self.numberOfWidgets = len(self.winfo_children())

class InitialInfoInput(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Initialize the isCouple Variable
        isCoupleVar = tk.StringVar()
        coupleOptions = ['Yes','No']
        cashNeededVar = tk.DoubleVar()
        totalAccountsVar = tk.IntVar()
        inflationValue = tk.DoubleVar()
        incomeTaxRateValue = tk.DoubleVar()
        capitalGainsVar = tk.DoubleVar()
        nameEntryVar = tk.StringVar()
        ageEntryVar = tk.IntVar()
        name2EntryVar = tk.StringVar()
        age2EntryVar = tk.IntVar()
        yearsTilRetirementValue1 = tk.IntVar()
        yearsTilRetirementValue2 = tk.IntVar()
        widgetState = 'disabled'

        def initialQuestions():
            try:
                self.controller.shared_data['isCouple'] = isCoupleVar.get()
                self.controller.shared_data['cashNeededStart'] = cashNeededVar.get()
                self.controller.shared_data['howManyAccounts'] = totalAccountsVar.get()
                self.controller.shared_data['inflation'] = inflationValue.get() / 100
                self.controller.shared_data['incomeTaxRate'] = incomeTaxRateValue.get() / 100
                self.controller.shared_data['capitalGainsTaxRate'] = capitalGainsVar.get() / 100

                if self.controller.shared_data['isCouple'] == '':
                    accountInfoButton.configure(state='disabled')
                    accountInfoButton.update()
                    messagebox.showwarning("Error","Please answer whether analysis is for a couple")

                if self.controller.shared_data['howManyAccounts'] <= 0:
                    accountInfoButton.configure(state='disabled')
                    accountInfoButton.update()
                    messagebox.showwarning("Error","There needs to be at least one account")

                if self.controller.shared_data['isCouple'] == 'No':
                    try:
                        self.controller.shared_data['name1'] = nameEntryVar.get()
                        self.controller.shared_data['age1'] = int(ageEntryVar.get())
                        self.controller.shared_data['names'] = [self.controller.shared_data['name1']]
                        self.controller.shared_data['ages'] =  [self.controller.shared_data['age1']]
                        self.controller.shared_data['yearsTilRetirement'] = [yearsTilRetirementValue1.get()]
                        accountInfoButton.configure(state='enabled')
                        accountInfoButton.update()
                        if self.controller.shared_data['name1'] == '' and self.controller.shared_data['age1'] == 0:
                            accountInfoButton.configure(state='disabled')
                            accountInfoButton.update()
                            messagebox.showwarning('Error', "You are missing name and age information")
                    except:
                        accountInfoButton.configure(state='disabled')
                        accountInfoButton.update()
                        messagebox.showwarning('Error', 'Please review values entered for name, age, and retirement')

                else:
                    try:
                        self.controller.shared_data['name1'] = nameEntryVar.get()
                        self.controller.shared_data['age1'] = int(ageEntryVar.get())
                        self.controller.shared_data['name2'] = name2EntryVar.get()
                        self.controller.shared_data['age2'] = int(age2EntryVar.get())
                        self.controller.shared_data['names'] = [self.controller.shared_data['name1'], self.controller.shared_data['name2']]
                        self.controller.shared_data['ages'] = [self.controller.shared_data['age1'], self.controller.shared_data['age2']]
                        self.controller.shared_data['yearsTilRetirement'] = [yearsTilRetirementValue1.get(),yearsTilRetirementValue2.get()]
                        accountInfoButton.configure(state='enabled')
                        accountInfoButton.update()
                        if self.controller.shared_data['name1'] == '' and self.controller.shared_data['age1'] == 0 and self.controller.shared_data['name2'] == '' and self.controller.shared_data['age2'] == 0:
                            accountInfoButton.configure(state='disabled')
                            accountInfoButton.update()
                            messagebox.showwarning('Error', "You are missing name, age, and retirement information")
                    except:
                        messagebox.showwarning('Error', 'Please review values entered for name, age, and retirement')
                        accountInfoButton.configure(state='disabled')
                        accountInfoButton.update()

            except:
                accountInfoButton.configure(state='disabled')
                accountInfoButton.update()
                messagebox.showwarning("Error", "There is an issue with the information you have inputted.")

        def isCoupleAnswers():
            isCoupleAnswer = isCoupleVar.get()
            if isCoupleAnswer == 'Yes':
                widgetState = 'normal'
                name2Label.configure(state=widgetState)
                name2Label.update()
                name2Entry.configure(state=widgetState)
                name2Entry.update()
                age2Label.configure(state=widgetState)
                age2Label.update()
                age2Entry.configure(state=widgetState)
                age2Entry.update()
                ret2Label.configure(state=widgetState)
                ret2Label.update()
                ret2Entry.configure(state=widgetState)
                ret2Entry.update()
            else:
                widgetState = 'disabled'
                name2Label.configure(state=widgetState)
                name2Label.update()
                name2Entry.configure(state=widgetState)
                name2Entry.update()
                age2Label.configure(state=widgetState)
                age2Label.update()
                age2Entry.configure(state=widgetState)
                age2Entry.update()
                ret2Label.configure(state=widgetState)
                ret2Label.update()
                ret2Entry.configure(state=widgetState)
                ret2Entry.update()

        def populateAccounts():
            initialQuestions()
            self.listOfAccounts = []
            self.accountModels = []
            self.accountTypes = []
            self.accountValues = []
            self.contribValues = []
            self.accountOwners = []
            self.controller.shared_data['listOfAccounts'] = []
            self.controller.shared_data['accountOwners'] = []
            self.controller.shared_data['accountModels'] = []
            self.controller.shared_data['accountTypes'] = []
            self.controller.shared_data['accountValues'] = []

            lengthOfRefresh = len(self.winfo_children()) - self.numberOfWidgets
            print('len {}'.format(lengthOfRefresh))
            print(self.winfo_children())
            if lengthOfRefresh > 0:
                for widget in self.winfo_children()[self.numberOfWidgets:len(self.winfo_children())]:
                    print('{} this is widget'.format(widget))
                    widget.destroy()

            rowNumber = 0
            if self.controller.shared_data['isCouple'] == 'Yes':
                ownerOptions = [('Both','B'),('{}'.format(self.controller.shared_data['names'][0]),'0'),('{}'.format(self.controller.shared_data['names'][1]),'1')]
                ownerDropDownOptions = (ownerOptions[0][0],ownerOptions[1][0],ownerOptions[2][0])

            modelOptions = ('Stock','Bond','70%Stock/30%Bond','55%Stock/45%Bond','30%Stock/70%Bond')
            accountTypeOptions = ('Savings Account','After-Tax IRA/401k','Taxable','Tax-Deferred IRA/401k')


            accountInfo = tk.Frame(self,width = 300, height = 200, relief = tk.GROOVE, bd = 5)
            accountInfo.place(x = 0, y = 400)

            for i in range(0,self.controller.shared_data['howManyAccounts']):
                nameLabel = tk.Label(accountInfo, text = 'Name for account {}'.format(i+1))
                nameLabel.grid(row = rowNumber, column = 0)
                nameV = tk.StringVar()
                e = tk.Entry(accountInfo, textvariable = nameV)
                e.grid(row = rowNumber, column = 1)
                self.listOfAccounts.append(nameV)

                modelLabel = tk.Label(accountInfo,text = 'Strategy: ')
                modelLabel.grid(row = rowNumber, column = 2)
                modelV = tk.StringVar()
                modeldropDown = ttk.Combobox(accountInfo, textvariable = modelV, state = 'readonly')
                modeldropDown['values'] = modelOptions
                modeldropDown.grid(row = rowNumber, column = 3)
                self.accountModels.append(modelV)

                typeLabel = tk.Label(accountInfo, text = 'Type: ')
                typeLabel.grid(row = rowNumber, column = 4)
                typeV = tk.StringVar()
                typeDropDown = ttk.Combobox(accountInfo, textvariable = typeV, state = 'readonly')
                typeDropDown['values'] = accountTypeOptions
                typeDropDown.grid(row = rowNumber, column = 5)
                self.accountTypes.append(typeV)

                valueLabel = tk.Label(accountInfo, text = 'Value: ')
                valueLabel.grid(row = rowNumber, column = 6)
                valueV = tk.DoubleVar()
                valueEntry = tk.Spinbox(accountInfo, textvariable = valueV, from_=0.00, to=10000000000, increment=1000)
                valueEntry.grid(row = rowNumber, column = 7)
                self.accountValues.append(valueV)

                contribLabel = tk.Label(accountInfo, text = 'Annual Contribution: ')
                contribLabel.grid(row = rowNumber, column = 8)
                contribV = tk.DoubleVar()
                contribEntry = tk.Spinbox(accountInfo, textvariable = contribV, from_=0.00, to=10000000000, increment=1000)
                contribEntry.grid(row = rowNumber, column = 9)
                self.contribValues.append(contribV)


                if self.controller.shared_data['isCouple'] == 'Yes':
                        ownerLabel = tk.Label(accountInfo,text = 'Account Owner: ')
                        ownerLabel.grid(row = rowNumber, column = 10)
                        ownerV = tk.StringVar()
                        ownerDropDown = ttk.Combobox(accountInfo, textvariable = ownerV, state = 'readonly')
                        ownerDropDown['values'] = ownerDropDownOptions
                        ownerDropDown.grid(row = rowNumber, column = 11)
                        self.accountOwners.append(ownerV)
                else:
                    self.accountOwners.append(self.controller.shared_data['name1'])

                rowNumber += 1


            accountInfoButton.configure(text = 'Refresh Accounts')
            accountInfoButton.update()

            runModelButton.configure(state = 'enabled')
            runModelButton.update()









        def getAccountInfo():
            self.controller.shared_data['listOfAccounts'] =  [x.get() for x in self.listOfAccounts]
            self.controller.shared_data['accountModels'] =  [x.get() for x in self.accountModels]
            self.controller.shared_data['accountTypes'] =  [x.get() for x in self.accountTypes]
            self.controller.shared_data['accountValues'] = [x.get() for x in self.accountValues]
            self.controller.shared_data['contribValues'] = [x.get() for x in self.contribValues]
            try:
                self.controller.shared_data['accountOwners'] = [x.get() for x in self.accountOwners]
            except:
                self.controller.shared_data['accountOwners'] = self.accountOwners

            print(self.controller.shared_data['listOfAccounts'])
            print(self.controller.shared_data['accountModels'])
            print(self.controller.shared_data['accountTypes'])
            print(self.controller.shared_data['accountValues'])
            print(self.controller.shared_data['accountOwners'])

            print(self.controller.shared_data)
            Review(self.controller)
            #controller.show_frame(ReviewPage) # This is used to create the Review Page


        x = 20
        startx = 30
        initialInfoLabel = tk.Label(self, text = 'Initial Information', font = ("Times", 15, "bold", "underline"))
        initialInfoLabel.place(x = 150, y = 20)
        isCoupleLabel = tk.Label(self, text = 'Is this analysis for a couple?')
        isCoupleLabel.place(x=0, y = startx + x)
        columnCount = 1


        columnx = 320
        for answer in coupleOptions:
            isCoupleRadio = tk.Radiobutton(self, text=answer, variable = isCoupleVar,value=answer, command = isCoupleAnswers)
            isCoupleRadio.place(x = columnx, y = startx + x-7)
            columnx += 60

        cashNeededLabel = tk.Label(self, text = 'How much money will you need annually in retirement?')
        cashNeededLabel.place(x=0, y = startx + x*2)
        cashNeededSpinbox = tk.Spinbox(self, from_ = 0.00, to = 100000000.00, textvariable = cashNeededVar, increment = 1000)
        cashNeededSpinbox.place(x=300, y = startx + x*2)

        totalAccountsLabel = tk.Label(self, text = 'How many Accounts do you have?')
        totalAccountsLabel.place(x=0, y = startx + x*3)
        totalAccountsSpinbox = tk.Spinbox(self, from_ = 1, to = 8, textvariable = totalAccountsVar, state = 'readonly')
        totalAccountsSpinbox.place(x=300, y = startx + x*3)

        infLabel = tk.Label(self, text = 'What is the expected rate of inflation? (in %)').place(x=0, y = startx + x*4)
        infEntry = tk.Spinbox(self, textvariable = inflationValue, from_ = 0, to = 100, increment = 0.5).place(x=300, y = startx + x*4)
        incomeTaxLabel1 = tk.Label(self, text = 'What is your income tax rate? (in %)').place(x=0, y = startx + x*5)
        incomeTaxEntry1 = tk.Spinbox(self, textvariable = incomeTaxRateValue, from_ = 0, to = 90, increment = 0.5).place(x=300, y = startx + x*5)
        capitalGainsLabel = tk.Label(self, text = 'What is your capital gains rate? (in %)').place(x=0, y = startx + x*6)
        capitalGainsEntry1 = tk.Spinbox(self, textvariable = capitalGainsVar, from_ = 0, to = 90, increment = 0.5).place(x=300, y = startx + x*6)

        nameAgeRetLabel = tk.Label(self, text = 'Name, Age, and Retirement Info', font = ("Times", 15, "bold", "underline"))
        nameAgeRetLabel.place(x=90, y = startx + x*7)


        nameLabel = tk.Label(self, text='Name of person 1?')
        nameLabel.place(x=0, y = startx + x*9)
        nameEntry = tk.Entry(self, textvariable = nameEntryVar)
        nameEntry.place(x=300, y = startx + x*9)
        ageLabel = tk.Label(self, text='How old is person 1?')
        ageLabel.place(x=0, y = startx + x*10)
        ageEntry = tk.Spinbox(self, from_ = 0, to = 115, textvariable = ageEntryVar)
        ageEntry.place(x=300, y = startx + x*10)
        ret1Label = ttk.Label(self, text = 'Years until retirement for person 1:')
        ret1Label.place(x=0, y = startx + x*11)
        ret1Entry = tk.Spinbox(self, from_ = 0, to = 100, textvariable = yearsTilRetirementValue1)
        ret1Entry.place(x=300, y = startx + x*11)

        name2Label = tk.Label(self, text='Name of person 2?', state = widgetState)
        name2Label.place(x=0, y = startx + x*12)
        name2Entry = tk.Entry(self,  textvariable = name2EntryVar, state = widgetState)
        name2Entry.place(x=300, y = startx + x*12)
        age2Label = tk.Label(self, text='How old is person 2?', state = widgetState)
        age2Label.place(x=0, y = startx + x*13)
        age2Entry = tk.Spinbox(self, from_ = 0, to = 115, textvariable = age2EntryVar, state = widgetState)
        age2Entry.place(x=300, y = startx + x*13)
        ret2Label = ttk.Label(self, text = 'Years until retirement for person 2:', state = widgetState)
        ret2Label.place(x=0, y = startx + x*14)
        ret2Entry = tk.Spinbox(self, from_ = 0, to = 100, textvariable = yearsTilRetirementValue2, state = widgetState)
        ret2Entry.place(x=300, y = startx + x*14)


        x2 = 111
        button1 = ttk.Button(self, text="Back to Home", width = 17, command=lambda: controller.show_frame(StartPage))
        button1.place(x=0, y = 0)

        b = ttk.Button(self, text='Submit Info',width = 17, command = initialQuestions)
        b.place(x=x2, y = 0)

        accountInfoButton = ttk.Button(self, text = 'Generate Accounts', width = 17, state = 'disabled', command = populateAccounts)
        accountInfoButton.place(x=x2*2, y = 0)



        runModelButton = ttk.Button(self, text = 'Run Projection', width = 17, command = getAccountInfo, state = 'disabled')
        runModelButton.place(x=x2*3, y = 0)

        accountInfoLabel = ttk.Label(self, text = 'Account Information', font = ("Times", 15, "bold", "underline"))
        accountInfoLabel.place(x=130, y = startx + x*16)

        photo = Image.open("InputBackground.jpg")
        self.graphic = ImageTk.PhotoImage(photo)
        graphic = tk.Label(self, image=self.graphic)
        graphic.image = photo
        graphic.place(x=445, y = -2)

        self.numberOfWidgets = len(self.winfo_children())



""" Need to figure out this page. Once this is done I can run the model."""

class ReviewPage(tk.Frame):

    '''def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        backToInputButton = ttk.Button(self, text = 'Back to Input', command = lambda: controller.show_frame(InitialInfoInput))
        backToInputButton.grid(row = 0, column = 0)'''


class QuarterlyBilling(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.printoutInfo = []

        def get_files():
            try:
                self.hd = filedialog.askopenfilename(initialdir = "/", title = "Select Holdings File")
                self.tb = filedialog.askopenfilename(initialdir = "/", title = "Select Billing File")
                self.tt = filedialog.askopenfilename(initialdir = "/", title = "Select Transactions File")
                self.pa = filedialog.askopenfilename(initialdir = "/", title = "Select PortAccount# File")
                self.ca = filedialog.askopenfilename(initialdir = "/", title = "Select Cash Available File")
                self.st = filedialog.askopenfilename(initialdir = "/", title = "Select Short Term Shares File")

                runBillingButton.configure(state = 'active')
                runBillingButton.update()

            except:
                messagebox.showwarning("Error", "There was an error with one of the input files.")

        def runBilling():
            try:
                hd = pd.read_csv(self.hd)
                tb = pd.read_csv(self.tb, thousands = ',')
                tt = pd.read_csv(self.tt)
                pa = pd.read_csv(self.pa)
                ca = pd.read_csv(self.ca)

                ### While reading the ShortTerm csv I need
                st = pd.read_csv(self.st, thousands = ',')

                files = {'Holdings File:':self.hd, 'Billing Info:':self.tb,'Transactions File:':self.tt,'Portfolio Account # File:':self.pa,'Cash Available File:':self.ca,'Short Term Shares File:':self.st}

                for key, value in files.items():
                    output.insert(tk.END, '{} {}\n'.format(key, value))
                    output.update()
                output.insert(tk.END, '\n')

                ### Rename columns in PortAccount#, ShortTerm, Billing, and CashAvailable to make the merge function possible.
                pa.rename(columns={'Portfolio Name':'Portfolio','Account Number': 'AccountNumber'},inplace=True)
                st.rename(columns={'Account Number': 'AccountNumber'},inplace=True)
                tb.rename(columns={'Acct Number': 'AccountNumber'},inplace=True)
                ca.rename(columns={'Cash Avail. to Withdraw': 'WcCashAvailable','Account #': 'AccountNumber'},inplace=True)

                ### Fill NaN values and change the column names for Trasactions DataFrame.
                tt.fillna('',inplace=True)
                tt.columns = tt.loc[1]

                ### Remove all unnessesary columns from ShortTerm DataFrame
                st = st[['AccountNumber','Shares With Redemption Fees', 'Symbol']]
                st.fillna(0,inplace = True)

                ### Drop the Portfolios that do not have holdings at the bottom of the Holding Dataframe.
                hd = hd[0:len(hd['Symbol'].dropna())]

                ### Convert Fee from $ as a string to a float
                tb['Fee'] = tb['Fee'].apply(lambda x: x.replace('$','').replace(',',''))
                tb['Fee'] = pd.to_numeric(tb['Fee'],errors='coerce')

                ### Convert Cash Available from $ as a string to a float
                ca['WcCashAvailable'] = ca['WcCashAvailable'].apply(lambda x: x.replace('$','').replace(',',''))
                ca['WcCashAvailable'] = pd.to_numeric(ca['WcCashAvailable'],errors='raise')

                ### Convert the Market Value to a float

                tt['MarketValue'] = pd.to_numeric(tt['MarketValue'],errors='coerce')

                ### Create the Transaction DataFrame that only includes buy orders greater than 999. Sum it to double Check with
                ### manually doing the Transaction sheet in Excel. Total Should equal 21793739.190000002

                tt = tt[(tt['Action']=='Buy') & (tt['MarketValue'][3:]>999)]
                sum(tt['MarketValue'])

                ### Create the Yes value for the RoundTrip column

                tt['RoundTrip'] = 'Yes'

                ### This removes the 403(b) accounts which are longer than 9 characters
                tt = tt[tt['AccountNumber'].apply(len)<10]

                ### Prep the Transactions DataFrame for the merge with holdings. Keep only relevant columns

                tt = tt[['AccountNumber','Ticker','RoundTrip']]

                ### Rename the columns to match with the holdings excel sheet

                tt.columns = ['AccountNumber','Symbol','RoundTrip']

                ### Remove duplicates from the Transaction dataframe. Since only 1 roundtrip matters we don't need duplicates.
                tt.drop_duplicates(inplace=True)

                ### Remove trailing whitespace from the Portfolio column and then merge with Data mined Portfolio and Account# CSV

                hd['Portfolio'] = hd.Portfolio.apply(lambda x: str(x).rstrip())
                hda = pd.merge(hd,pa,how='left',on=['Portfolio'])

                ### Merge the holdings DataFrame on account number and symbol with the Transactions Dataframe

                Trades1 = pd.merge(hda,tt,how = 'left',on=['AccountNumber','Symbol'])

                ### Replace the Trades NaN with No

                Trades1.fillna('No',inplace = True)

                ### Remove Duplicate values from Trades1

                Trades1_drop_duplicated = Trades1.drop_duplicates()

                ### This tests to make sure that the roundtrip additions to the Holding DataFrame equal the amount that originated from the Transaction DataFrame
                print('''---Double Checks that the Merged DataFrame with RoundTrips Equals the Original DataFrame with RoundTrip Information---
                ------------------------------------------------------------------------------------------------------------------------''')
                if Trades1_drop_duplicated[Trades1_drop_duplicated['RoundTrip'] == 'Yes'].shape[0] != tt.shape[0]:
                    roundtripLine = '''\nMerged DataFrame has {} instances of RoundTrips and Original Transactions DataFrame has {} instances.
    There is a difference between the amount of holdings showing roundtrip and the non-duplicated RoundTrip dataframe tt. Total difference = {}\n'''.format(
                        Trades1_drop_duplicated[Trades1_drop_duplicated['RoundTrip'] =='Yes'].shape[0],
                                    tt.shape[0], abs(Trades1_drop_duplicated[Trades1_drop_duplicated['RoundTrip'] == 'Yes'].shape[0]-tt.shape[0]))

                else:
                    roundtripLine = '\nMerged DataFrame has {} instances of RoundTrips and Original Transactons DataFrame has {} instances. Everything is good\n'.format(
                        Trades1_drop_duplicated[Trades1_drop_duplicated['RoundTrip'] =='Yes'].shape[0],tt.shape[0])

                self.printoutInfo.append(roundtripLine)
                ### Find values that aren't in merged dataframe. This will show the instances where a position was bought into, but potentially sold
                ### before the round-trip was over or for positions that were converted to advantage class funds (i.e FSEMX to FSEVX)
                missing = pd.DataFrame()
                missing['OriginalAccountNumber'] = tt['AccountNumber']
                missing['OriginalSymbol'] = tt['Symbol']
                missing['MergeFrame'] = missing['OriginalAccountNumber'] + missing['OriginalSymbol']
                missing2 = pd.DataFrame()
                missing2 = Trades1_drop_duplicated[Trades1_drop_duplicated['RoundTrip'] == 'Yes'][['AccountNumber','Symbol']]
                missing2['MergeFrame'] = missing2['AccountNumber'] + missing2['Symbol']
                findmissing = pd.merge(missing, missing2, how = 'outer', on = ['MergeFrame'])

                ### Fills Symbol and AccountNumber column in all positions that are not contained in both DataFrames.

                findmissing.fillna('ERROR',inplace = True)
                print(findmissing[findmissing['Symbol'] == 'ERROR'])
                missingRoundTripLine1 = """These Accounts are the accounts missing in merged dataframe that added RoundTrip information.
    More often than not this is the result of the seed accounts that do not have a portfolio or an account that bought a fund that was either sold during the round-trip or that was converted.
    Conversions occur for a lower fee fund of the same positions (ie. FSEMX to FSEVX)\n"""
                missingRoundTripLine2 = findmissing[findmissing['Symbol'] == 'ERROR']

                self.printoutInfo.append(missingRoundTripLine1)
                self.printoutInfo.append(missingRoundTripLine2)

                ### Creation of a ShortTermCheck varible that calculates the total shares with redemption fees for a later double-check
                ShortTermCheck = st['Shares With Redemption Fees'].sum()

                ### Creation of the new ShortTerm Dataframe that only shows value greater than 0
                st = st[st['Shares With Redemption Fees'] > 0]

                ### Creation of a variable that is used to make sure that the short term shares have been calculated correctly.
                PostManipulatedShortTermCheck = st['Shares With Redemption Fees'].sum()

                if round(PostManipulatedShortTermCheck,4) != round(ShortTermCheck,4):
                    shortTermLine = '''\nThe amount of short-term shares with the premanipulated DataFrame is different than the frame after checking for Shares > 0
    Dataframe Values: Original = {} and New = {}\n'''.format(ShortTermCheck,PostManipulatedShortTermCheck)

                else:
                    shortTermLine = '\nShort term shares are calculated correctly. Dataframe Values: Orignal = {} and New = {}\n'.format(
                        round(ShortTermCheck,4),PostManipulatedShortTermCheck)


                self.printoutInfo.append(shortTermLine)

                ### Replaces the hyphon in the account numbers that are in the Short Term shares Dataframe.
                st['AccountNumber'] = st['AccountNumber'].apply(lambda x: x.replace('-',''))

                ### Merge Short-term shares onto the Dataframe that includes holding and round-trips. This is the final DataFrame for Trade Prep

                FinalTradePrep = pd.merge(Trades1_drop_duplicated,st,how = 'left',on=['AccountNumber','Symbol'])

                ### Replace Shares With Redemtion Fees values of Nan with 0

                FinalTradePrep['Shares With Redemption Fees'].fillna(0,inplace = True)

                ### Reduce columns in CashAvailable to desired columns.
                ca = ca[['AccountNumber','WcCashAvailable']]

                ### Remove Cash from Holdings so that it doesn not impact trades since these holdings would be used as regular mutual funds.
                FinalTradePrep = FinalTradePrep[FinalTradePrep['Level Name'] != 'Cash & Equivalents*']

                ####### PART 1 IS COMPLETE AT THIS POINT. ALL HOLDINGS HAVE BEEN PREPPED TO SHOW SHORT-TERM AND ROUNDTRIP HOLDINGS. ##########

                ### Calculate cumulative fees by billing account.
                cumfees = pd.DataFrame(tb.groupby("BillingAccount")["Fee"].sum())
                cumfees['AccountNumber']=cumfees.index
                cumfees.rename(columns={'Fee':'CumulativeFee'},inplace=True)

                ### Add cumulative fees and WC CashAvailable to the billing DataFrame.
                tb = pd.merge(tb,cumfees,how = 'left',on=['AccountNumber'])
                tb = pd.merge(tb,ca,how='left',on=['AccountNumber'])

                ### Fill all NaN cumulative fee values with 0
                tb.fillna(0,inplace=True)

                ### Create the Fee trade for all accounts. Cumulative Fee minus the cash available from WC Cash Data and then add .5 for rounding errors.
                tb['FeeTrade'] = tb['CumulativeFee'] - tb['WcCashAvailable']+.05

                tblength = len(tb.index.values)

                ### Create A DataFrame for Pay By Invoice clients. Used to double check Trade Total + Invoice Total after trading and for reference. Remove Clients from DataFrame
                PayByInvoice = tb[tb['BillingAccount'] == 'Pay By Invoice']
                tb_no_invoice = tb[tb['BillingAccount'] != 'Pay By Invoice']



                ### Create length value to loop through billing dataframe
                tblength = len(tb.index.values)

                ### Add TradeValue to Final Trade Prep DataFrame
                FinalTradePrep['TradeValue']=0

                """ This Loop applies the trade values to each holding that needs to be traded for fees. I first make sure that the cummulative fee is greater than 0 to avoid applying
                trades for accounts with negative fee trades due to the calculation method. I then check to make sure the fee trade is greater than 0. If either of these if functions fail
                make sure the FeeTrade column value = 0. I take the account number from billing and then the feetrade amount calculated earlier. After this I create a new mini DataFrame
                that only contains the information for the accountnumber and then I clean it to remove holdings with redemption fees, targets that have a value of zero since these tend
                to be special holdings. New clients will have waived fees and they should be the only other clients holding positions with a target of 0. To clean for models that account
                for stock holdings on a clients request I have filtered the dataframe to remove symbols that are less than length 5 which denotes mutual fund. Finally I sort the dataframe
                by the difference from target and actual holding values. This places overweight holdings on top. After this I create a variable to test whether we can sell multiple holdings to
                achieve the fee or if we need to sell a large amount of one holding. This then get's processed through some if statements and it creates the final trade instructions."""
                for i in range(0,tblength):
                    try:
                        if tb_no_invoice.loc[i,'CumulativeFee'] > 0:
                            if tb_no_invoice.loc[i,'FeeTrade'] > 0:
                                AccountNumber = tb_no_invoice.loc[i,'AccountNumber']
                                print(AccountNumber,tb_no_invoice.loc[i,'CumulativeFee'],tb_no_invoice.loc[i,'WcCashAvailable'])
                                FeeTrade = tb_no_invoice.loc[i,'FeeTrade']
                                TradingFrame = FinalTradePrep[(FinalTradePrep['AccountNumber'] == AccountNumber) &
                                                              (FinalTradePrep['Shares With Redemption Fees'] < 1) & (FinalTradePrep['Target'] > 0) & (FinalTradePrep['Symbol'].apply(len) > 4)].sort_values(by = 'Difference',ascending = False)
                                TradingFrame.sort_values(by = 'Difference',ascending=False,inplace = True)
                                TradingFramelength = len(TradingFrame.index.values)
                                TradingFrameTotal = TradingFramelength*999
                                IndexValues = TradingFrame.index.values
                                if TradingFrameTotal < FeeTrade:
                                    TradingFrame = TradingFrame[TradingFrame['RoundTrip'] != 'Yes']
                                    FinalTradePrep.loc[IndexValues[0], 'TradeValue'] = FeeTrade
                                elif FeeTrade > 999 and TradingFrameTotal > FeeTrade:
                                    count = 0
                                    while FeeTrade > 999:
                                        FinalTradePrep.loc[IndexValues[count], 'TradeValue'] = 999
                                        FeeTrade = FeeTrade - 999
                                        count = count + 1
                                    FinalTradePrep.loc[IndexValues[count], 'TradeValue'] = FeeTrade
                                else:
                                    FinalTradePrep.loc[IndexValues[0],'TradeValue'] = FeeTrade
                            else:
                                tb_no_invoice.loc[i,'FeeTrade'] = 0
                        else:
                            tb_no_invoice.loc[i,'FeeTrade'] = 0
                            pass
                    except Exception as e:
                        print(str(e))
                        try:
                            output.insert(tk.END,"Location {} is associated with a client or account that is to be paid by invoice. Portfolio name is: {}".format(i, PayByInvoice.loc[i,'Portfolio']))
                            output.insert(tk.END,'\n')
                            output.update()
                        except:
                            print("This account had an error {}".format(tb_no_invoice.loc[i, "Portfolio"]))

                ### Part 2 Is Complete ###

                ###Create New DataFrame that will be used to import trade information to WC.
                WC_Import = FinalTradePrep[FinalTradePrep['TradeValue'] > 0]

                if round(sum(FinalTradePrep['TradeValue']),4) == round(sum(WC_Import['TradeValue']),4):
                    tradeAuditLine = 'Trade values match up: FinalTradePrep = {}, WC_Import = {}'.format(sum(FinalTradePrep['TradeValue']),sum(WC_Import['TradeValue']))
                else:
                    tradeAuditLine = 'Trade values do not match-up: FinalTradePrep = {}, WC_Import = {}'.format(sum(FinalTradePrep['TradeValue']),sum(WC_Import['TradeValue']))


                self.printoutInfo.append(tradeAuditLine)
                ###Changes the Import File to just contain the 3 columns that are needed.
                WC_Import_Final = WC_Import[['AccountNumber','TradeValue','Symbol']]

                ###Fills in the columns with the information that Fidelity uses to create mutual fund trades. All information can be seen in WC. Import/Export > Import > Question Mark in the top right.
                WC_Import_Final['AccountType'] = 1
                WC_Import_Final['OrderAction'] = 'SF'
                WC_Import_Final['PriceType'] = ''
                WC_Import_Final['TimeInForce'] = ''
                WC_Import_Final['StopPrice/LimitPrice'] = ''
                WC_Import_Final['QuantityType'] = 'D'

                ### Creates the Finalized DataFrame with the columns in the correct order.
                WC_Import_Final = WC_Import_Final[['AccountNumber','AccountType','OrderAction','TradeValue','Symbol','PriceType','TimeInForce','StopPrice/LimitPrice','QuantityType']]

                ### Rounds the trade values to 2 decimal places to avoid an error that is created when the value has goes to too many decimal places.
                WC_Import_Final['TradeValue'] = WC_Import_Final['TradeValue'].apply(lambda x: round(x,2))



                for i in self.printoutInfo:
                    output.insert(tk.END, i)
                    output.insert(tk.END, '\n')
                    output.update()

                ### Creation of the CSV file that will be uploaded.
                now = datetime.datetime.now()
                date = str(now.month) + str(now.day) + str(now.year)
                getDirectoryName = filedialog.askdirectory(title = 'Choose Folder to Save Files')
                PayByInvoice.to_csv(getDirectoryName + "\PaybyInvoiceClients{}.csv".format(date), index = False)
                FinalTradePrep.to_csv(getDirectoryName + '\FinalTradesPrep{}.csv'.format(date), index = False)
                WC_Import_Final.to_csv(getDirectoryName + "\WCImport{}.csv".format(date), index = False, header=False)

            except Exception as e:
                import traceback
                output.insert(tk.END, traceback.format_exc())
                output.update()

                ### Part 3 Is Complete ###



        backHomeButton = ttk.Button(self, text="Back to Home", width = 17, command=lambda: controller.show_frame(StartPage))
        backHomeButton.pack()
        importFilesButton = ttk.Button(self, text = "Import Files", command=get_files)
        importFilesButton.pack()
        runBillingButton = ttk.Button(self, text = "Run Billing", command = runBilling, state = 'disabled')
        runBillingButton.pack()

        outputLabel = tk.Label(self, text = "Output", font = ("Times", 25, "bold", "underline"))
        outputLabel.pack()


        outputFrame = tk.Frame(self)
        outputFrame.pack(fill = 'both', expand = True)
        outputFrame.grid_propagate(False)
        outputFrame.columnconfigure(0, weight = 1)
        outputFrame.rowconfigure(0, weight = 1)
        output = tk.Text(outputFrame)
        output.grid(row = 0, column = 0, sticky='nsew')
        scroll = tk.Scrollbar(outputFrame, command = output.yview)
        scroll.grid(row = 0, column = 1, sticky = 'nsew')
        output['yscrollcommand'] = scroll.set


class CapitalGainsAudit(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.models = {'NS Med-Low': 'NS MEDIUM LOW',
                  'Med-Low': 'MEDIUM LOW',
                  'TE Growth': 'TE GROWTH',
                  'Medium': 'MEDIUM',
                  'NS Low': 'NS LOW',
                  'NS High': 'NS HIGH',
                  'TE Select': 'TE SELECT',
                  'Low': 'LOW',
                  'Med-High': 'MEDIUM HIGH',
                  'Income w Gwth': 'INCOME WITH GROWTH',
                  '70/30': 'INVALID ASSIGNMENT (MODEL CONFLICT)',
                  'Aggr G&I': 'AGGR G&I'}

        symbolVar = tk.StringVar()
        dateVar = tk.StringVar()
        self.completeAudit = None

        def get_files():
            try:
                self.accounts = filedialog.askopenfilename(initialdir = "/", title = "Select WC All Accounts File")
                self.gains = filedialog.askopenfilename(initialdir = "/", title = "Select WC Profit and Loss File")

                runAuditButton.configure(state = 'active')
                runAuditButton.update()
            except:
                messagebox.showwarning("Error", "There was an error with one of the input files.")

        def runAudit():
            try:
                accounts = pd.read_csv(self.accounts)
                gains = pd.read_csv(self.gains, thousands = ",")
                Symbol = symbolInput.get()
                tradeDate = tradeDateInput.get()

                ### Input trade date to avoid issues running the report early.
                tradeDate = datetime.strptime(tradeDate,'%m/%d/%Y')
                longTermDate = tradeDate - relativedelta(years = 1)

                models = [self.models[modelSelection.get(idx)] for idx in modelSelection.curselection()]

                gains.columns = gains[4:5].values.tolist()
                gains = gains[5:].reset_index(drop=True)

                ### Retains only clients that are included in the models that will be trading.
                accounts = accounts[accounts["Account Tax Status"] == "TAXABLE"]
                accounts['InModel'] = accounts["Model Name"].apply(lambda x: "True" if x in models else "False")
                accounts = accounts[accounts["InModel"] == "True"].reset_index(drop = True)
                accounts = accounts.copy()

                ### Cleans up dataframe and converts strings to ints where needed.
                gains["Account #"].apply(str)
                gains.dropna(inplace=True)
                gains["Account #"] = gains["Account #"].apply(lambda x: x.replace("-",""))
                gains["Gain/Loss"] = gains["Gain/Loss"].apply(lambda x: "0" if x == "--" else x)
                gains["Gain/Loss"] = gains["Gain/Loss"].apply(lambda x: x.replace(",","")).apply(float)
                gains["Closing Quantity"] = gains["Closing Quantity"].apply(lambda x: x.replace(",","")).apply(float)
                gains["Date Acquired"] = gains["Date Acquired"].apply(lambda x: datetime.strptime(x,'%m/%d/%Y'))
                gains["Holding Period"] = gains["Date Acquired"].apply(lambda x: "Long" if x < longTermDate else "Short")
                gains = gains.copy()

                stGains = []


                stShares = []
                ltGains = []
                ltShares = []
                buyDates = []
                longTermDates = []

                ### The loop that calculates all gain information for each client.
                for account in range(0, len(accounts.index.values)):
                    accountNumber = accounts.loc[account,"Account #"]
                    accountStGain = 0
                    accountStShares = 0
                    accountLtGain = 0
                    accountLtShares = 0
                    accountBuyDates = []
                    firstBuyDate = []
                    accountGains = gains[(gains["Account #"] == accountNumber) & (gains["Symbol"] == Symbol)].reset_index(drop=True).copy()
                    for i in range(0, len(accountGains.index.values)):
                        if accountGains.loc[i,"Holding Period"] == "Short":
                            accountStGain += accountGains.loc[i,"Gain/Loss"]
                            accountStShares += accountGains.loc[i,"Closing Quantity"]
                            dt = accountGains.loc[i,"Date Acquired"]
                            accountBuyDates.append("{}/{}/{} bought {} shares".format(dt.month,dt.day,dt.year,accountGains.loc[i,"Closing Quantity"]))
                            firstBuyDate.append(dt)
                        elif accountGains.loc[i,"Holding Period"] == "Long":
                            accountLtGain += accountGains.loc[i,"Gain/Loss"]
                            accountLtShares += accountGains.loc[i,"Closing Quantity"]
                        else:
                            stGains.append(0)
                            stShares.append(0)
                            ltGains.append(0)
                            ltShares.append(0)
                            buyDates.append(0)
                            print("{} does not own".format(accounts.loc[account,"Primary Account Holder"]))
                    stGains.append(accountStGain)
                    stShares.append(accountStShares)
                    ltGains.append(accountLtGain)
                    ltShares.append(accountLtShares)
                    buyDates.append(accountBuyDates)
                    if len(firstBuyDate) > 0:
                        print("Min date {} for {}".format(min(firstBuyDate) + relativedelta(years=1),accountNumber))
                        ltDate = min(firstBuyDate) + relativedelta(years=1)
                        longTermDates.append("{}/{}/{}".format(ltDate.month,ltDate.day,ltDate.year))
                    else:
                        longTermDates.append(0)


                accounts["ShortTermGains"] = stGains
                accounts["ShortShares"] = stShares
                accounts["LongTermGains"] = ltGains
                accounts["LongShares"] = ltShares
                accounts["BuyDates"] = buyDates
                accounts["FirstLongTermDate"] = longTermDates

                accounts["TotalShares"] = accounts["ShortShares"] + accounts["LongShares"]
                accounts["ShortShare%"] = accounts["ShortShares"]/accounts["TotalShares"] * 100
                accounts = accounts[["Account #","Primary Account Holder","Account Tax Status", "Total Account Value", "Model Name", "ShortTermGains",
                                     "ShortShares", "LongTermGains", "LongShares", "BuyDates","TotalShares","ShortShare%","FirstLongTermDate"]]

                self.completeAudit = accounts
                exportAuditButton.configure(state = "active")
                exportAuditButton.update()

            except:
                messagebox.showwarning("Error", "There was an error with the Audit. Double Check your inputs and try again")

        def exportExcel():
            fileName = filedialog.asksaveasfile(mode='w', defaultextension='.csv')
            self.completeAudit.to_csv(fileName, index = False)


        backHomeButton = ttk.Button(self, text="Back to Home", width = 17, command=lambda: controller.show_frame(StartPage))
        backHomeButton.pack()

        importFilesButton = ttk.Button(self, text = "Import Files", command=get_files)
        importFilesButton.pack()

        modelSelection = tk.Listbox(self, selectmode="multiple")

        listIndex = 0
        for key in self.models:
            modelSelection.insert(listIndex, key)
            listIndex += 1

        modelSelection.pack()

        symbolLabel = ttk.Label(self, text = "Enter in Symbol to be Traded: ")
        symbolInput = ttk.Entry(self, textvariable = symbolVar)
        symbolLabel.pack()
        symbolInput.pack()

        tradeDateLabel = ttk.Label(self, text = "Enter Trade Date (MM/DD/YYYY): ")
        tradeDateInput = ttk.Entry(self, textvariable = dateVar)
        tradeDateLabel.pack()
        tradeDateInput.pack()

        runAuditButton = ttk.Button(self, text = "Run Billing", command = runAudit, state = 'disabled')
        runAuditButton.pack()

        exportAuditButton = ttk.Button(self, text = "Export Audit CSV", command = exportExcel, state = 'disabled')
        exportAuditButton.pack()




app = BWMCommandCenterApp()
app.geometry("1045x620")
app.mainloop()

