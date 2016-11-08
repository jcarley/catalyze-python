import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

import falcon
import users

api = application = falcon.API()

db = os.path.join(curpath, 'data.db')
users = users.UserResource(db)

api.add_route('/user/{userID}', users)