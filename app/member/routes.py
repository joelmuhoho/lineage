from . import bp
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import current_user, login_required
from .forms import MemberForm
from app.models import Member, Relationship
from app.utils.constants import RelationshipConstants
from .services import MemberService, RelationshipService



@bp.route('/member/<member_id>/spouse', methods=['GET', 'POST'])
@login_required
def add_spouse(member_id):
    form = MemberForm(add_relative_mode=RelationshipConstants.Spouse)

    data, status = MemberService.get_member(member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        flash(message, category)
        return redirect(url_for('family.index'))

    member1 = data.get('data')
    family_id = member1.family_id
    title = f'Adding spouse of {member1.first_name} {member1.last_name}'

    if form.validate_on_submit():
        data, status = MemberService.create_member(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            family_id=family_id,
            alive=eval(form.alive.data),
            deathdate=form.deathdate.data,
            )
        newMember, message, category = data.get('data'), data.get('message'), data.get('category')
        if status != 201:
            flash(message, category)
            return redirect(url_for('family.index'))

        data, status = RelationshipService.create_relationship(member1.member_id,
                                                newMember.member_id, form.relationship.data)
        message, category = data.get('message'), data.get('category')
        if status != 201:
            flash(message, category)
            return redirect(url_for('family.index'))

        flash(f'{newMember.first_name} added as spouse to {member1.first_name} {member1.last_name}', 'success')
        return redirect(url_for('family.index'))

    return render_template('add_member.html', title=title, form=form, families=current_user.families, member1=member1)

@bp.route('/member/<member_id>/<spouse_id>/child', methods=['GET', 'POST'])
@login_required
def add_child(member_id, spouse_id):
    form = MemberForm(add_relative_mode=RelationshipConstants.Child)
    father = ''
    mother = ''

    data, status = MemberService.get_member(member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        flash(message, category)
        return redirect(url_for('family.index'))

    member1 = data.get('data')

    data, status = MemberService.get_member(spouse_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        flash(message, category)
        return redirect(url_for('family.index'))

    spouse = data.get('data')

    if member1.gender == 'Male':
        father = member1
        mother = spouse
    else:
        mother = member1
        father = spouse

    family_id = member1.family_id

    if form.validate_on_submit():
        data, status = MemberService.create_member(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            family_id=family_id,
            alive=eval(form.alive.data),
            deathdate=form.deathdate.data,
            father=father.member_id,
            mother=mother.member_id
            )
        newMember, message, category = data.get('data'), data.get('message'), data.get('category')
        if status != 201:
            flash(message, category)
            return redirect(url_for('family.index'))

        data, status = RelationshipService.create_relationship(spouse.member_id, newMember.member_id, form.relationship.data)
        message, category = data.get('message'), data.get('category')
        if status != 201:
            flash(message, category)
            return redirect(url_for('family.index'))

        flash(f'{newMember.first_name} {newMember.last_name} added as child to {member1.first_name} {member1.last_name} and {spouse.first_name} {spouse.last_name}', 'success')
        return redirect(url_for('family.index'))
    return render_template('add_member.html', title='Add child', form=form, families=current_user.families, member1=member1)

@bp.route('/member/<member_id>', methods=['GET'])
@login_required
def member_profile(member_id):
    data, status = MemberService.get_member(member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        flash(message, category)
        return redirect(url_for('family.index'))

    member = data.get('data')

    data, status = MemberService.get_member(member.mother)
    mother = data.get('data')

    data, status = MemberService.get_member(member.father)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        flash(message, category)

    father = data.get('data')

    data, status = MemberService.get_member_siblings(member_id)
    siblings, message, category = data.get('data'), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)

    # TODO: include step siblings

    data, status = MemberService.get_member_children(member_id)
    children, message, category = data.get('data'), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)

    data, status = MemberService.get_member_spouses(member_id)
    spouses, message, category = data.get('data'), data.get('message'), data.get('category')
    if status != 200:
        flash(message, category)

    return render_template('member_profile.html', title=f'{member.first_name} information ',
                           member=member,
                           father=father,
                           mother=mother,
                           siblings=siblings,
                           spouses=spouses,
                           children=children)

@bp.route('/update_member/<member_id>', methods=['GET', 'POST'])
@login_required
def update_member(member_id):
    form = MemberForm()

    data, status = MemberService.get_member(member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        flash(message, category)
        return redirect(url_for('family.index'))

    member = data.get('data')

    if form.validate_on_submit():
        data, status = MemberService.update_member(
            member_id=member.member_id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birthdate=form.birthdate.data,
            gender=form.gender.data,
            deathdate=form.deathdate.data,
            alive=eval(form.alive.data),
            )
        message, category = data.get('message'), data.get('category')
        if status != 200:
            flash(message, category)
            return redirect(url_for('member.update_member', member_id=member.member_id))

        flash(message, category)
        return redirect(url_for('member.member_profile', member_id=member.member_id))

    return render_template('update_member.html', title=f'Update {member.first_name} information ', form=form, member=member)

@bp.route('/delete_member/<member_id>')
@login_required
def delete_member(member_id):
    data, _ = MemberService.delete_member(member_id)
    message, category = data.get('message'), data.get('category')
    flash(message, category)
    return redirect(url_for('family.index'))

# API call
@bp.route('/member/spouses', methods=['POST', 'GET'])
@login_required
def get_spouse():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    spousesList = []
    data, status = MemberService.get_member_spouses(member_id=int(data['member1_id']))
    if status != 200:
        message, category = data.get('message'), data.get('category')
        return make_response(jsonify({category: message}), status)
    spouses = data.get('data')
    print(f"spouses: {spouses} \n status: {status}")
    for spouse in spouses:
        spousesList.append(spouse.to_dict())
    if current_user.is_authenticated:
        login = {'authenticated': True}
    else:
        login = {'authenticated': False}
    response =  make_response(jsonify(spousesList, login), 200)
    return response

@bp.route('/member/children', methods=['POST', 'GET'])
@login_required
def get_children():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    elif "spouse_id" not in data:
        return make_response(jsonify({"error": "Missing spouse_id"}), 400)

    member_id = int(data['member1_id'])
    spouse_id = int(data['spouse_id'])
    parent_ids = [member_id, spouse_id]

    data, status = MemberService.get_member_children(member_id=member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        return make_response(jsonify({category: message}), status)

    children = data.get('data')
    childrenList = []

    if children:
        for child in children:
            if child.father in parent_ids and child.mother in parent_ids:
                childrenList.append(child.to_dict())

    if current_user.is_authenticated:
        login = {'authenticated': True}
    else:
        login = {'authenticated': False}
    response =  make_response(jsonify(childrenList, login), 200)
    return response

@bp.route('/member/nuclear', methods=['POST', 'GET'])
@login_required
def get_nuclear():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    member_id = int(data.get('member1_id'))
    parent_ids = [member_id]
    nuclear_family = {"spouses": [], "children": []}

    data, status = MemberService.get_member_spouses(member_id=member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        return make_response(jsonify({category: message}), status)
    spouses = data.get('data')

    for spouse in spouses:
        parent_ids.append(spouse.member_id)
        nuclear_family["spouses"].append(spouse.to_dict())


    data, status = MemberService.get_member_children(member_id=member_id)
    if status != 200:
        message, category = data.get('message'), data.get('category')
        return make_response(jsonify({category: message}), status)

    children = data.get('data')

    if children:
        for child in children:
            if child.father in parent_ids and child.mother in parent_ids:
                nuclear_family["children"].append(child.to_dict())

    response =  make_response(jsonify(nuclear_family), 200)
    return response