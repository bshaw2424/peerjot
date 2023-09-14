from wtforms import Form, BooleanField, StringField, TextAreaField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=6, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [validators.DataRequired(
    ), validators.EqualTo('confirm', 'password does not match')])
    confirm = PasswordField('Confirm Password')


class Login(Form):
    username = StringField('Enter username')
    password = PasswordField('Enter Password')


class NoteBlock(Form):
    block_title = StringField(
        'Block Title', [validators.Length(min=4, max=50)])
    block_body = TextAreaField("Block Body", [validators.InputRequired()])
