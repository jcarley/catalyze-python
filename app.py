import sys
import os

sys.path.append(os.path.dirname(__file__))

import falcon
import uresource

api = application = falcon.API()

users = uresource.UserResource()
api.add_route('/user', users)