### description:
- DB: PostgreSQL
- python 3.8.0

### To run tests:
Type: `pytest`

#### Running the app:
1. Extract files to the location where you want the `apy` to be extracted
2. Open terminal
3. Change the current working directory to the extracted `apy` directory
4. create virtual environment
5. source it: `source venv_name/bin/activate`
6. Type `pip install -r requirements.txt` in terminal to install requirements
7. Migrate db: `flask db migrate -m "users table"`
8. Seed: `flask seed run` 
9. Start server: `flask run`

### curl commands:

1: signup user
`curl -i -X POST -H "Content-Type: application/json" -d '{"username": "admin","password": "admin", "is_admin": "True"}'  http://127.0.0.1:6767/signup`

2: obtain token
`curl -u admin:admin -i -X POST http://127.0.0.1:6767/token`

3: add
`curl -u token:whatever -i -X POST -H "Content-Type: application/json" -d '{"integer": 2}' http://127.0.0.1:6767/add`

4: calculate
`curl -u token:whatever -i -X GET -H "Content-Type: application/json" http://127.0.0.1:6767/calculate`

6: history
`curl -u token:whatever -i -X GET -H "Content-Type: application/json"  http://127.0.0.1:6767/history`

5: reset
`curl -u token:whatever -i -X POST -H "Content-Type: application/json" -d '{"integer": 2}' http://127.0.0.1:6767/reset`
