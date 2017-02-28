import Base
import DBM
import sys

class LoginHandler(Base.BaseHandler):
    def get(self):
        # create rock user if no users are in the database
        user = DBM.User.query(ancestor=DBM.UserKey("rock")).fetch(1)
        if len(user) == 0:
            newUser = DBM.User(parent=DBM.UserKey("rock"),
                               username="rock", password="cafe")
            newUser.put()

        self.session['currentPassword'] = ''
        template = Base.JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

    def post(self):

        try:
            self.session['currentPassword'] = self.request.get("password")
            self.session['username'] = self.request.get("username")
        except:
            self.redirect('/')

        if not self.check_login(): return
        self.redirect('manage.html')

