from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

locations = [('Bahen Centre', 'Bahen Centre'), ('Convocation Hall', 'Convocation Hall'),
             ('Robarts', 'Robarts'), ('Gerstein', 'Gerstein'),
             ('Hart House', 'Hart House'), ('King’s Circle', 'King’s Circle'),
             ('Instructional Centre', 'Instructional Centre'), ('Student Centre', 'Student Centre'),
             ('Environmental Science Building', 'Environmental Science Building'),
             ('Bladen Wing', 'Bladen Wing'), ('Tim Hortons', 'Tim Hortons'),
             ('UTSC Library', 'UTSC Library'), ('Pan-Am Centre', 'Pan-Am Centre')]


class LoginForm(Form):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
    location = SelectField('location', choices=locations,
                           validators=[DataRequired()])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if (not Form.validate(self)):
            return False
        if (self.nickname.data == self.original_nickname):
            return True
        user = User.query.filter_by(nickname=nickname.data).first()
        if (user != None):
            self.nickname.errors.append('This nickname is already in use. Please choose another one')
            return False
        return True


class LendItem(Form):
    item_name = StringField('item_name', validators=[DataRequired()])
    item_location = SelectField('item_location', choices=locations,
                                validators=[DataRequired()])
    item_time_pickup = StringField('item_time_pickup', validators=[DataRequired()])


class BorrowItem(Form):
    item_name = StringField('item_name', validators=[DataRequired()])
    item_location = SelectField('item_location', choices=locations,
                                validators=[DataRequired()])
    item_time_pickup = StringField('item_time_pickup', validators=[DataRequired()])
