import web.app


if __name__ == "__main__":
    web.app.run_dev()
else:
    app = application = web.app.get_app()


