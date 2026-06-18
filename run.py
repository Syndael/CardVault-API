from app.app import create_app

app = create_app()

if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, use_reloader=debug)