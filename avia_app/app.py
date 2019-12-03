from avia_app.application import create_app

app = create_app('settings')
if __name__ == '__main__':
    app.run()
