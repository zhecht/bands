from flask import Flask, render_template
import os
import controllers

app = Flask(__name__, template_folder='views')

app.register_blueprint(controllers.main)
app.register_blueprint(controllers.stats)

app.secret_key = os.urandom(24)
#app.secret_key = "\x97\xfe\x036\x02\xeb\xc1\xfa\xdde\x14 \x15\xd6\xde\xac,\xc8rG\x11\xb6(H"

if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
    #app.run(host='0.0.0.0', port=80, debug=True)
