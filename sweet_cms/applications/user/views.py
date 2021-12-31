# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
from flask_login import login_required
from sweet_cms.applications.eventy.models import Programme, ProgrammeFile
import subprocess
import json
blueprint = Blueprint("user", __name__, url_prefix="/users", static_folder="./static")


@blueprint.route("/")
@login_required
def members():
    """List members."""
  
    
    return render_template("users/members.html")
     
       
   

@blueprint.route('live_stream/', methods=['GET', 'POST'])
@login_required
def live_streaming():
      programme= Programme.query.all()
      return render_template('users/live_strem.html', programme=programme)

@blueprint.route("/profile")
@login_required
def profile():
    """List members."""
    form=["raja"]
    return render_template("users/profile.html",form=form)