from src import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["ENV"] == "development", port=app.config["PORT"])
