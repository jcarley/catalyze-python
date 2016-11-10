import sys
import os

curpath = os.path.dirname(__file__)
if(curpath not in sys.path):
    sys.path.append(curpath)

import falcon
import users
import auth

api = application = falcon.API()

db = os.path.join(curpath, 'data.db')

authcheck = auth.Authorizer(db)

userResource = users.UserResource(db, authcheck)
api.add_route('/user', userResource)

authResource = auth.AuthResource(db, authcheck)
api.add_route('/auth', authResource)

baseResource = users.BaseResource(db, authcheck)
api.add_route('/', baseResource)
