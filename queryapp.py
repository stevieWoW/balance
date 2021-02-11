import databaseapp as db
import datetime


class queryapp:
    def LoadData(df):
        ########### dfbalance ###########
        if(df == 'dfbalance'):
            data = db.databaseapp.ExecuteQuery(
                [
                    {
                        "rows":"call ",
                            "table":"Balance.P_BAL_BALANCE({0},{1})".format(str(datetime.datetime.now().year - 5),str(datetime.datetime.now().year)),
                    }
                ],"Balance",False
            )

            # reset data["Total"]
            data["Total"] = 0
            # sum rows to get total
            data["Total"] = data.iloc[:,2:].sum(axis=1)



        ########### Bankaccount ###########
        elif(df == 'BankAccount'):
            bank_account_options = db.databaseapp.ExecuteQuery(
                [
                    {
                        "rows":"select BNR,NAME",
                            "table":" from Balance.BAL_BANKACCOUNT",
                    }
                ],"BankAccounts",False
            )
            data = [
                {'label': str(row.NAME), 'value': str(row.BNR)} for index,row in bank_account_options.iterrows()
            ]
            # add a total column
            data.append({'label': 'Total', 'value':'Total'})



        ########### dfincome ###########
        elif(df == 'dfincome'):
            data = db.databaseapp.ExecuteQuery(
                [
                    {
                        "rows":"select BC.NAME, BI.MONTH,BI.YEAR,BI.INCOME,BI.STATUTORY_LEVIES,BI.NET_INCOME",
                        "table":" FROM Balance.BAL_INCOME BI inner join Balance.BAL_COMPANY BC on BI.COMPANY_ID = BC.ID"
                    }
                ],"InCome", False
            )
        else:
            # do something better here
             print('wrong df')


        return data

