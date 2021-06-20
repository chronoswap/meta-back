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


@app.before_first_request
def awakeListener():
    import os
    os.system('python3 ./eventListener.py &')


if __name__ == '__main__':
    app.run()
