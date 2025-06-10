from . import link_bp
from flask import flash, redirect, url_for
from app.family.services import FamilyService
from .services import LinkService
from flask_login import login_required, current_user

@link_bp.route('/create_link/<family_id>', methods=['POST', 'GET'])
@login_required
def create_link(family_id):
    family_service = FamilyService()
    data, status = family_service.get_family_by_id(family_id)
    family, message, category = data.get('data'), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)
        return redirect(url_for('user.user_profile'))
    elif not family:
        flash(message, category)
        return redirect(url_for('user.user_profile'))

    if not family_service.family_belongs_to_user(family_id=family_id, user_id=current_user.user_id):
        flash('You are not allowed to create a link for this family', 'info')
        return redirect(url_for('user.user_profile'))

    link_service = LinkService()
    data, status = link_service.create_link(family)
    message, category = data.get('message'), data.get('category')
    flash(message, category)
    return redirect(url_for('user.user_profile'))


@link_bp.route('/delete_link/<link_id>')
@login_required
def delete_link(link_id):
    link_service = LinkService()
    data, _ = link_service.delete_link(link_id=link_id)
    message, category = data.get('message'), data.get('category')

    flash(message, category)
    return redirect(url_for('user.user_profile'))