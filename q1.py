from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from datetime import date,datetime, timedelta
import mysql.connector
from functools import wraps
import jwt

#connect to sql database
#create two tables tasks and users
try:
    db = mysql.connector.connect(host='localhost', user='root', password='kali', database='taskdb')
    data_c = db.cursor()
except:
    db = mysql.connector.connect(host="localhost", user="root", password="kali")
    data_c = db.cursor()
    data_c.execute('create database taskdb')
    data_c.execute('use taskdb')
    data_c.execute('create table tasks(id int PRIMARY KEY AUTO_INCREMENT, task varchar(100),due date,status varchar(20));')
    data_c.execute('create table users(uid varchar(200) PRIMARY KEY, permission varchar(10));')
    db.commit()


authorizations = {
    'apikey': {
        'type' : 'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',authorizations=authorizations
)
app.config['SECRET_KEY'] = 'mysecretkey'

ns = api.namespace('todos', description='TODO operations')
apitoken = api.namespace('generateToken', description='Generate API token')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due': fields.Date(required=True, description='Due date of the task'),
    'status': fields.String(required=True, description='Status of the task(Not started, In progress, Finished)'),
})


def readPermission(f):
    '''For providing read access to the user'''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'User ID not found'}, 401
        data_c.execute("select * from users where uid=%s", (token,))
        user = data_c.fetchall()
        if len(user) == 0:
            return {'message': 'Access Denied',
                    'error': 'user with id {} NOT FOUND'.format(token)}, 401
        return f(*args, **kwargs)
    return decorated

def writePermission(f):
    '''For providing write access to the user'''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'User ID not found'}, 401
        data_c.execute("select * from users where uid=%s", (token,))
        user = data_c.fetchall()
        # print("->", user)
        if len(user) == 0 or (len(user) == 1 and user[0][1] != 'write'):
                return {'message': 'Access Denied'}, 403
        return f(*args, **kwargs)
    return decorated


class TodoDAO(object):
    def __init__(self):
        ct = 0
        tasks = []
        data_c.execute('select * from tasks')
        for i in data_c:
            tasks.append({'id': i[0], 'task': i[1], 'due': i[2], 'status': i[3]})
            ct = i[0]
        self.counter = ct
        self.todos = tasks

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))
    
    def create(self, data):
        '''
        create a toda with the given data and add it to the database
        '''
        todo = data
        if(data['status'] == "Finished" or data['status'] == "Not started" or data['status'] == "In progress"):
            todo['id'] = self.counter = self.counter + 1
            self.todos.append(todo)
            param = (data['task'], data['due'],data['status'])
            data_c.execute("insert into tasks(task, due, status) values(%s,%s,%s)", param)
            db.commit()
            return todo
        api.abort(404, "Invalid status {}".format(data['status']))
    
    def update(self, id, data):
        '''
        update the todo corresponding to the identifier given
        '''
        todo = self.get(id)
        if(data['status'] == "Finished" or data['status'] == "Not started" or data['status'] == "In progress"):
            index = 0
            for i in range(len(self.todos)):
                if(self.todos[i]['id'] == id):
                    index = i
                    break
            temp = self.todos[index]['id']
            self.todos[index] = data
            self.todos[index][id] = temp
            print(self.todos[index])
            param = (data['task'], data['due'], data['status'], id)
            data_c.execute("update tasks set task=%s, due=%s, status=%s where id=%s", param)
            db.commit()
            return todo
        api.abort(404, "Invalid status {}".format(data['status']))
        return None
    
    def delete(self, id):
        '''
        delete the todo corresponding to the identifier
        '''
        todo = self.get(id)
        self.todos.remove(todo)
        self.counter -= 1
        data_c.execute("delete from tasks where id=%s", (id,))
        db.commit()


    def finished(self):
        '''
        get all finished tasks
        '''
        l = []
        flag = 0
        for todo in self.todos:
            if todo['status'] == 'Finished':
                l.append(todo)
                flag = 1
        if(flag == 1): 
          return l
        else:
          api.abort(404, "Todo {} doesn't exist".format(id))

    def overdue(self):
        l=[]
        flag = 0
        for todo in self.todos:
            #year, month, day = map(int, todo['due'].split('-'))
            #d1 = datetime.date(year, month, day)
            #x = todo['due']
            #tdate = datetime.strptime(x, "%Y-%m-%d").strftime("%Y-%m-%d")
            #pdate = datetime.date.today().strftime("%Y-%m-%d")
            #d2= datetime.now().date()
            if todo['status'] != 'Finished' and date.today() > todo['due']:
                l.append(todo)
                flag = 1
        if(flag == 1): 
          return l
        else:
          api.abort(404, "Todo {} doesn't exist".format(id))

    def convt_to_date(self, d):
        '''
        Input: date string(d)
        Output: date object
        '''
        nd = list(map(int,d.split('-')))
        return date(nd[0], nd[1], nd[2])
    

    def duedate(self,date):
        l=[]
        flag = 0
        for todo in self.todos:
            if todo['status'] != 'Finished' and todo['due'] == self.convt_to_date(date):
                l.append(todo)
                flag = 1
        if(flag == 1): 
          return l
        else:
          api.abort(404, "Todo {} doesn't exist".format(id))


@apitoken.route('/')
class TokenGenerator(Resource):
    '''Generates the  API token'''
    @apitoken.param('username','Username',_in='query',required=True)
    @apitoken.param('password','Password',_in='query',required=True)
    @apitoken.param('permission','Permission',_in='query',required=True, enum=['read', 'write'])
    def get(self):
        data = request.args
        token = jwt.encode({'user': data['username'], 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        data_c.execute('insert into users values(%s,%s)', (token, data['permission']))
        db.commit()
        return jsonify({'token': token})

DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.todos

    @api.doc(security='apikey')
    @writePermission
    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)
    
    @api.doc(security='apikey')
    @writePermission
    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @api.doc(security='apikey')
    @writePermission
    @ns.doc('update_todo_status')
    @ns.response(204, 'status updated')
    @ns.param('status','Task Status',_in='query',required=True)
    @ns.marshal_with(todo)
    def post(self, id):
        '''Update status of task given its identifier'''
        data = request.args
        todo = DAO.get(id)
        todo['status'] = data['status']
        return DAO.update(id, todo)

    @api.doc(security='apikey')
    @writePermission
    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

@ns.route('/finished')
class finished(Resource):
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('get_finished_todo')
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch all finished todo'''
        return DAO.finished()

@ns.route('/overdue')
class overdue(Resource):
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('overdue_todo')
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch all overdue todo'''
        return DAO.overdue()

@ns.route('/<string:date>')
class overdue(Resource):
    @api.doc(security='apikey')
    @readPermission
    @ns.doc('overduedate_todo')
    @ns.marshal_with(todo)
    def get(self,date):
        '''Fetch all overdue todo on a particular date'''
        return DAO.duedate(date)

if __name__ == '__main__':
    app.run(host="localhost", port=9000,debug=True)