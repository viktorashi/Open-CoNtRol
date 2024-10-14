from wtforms import  StringField, HiddenField, SelectField, FieldList, FormField, SubmitField,  validators
from flask_wtf import FlaskForm

class ReactionInputForm(FlaskForm):
    ec_left = StringField('Left Side', validators=[validators.DataRequired(), validators.Length(min=1, max=256, message='Less than 265 chars allowed!')], render_kw={"size" : "20" , "maxlength": "64", "placeholder": "∅", "spellcheck": "false"})
    ec_dir = SelectField('Direction', choices=[('left', '←'), ('both', '⇌'), ('right', '→')], default='both')
    ec_right = StringField('Right Side', validators=[validators.DataRequired(), validators.Length(min=1, max=256, message='Less than 265 chars allowed!')], render_kw={ "size" : "20" ,"maxlength": "64", "placeholder": "∅", "spellcheck": "false"})

class DynamicReactionForm(FlaskForm):
    ecuatiiCount = HiddenField('Ecuatii Count')
    reactions = FieldList(FormField(ReactionInputForm), min_entries=0)  # Start with one reaction by default
    submit = SubmitField('Generate Graph')
