from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user

from sweet_cms.extensions import login_manager
from sweet_cms.applications.base.forms import LoginForm
from sweet_cms.applications.user.forms import RegisterForm
from sweet_cms.applications.user.models import User
from sweet_cms.utils import flash_errors
blueprint = Blueprint("base", __name__, static_folder="./static", template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("base.home"))


#login    
@blueprint.route("/login/" , methods=["GET", "POST"])
def login():
    """Login."""
    if request.method=="GET":
         form = LoginForm()
         return render_template("public/login.html", form=form)
  
    # Handle logging in
    elif request.method == "POST":
         form = LoginForm(request.form)
         if form.validate_on_submit():
             login_user(form.user)
             flash("You are logged in.", "success")
             redirect_url = request.args.get("next") or url_for("user.members")
             return redirect(redirect_url)
         else:
             flash_errors(form)
    return render_template("public/home.html")

      


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("base.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
