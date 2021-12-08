# Survey Web

## Set up
```
pip3 install -r requirements.txt
```

## Project structure
```
{ROOT}
└── app
    ├── api
    │   ├── __pycache__
    │   └── v1 
    │       ├── endpoints # folder contains all api route
    │       │   └── __pycache__
    │       └── __pycache__
    ├── core # folder contains middlewares
    │   └── __pycache__
    ├── crud # folder contains crud for database
    │   └── __pycache__
    ├── db # folder contains database 
    │   └── __pycache__
    ├── models # folder contains object (read pydantic for more info)
    │   └── __pycache__
    └── __pycache__

```

## Run 
- In {ROOT}, run application server:
```
uvicorn app.main:app --reload
```

- For API documentations:
```
localhost:8000/docs
```
