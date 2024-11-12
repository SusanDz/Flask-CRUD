from webapp import create_app
from waitress import serve

app = create_app()

mode ="dev"

if __name__ == '__main__':
    if mode == "dev":
        app.run(debug=True)
    else:
        serve(app, host='0.0.0.0', port=8080)