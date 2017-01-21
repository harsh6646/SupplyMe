from app import db
from hashlib import md5


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(140))
    location = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(1000))

    sell_items = db.relationship('Lend', backref='lister', lazy='dynamic')
    borrow_items = db.relationship('Borrow', backref='lister', lazy='dynamic')

    @staticmethod
    def make_unique_nickname(nickname):
        if (User.query.filter_by(nickname=nickname).first() is None):
            return nickname
        version = 2
        while (True):
            new_nickname = nickname + str(version)
            if (User.query.filter_by(nickname=new_nickname).first() is None):
                break
            version += 1
        return new_nickname

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def first_name(self, nickname):
        # split at space in name
        name = nickname.split(' ')
        return name[0]

    def avatar(self, size):
        return('http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size))

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Lend(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Item Details
    item_name = db.Column(db.String(160))
    item_location = db.Column(db.String(160))
    item_time_pickup = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Lend %r>' % (self.item_name)


class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Item Details
    item_name = db.Column(db.String(160))
    item_location = db.Column(db.String(160))
    item_time_pickup = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Borrow %r>' % (self.item_name)
