import os
import shutil

from stem.control import Controller
from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
  return "<h1>Hi Grandma!</h1>"


print(' * Connecting to tor')

with Controller.from_port() as controller:
  controller.authenticate()

  hidden_service_dir = os.path.join(controller.get_conf('DataDirectory', '/tmp'), 'hello_world')



  print(" * Creating our hidden service in %s" % hidden_service_dir)
  result = controller.create_hidden_service(hidden_service_dir, 80, target_port = 5000)


  if result.hostname:
    print(" * Our service is available at %s, press ctrl+c to quit" % result.hostname)
  else:
    print(" * Unable to determine our service's hostname, probably due to being unable to read the hidden service directory")

  try:
    app.run()
  finally:


    print(" * Shutting down our hidden service")
    controller.remove_hidden_service(hidden_service_dir)
    shutil.rmtree(hidden_service_dir)