import csv
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, RedirectResponse
from dynamo_model import UserModel

app = FastAPI(
    title="User API Service",
    description="User management API",
    version="1.0.0",
)

def get_user_details(first_name=None, last_name=None, get_all=False):
    return_data = list()
    if get_all:
        result = UserModel.scan()
    else:
        result = UserModel.query(first_name, UserModel.last_name == last_name)
        
    for x in result:
        return_data.append(x)
        
    return return_data
        
@app.get("/health")
def health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"Status": "Healthy"})

@app.get("/")
def root():
    return RedirectResponse(url='/docs')
    
@app.get("/user/")
def return_user_data(first: str, last: str):
    """
    Returns user information for a specific user
    """
    try:
        user_details = get_user_details(first_name=first, last_name=last)[0]
        return JSONResponse({
            "FirstName": user_details.first_name,
            "LastName": user_details.last_name,
            "PhoneNumber": user_details.phone,
            "EmailAddress": user_details.email
        })
    except:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"Response": "User not found"})

@app.get("/all_users")
def get_all_users():
    all_users = get_user_details(get_all=True)
    return_data = list()
    for user_details in all_users:
        return_data.append({
            "FirstName": user_details.first_name,
            "LastName": user_details.last_name,
            "PhoneNumber": user_details.phone,
            "EmailAddress": user_details.email
        })
    return return_data

@app.post("/load_db")
def load_data():
    try:
        with open('./users.csv', 'r') as csvfile:
            csv_data = csv.reader(csvfile)
            for row in csv_data:
                UserModel(
                    first_name=row[0], 
                    last_name=row[1],
                    email=row[2],
                    phone=row[3]
                ).save()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"Status": "Success"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"Status": "Failed"})
        
        
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
