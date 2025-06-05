from fastapi import FastAPI, UploadFile, File,HTTPException, Form
from pydantic import BaseModel
import uvicorn
from service import newUserService,loginService,summaryService,fetchHistoryService
from uuid import UUID

app=FastAPI()

class newUser(BaseModel):
    name : str
    email : str
    password : str
    confirmPassword : str

class existUser(BaseModel):
    email: str
    password: str

@app.get("/")
async def welcomePage():
    return {'data':'Welcome to my AI Based Summary Application'}


@app.post('/signup')
async def createUser(user: newUser):
    try:
        if user.name=='' and user.email=='' and user.password=='' and user.confirmPassword=='':
            return HTTPException(status_code=400,detail='All fields should be non-empty')
        if user.password!=user.confirmPassword:
            return {"data":"password and confirm password should be same",'status code':200}
        
        newUser= newUserService(user)
        return {"data":newUser.get('data'),'status code':200}
    except Exception as e:
        return {"error":e,'status code':400}

@app.post('/login')
async def login(user :existUser):
     try:
         if user.email=='' and user.password=='':
            return HTTPException(status_code=400,detail='All fields should be non-empty')
         login = loginService(user)
         return {"data":login.get('data'),"status code":200}
     except Exception as e:
         return {"error":e,"status code":400}
     

@app.post('/summary')
async def summaryContent(file: UploadFile = File(...),
                         page_num: int = Form(...),
                         range: int = Form(...),
                         user_req: str = Form(...),
                         user_id: UUID = Form(...)):
    
    try:
        if not file.filename:
            return {"data":'Upload the file(pdf,docx,csv,xlsx and txt)','status code':400}
        
        data=f"file: {file}, page_num: {page_num}, range: {range}, user_request: {user_req} and userId: {user_id}"
        print("Request body: ",data)
        
        print(f"type of user_id: {type(user_id)}")
        
        print(f"file: {file.file}")
        print(f"file name: {file.filename}")
        

        file_type = file.filename.split('.')[-1]
        print('file type: ',file_type)

        result = summaryService(file.file,file_type,user_id)

        return {"data": result, 'status code':200}
        
    except Exception as e:
        return {"error":e,'status code':400}
    

@app.get("/getHistory")
async def historySummary(userid: UUID):
    try:
        print("userid",userid)
        if not userid:
            return {"data":"There is no userid","status code":400}
        result = fetchHistoryService(userid)
        return {"data":result,"statusCode":200}
    except Exception as e:
        return {"error":e,"status code":400}

if __name__=='__main__':
    uvicorn.run(app,port=8000)