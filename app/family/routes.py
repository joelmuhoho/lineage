from flask import render_template, redirect, url_for, flash, session
from flask_login import current_user, login_required
from . import bp
from .forms import CreateFamilyForm
from app.member.forms import MemberForm
from app.auth.services import AuthService
from .services import FamilyService
from app.link.services import LinkService
from app.member.services import MemberService


@bp.route('/family/<family_id>')
@bp.route('/family')
def index(family_id=0):
    families = []
    if not family_id == 0:
        AuthService.set_current_family_id(family_id)

        current_family_id = session.get("current_family_id")
        if current_family_id is not None:
            data, status = FamilyService.get_family_by_id(current_family_id)
            family, message, category = data.get('data'), data.get('message'), data.get('category')
            if status != 200:
                flash(message, category)
            elif not family:
                flash(message, category)
            else:
                families = [family]

    elif current_user.is_authenticated:
        data, status = FamilyService.get_user_families(current_user.user_id)
        families, message, category = data.get('data'), data.get('message'), data.get('category')
        if status != 200:
            flash(message, category)
        elif not families:
            flash(message, category)

    return render_template('family.html', families=families)


@bp.route('/create-family', methods=['GET', 'POST'])
@login_required
def create_family():
    form = CreateFamilyForm()
    member_form = MemberForm()
    member_service = MemberService()

    if form.validate_on_submit() and member_form.validate_on_submit():
        data, status = FamilyService.create_family(form.name.data, current_user.user_id)
        family, message, category = data.get('data'), data.get('message'), data.get('category')
        if status != 201:
            flash(message, category)
            return redirect(url_for('family.index'))

        data, status = member_service.create_member(
            first_name=member_form.first_name.data,
            last_name=member_form.last_name.data,
            birthdate=member_form.birthdate.data,
            gender=member_form.gender.data,
            family_id=family.family_id,
            alive=eval(member_form.alive.data),
            deathdate=member_form.deathdate.data,
            root=True
        )
        return redirect(url_for('family.index'))

    return render_template('create_family.html', title='Create Family', form=form, memberForm=member_form)

@bp.route('/family/delete/<family_id>')
@login_required
def delete_family(family_id):
    is_family_owner = FamilyService.family_belongs_to_user(family_id=id, user_id=current_user.user_id)
    if not is_family_owner:
        flash('You are not allowed to delete this family', 'info')
        return redirect(url_for('user.user_profile'))

    data, _ = FamilyService.delete_family(family_id=family_id)
    message, category = data.get('message'), data.get('category')

    flash(message, category)
    return redirect(url_for('user.user_profile'))

@bp.route('/create_link/<family_id>', methods=['POST', 'GET'])
@login_required
def create_link(family_id):
    data, status = FamilyService.get_family_by_id(family_id)
    family, message, category = data.get('data'), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)
        return redirect(url_for('user.user_profile'))
    elif not family:
        flash(message, category)
        return redirect(url_for('user.user_profile'))

    if not FamilyService.family_belongs_to_user(family_id=family_id, user_id=current_user.user_id):
        flash('You are not allowed to create a link for this family', 'info')
        return redirect(url_for('user.user_profile'))

    data, status = LinkService.create_link(family)
    message, category = data.get('message'), data.get('category')
    flash(message, category)
    return redirect(url_for('user.user_profile'))


@bp.route('/delete_link/<link_id>')
@login_required
def delete_link(link_id):
    data, _ = LinkService.delete_link(link_id=link_id)
    message, category = data.get('message'), data.get('category')

    flash(message, category)
    return redirect(url_for('user.user_profile'))
