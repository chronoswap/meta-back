from flask import Flask
from bp_generic import genericBlueprint
from bp_manage import manageBlueprint
from bp_getter import getterBlueprint
from bp_setter import setterBlueprint


app = Flask(__name__)
app.register_blueprint(genericBlueprint)
app.register_blueprint(manageBlueprint)
app.register_blueprint(getterBlueprint)
app.register_blueprint(setterBlueprint)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run()
