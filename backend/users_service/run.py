from app import create_app;

app = create_app();

if __name__ == '__main__':
    # -> modificar el host correspondiente (ip fija?)
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    );