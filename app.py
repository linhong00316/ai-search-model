from app import app

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0',port='10086')
