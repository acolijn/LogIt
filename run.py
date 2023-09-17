from app import create_app

print("Executing run.py")

app = create_app('config.Config')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
