import sys
import requests
import json

class Ziner_automation:
    modelName = None
    email = 'emailaddress'
    password = 'password'
    orgId = None
    token = None

    def __init__(self,modelName):
        self.modelName = modelName

    def login(self,server,org_id):
        loginUrl = 'https://%s.zinier.com/session/login' % server
        
        loginHeader = {
        "Content-Type": "application/json",
        "Authorization": "Basic emluMjE1MTM5NDc1NDE6emluaWVy",
        "loginId": self.email,
        "password": self.password,
        "orgId": org_id
        }

        # import pdb; pdb.set_trace()
        # print(loginHeader)
        loginResponse = requests.request("POST", loginUrl, headers=loginHeader)

        if(loginResponse.ok):
            jData = json.loads(loginResponse.content)

            print("The response contains {0} properties".format(len(jData)))
            print("\n")
            for key in jData:
                print(key + " : " + str(jData[key]))
            print("\n")
        else:
            loginResponse.raise_for_status()
        self.token = jData['token']
        self.orgId = org_id
        return jData    
    
    def get_model_def(self):
        getModelDefUrl = 'https://orglab.zinier.com/model/getModelDef'

        apiHeader = {
        "Content-Type": "application/json",
        "Authorization": "Basic emluMjE1MTM5NDc1NDE6emluaWVy",
        "loginId": self.email,
        "token": self.token,
        "orgId": self.orgId
        }

        body = {
        "data": [
            {
            "modelName": self.modelName
            }
        ]
        }

        payload = json.dumps(body, indent = 2,sort_keys=False)

        modelColumnNamesResponse = requests.request("POST", getModelDefUrl, data=payload, headers=apiHeader)

        if(modelColumnNamesResponse.ok):
            kData = json.loads(modelColumnNamesResponse.content)
        else:
            modelColumnNamesResponse.raise_for_status()

        model_def = json.dumps(kData, indent = 2,sort_keys=False)
        return model_def
    
    def read_model_query_data(self,model_def):
        responseData = json.loads(model_def)
        data = responseData['data']
        modelName = data[0]['modelName']
        modelFields = data[0]['fields']
        modelFieldsKeysList = list(modelFields.keys())

        value = '@PrimaryKey'

        def find_key_for(input_dict, value):    
            for k, v in input_dict.items():
                for j, _w in v.items():
                    if j == value:
                        yield k

        primaryKey = next(find_key_for(modelFields, value), None)

        columns = {}

        for key in modelFieldsKeysList:
            leftkey =  key
            rightvalue = modelName+"."+key
            columns[leftkey] = rightvalue

        columns.update({'recver' : modelName+".recver"})
        # columns.update({'createdDate' : modelName+".createdDate"})
        # columns.update({'createdByUser' : modelName+".createdByUser"})
        # columns.update({'modifiedDate' : modelName+".modifiedDate"})
        # columns.update({'modifiedByUser' : modelName+".modifiedByUser"})

        querydata = {
        "data": [
                {
                    "models": [
                        modelName
                    ],
                    "columns": columns,
                    # "orderBy": "modifiedDate DESC",
                    "getCount": bool(True)
                },
            ]
        }

        query_data = json.dumps(querydata, indent = 2,sort_keys=False)
        print("Primary Key : "+primaryKey)
        print(query_data)

        filename = 'readquery'

        with open('%s.json'% filename,"w") as g:
            g.write(query_data)

        return query_data, primaryKey

    def get_model_data(self,query_data):
        ReadQueryUrl = 'https://orglab.zinier.com/query/read'

        apiHeader = {
        "Content-Type": "application/json",
        "Authorization": "Basic emluMjE1MTM5NDc1NDE6emluaWVy",
        "loginId": self.email,
        "token": self.token,
        "orgId": self.orgId
        }

        modelDataResponse = requests.request("POST", ReadQueryUrl, data=query_data, headers=apiHeader)

        if(modelDataResponse.ok):
            lData = json.loads(modelDataResponse.content)
        else:
            modelDataResponse.raise_for_status()

        b_lData = json.dumps(lData, indent = 2,sort_keys=False)

        # print(b_lData)

        filename = 'readresponse'

        with open('%s.json'% filename,"w") as g:
            g.write(b_lData)
        
        return b_lData

    def update_model_query_data(self,b_ldata,primaryKey):        
        modelName = self.modelName
        columnName = primaryKey

        updateQuery = {}
        # import pdb; pdb.set_trace()
        data = json.loads(b_ldata)['data']
        # print(data)
        for obj in data:
            obj.update({'modelName' : modelName})

        updateQuery['data'] = data
        updateQuery.update({'columns' : [columnName]})

        updateQuery_data = json.dumps(updateQuery, indent = 2,sort_keys=False)

        filename = 'updateresponse'

        with open('%s.json'% filename,"w") as g:
            g.write(updateQuery_data)

        return updateQuery_data

    def update_destination_org_model_data(self,updateQuery_data):
        pass
        # UpdateQueryUrl = 'https://orglab.zinier.com/model/update'

        # apiHeader = {
        # "Content-Type": "application/json",
        # "Authorization": "Basic emluMjE1MTM5NDc1NDE6emluaWVy",
        # "loginId": self.email,
        # "token": self.token,
        # "orgId": self.orgId
        # }

        # updateFormatQuery = requests.request("POST", UpdateQueryUrl, data=updateQuery_data, headers=apiHeader)

        # if(updateFormatQuery.ok):
        #     mData = json.loads(updateFormatQuery.content)
        # else:
        #     updateFormatQuery.raise_for_status()

        # b_mData = json.dumps(mData, indent = 2,sort_keys=False)
        # print(b_mData)

if __name__ == "__main__":
    modelName = sys.argv[1]
    za = Ziner_automation(modelName)
    jdata = za.login('orglab','orgname')
    model_def = za.get_model_def()
    q_data,p_key = za.read_model_query_data(model_def)
    model_data = za.get_model_data(q_data)
    result = za.update_model_query_data(model_data,p_key)
    # print(result)
    # jdata = za.login('orglab','gamechanger')
