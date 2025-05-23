from . import bp
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import current_user, login_required
from app.extensions import db
from .forms import MemberForm
from app.models import Member, Relationship
from app.utils.constants import RelationshipConstants
from .services import MemberService, RelationshipService


def add_root(family_id, memberForm={}):
    if memberForm:
        data, status = MemberService.create_member(
            first_name=memberForm.first_name.data,
            last_name=memberForm.last_name.data,
            birthdate=memberForm.birthdate.data,
            gender=memberForm.gender.data,
            root=True,
            family_id=family_id,
            alive=eval(memberForm.alive.data),
            deathdate=memberForm.deathdate.data)

        newMember, message, category = data.get('member'), data.get('message'), data.get('category')

        if status != 201:
            flash(message, category)
            return redirect(url_for('family.create_family'))

        flash(f'{newMember.first_name} {newMember.last_name} added as a root Member', 'success')
        return redirect(url_for('family.index'))

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
    member = Member.query.filter_by(member_id=member_id).first()
    # user deleting member should be in sane family as member
    currentUserFamilyIds = [family.family_id for family in current_user.families ]
    if member and member.family_id in currentUserFamilyIds:
        db.session.delete(member)
        db.session.commit()
        flash(f'{member.first_name} has been Deleted', 'success')
        return redirect(url_for('family.index'))
    flash('Not allowed to Delete', 'danger')
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
    spouses = Relationship.query.filter_by(member_id_1=int(data['member1_id']), relationship_type='spouse').all()
    for spouse in spouses:
        spouse_member = Member.query.filter_by(member_id=spouse.member_id_2).first()
        spouse_member = spouse_member.__dict__
        del spouse_member['_sa_instance_state']
        spousesList.append(spouse_member)
    if current_user.is_authenticated:
        login = {'authenticated': True}
    else:
        login = {'authenticated': False}
    response =  make_response(jsonify(spousesList, login), 200)
    return response

# return child/children
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
    member1 = Member.query.filter_by(member_id=data['member1_id']).first()
    spouse = Member.query.filter_by(member_id=data['spouse_id']).first()
    if member1.gender == 'Male':
        father = member1
        mother = spouse
    else:
        mother = member1
        father = spouse
    childrenList = []
    fatherMotherRelation = Relationship.query.filter_by(member_id_1=member1.member_id, member_id_2=spouse.member_id).first()
    fatherMotherRelation = fatherMotherRelation.relationship_type
    if fatherMotherRelation == 'spouse':
        children = Relationship.query.filter_by(member_id_1=spouse.member_id, relationship_type='child').all()
        for child in children:
            child_member = Member.query.filter_by(member_id=child.member_id_2).first()
            child_member = child_member.__dict__
            del child_member['_sa_instance_state']
            childrenList.append(child_member)
        if current_user.is_authenticated:
            login = {'authenticated': True}
        else:
            login = {'authenticated': False}
        response =  make_response(jsonify(childrenList, login), 200)
        return response

# @bp.route('/member/nuclear', methods=['POST', 'GET'])
@login_required
def get_nuclear():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    nuclear_family = {"spouses": [], "children": []}
    spouses = Relationship.query.filter_by(member_id_1=int(data['member1_id']), relationship_type='spouse').all()
    children = Relationship.query.filter_by(member_id_1=int(data['member1_id']), relationship_type='child').all()
    for spouse in spouses:
        spouse_member = Member.query.filter_by(member_id=spouse.member_id_2).first()
        spouse_member = spouse_member.__dict__
        del spouse_member['_sa_instance_state']
        nuclear_family['spouses'].append(spouse_member)
    for child in children:
        child_member = Member.query.filter_by(member_id=child.member_id_2).first()
        child_member = child_member.__dict__
        del child_member['_sa_instance_state']
        nuclear_family['children'].append(child_member)
    response =  make_response(jsonify(nuclear_family), 200)
    return response
