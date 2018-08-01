from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    def   q1(arg1,arg2,arg3,arg4):
          print (arg1,arg2,arg3,arg4)
    tu=(1,2,3,4)
    print('extract from tuple \n')
    q1(*tu)
    di={'arg1':1,'arg2':2,'arg3':3,'arg4':4}
    print ('/nextract from dict \n')
    q1(**di)


if __name__ == '__main__':
    hello_world()
