from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, NewsHistory
import models
import auth
import utils
import requests
import bcrypt
from datetime import timedelta
import google.generativeai as genai

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

API_URL = "AIzaSyBhQpytzAeNrvI4w4WF3lX_zG7jIvpI3ro"  # ← Replace with your key
genai.configure(api_key=API_URL)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# Hugging Face API configuration
# HEADERS = {"Authorization": "Bearer hf_AbCdEfGhIjKlMnOpQrStUvWxYz"}
# API_URL = "https://api-inference.huggingface.co/models/gpt2"
# print("Available Models:")
# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         print(f"- {m.name} (Supports generateContent)")
        

def generate_news(prompt: str):
    try:
        response = model.generate_content(
            f"Generate a concise news article about: {prompt}. Keep it under 200 words."
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": str(e)}
        )
    

@app.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")

    print(f"Received username: {username}")
    print(f"Received password: {password}")
    
    if not username or not password:
        return JSONResponse(
            status_code=400,
            content={"message": "Username and password are required"}
        )
    
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        db_user = User(username=username, hashed_password=hashed_password.decode('utf-8'))
        db.add(db_user)
        db.commit()
        return JSONResponse(
            status_code=201,
            content={"message": "User created successfully"}
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"message": "Username already exists"}
        )
    
# @app.post("/login")
# async def login(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.generation_count = 0  # Add this line
    db.commit()

    access_token = auth.create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=10)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Update login endpoint to set cookie
@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid credentials"}
        )
    
    user.generation_count = 0
    db.commit()

    access_token = auth.create_access_token(data={"sub": username})
    response = JSONResponse(content={"success": True})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
    )
    return response

# Update generate news endpoint
@app.post("/generate-news")
async def generate_news_endpoint(request: Request, 
                               db: Session = Depends(get_db),
                               current_user: str = Depends(utils.get_current_user)):
    try:
        user = db.query(User).filter(User.username == current_user).first()
        
        if user.generation_count >= 5:
            response = RedirectResponse(url="/login")
            response.delete_cookie("access_token")
            return response
            
        generated_text = generate_news(request.query_params.get("prompt", ""))
        
        # Update generation count
        user.generation_count += 1
        db.commit()
        
        return JSONResponse(content={"news": generated_text})
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"News generation failed: {str(e)}")

# @app.post("/generate-news")
# async def generate_news_endpoint(request: Request, 
#                                db: Session = Depends(get_db),
#                                current_user: str = Depends(utils.get_current_user)):
#     try:
#         user = db.query(User).filter(User.username == current_user).first()
#         news_count = db.query(NewsHistory).filter(NewsHistory.user_id == user.id).count()
        
#         if news_count % 5 == 0 and news_count != 0:
#             return JSONResponse(
#                 status_code=403,
#                 content={"message": "Please re-authenticate"}
#             )
            
#         form_data = await request.form()
#         prompt = form_data.get("prompt", "Generate news about")
        
#         generated_text = generate_news(prompt)
        
#         news_item = NewsHistory(user_id=user.id, content=generated_text)
#         db.add(news_item)
#         db.commit()
        
#         return JSONResponse(content={"news": generated_text})
    
#     except Exception as e:
#         db.rollback()
#         return JSONResponse(
#             status_code=500,
#             content={"message": f"News generation failed: {str(e)}"}
#         )

# @app.post("/generate-news")
# async def generate_news_endpoint(request: Request, 
#                                db: Session = Depends(get_db),
#                                current_user: str = Depends(utils.get_current_user)):
#     try:
#         user = db.query(User).filter(User.username == current_user).first()
        
#         if user.generation_count >= 5:
#             # Clear the generation count and force logout
#             user.generation_count = 0
#             db.commit()
#             return JSONResponse(
#                 status_code=403,
#                 content={"message": "Please re-authenticate"}
#             )
            
#         form_data = await request.form()
#         prompt = form_data.get("prompt", "Generate news about")
        
#         generated_text = generate_news(prompt)
        
#         # Update generation count
#         user.generation_count += 1
#         db.commit()
        
#         return JSONResponse(content={"news": generated_text})
    
#     except Exception as e:
#         db.rollback()
#         return JSONResponse(
#             status_code=500,
#             content={"message": f"News generation failed: {str(e)}"}
#         )

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, current_user: str = Depends(utils.get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request})

# Add exception handler
@app.exception_handler(HTTPException)
async def custom_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        return RedirectResponse(url="/login")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})