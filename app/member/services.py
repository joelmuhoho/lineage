from app.extensions import db
from app.models import Member, Relationship
from app.services.service_base import service_response
from flask_login import current_user
from typing import Tuple

class MemberService:
    """Service class for managing family members."""

    @staticmethod
    def get_member(member_id: int) -> Tuple[dict, int]: #TODO: get multiple members by id in a list [id1, id2, id3] -> [member1, member2, member3]
        """
        Retrieves a family member by their member ID.

        Args:
            member_id (int): The ID of the member to retrieve.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If the member is found, the dictionary will include the
            member data with a success message. If not found, it will contain an error message.
        """

        try:
            member = db.session.query(Member).filter_by(member_id=member_id).first()

            if not member:
                return service_response(404, "Member not found", "warning", None)
            elif not MemberService.is_member_accessible_by_user(member):
                return service_response(403, "You do not have permission to access this member", "danger", None)
            return service_response(200, "Member retrieved successfully", "success", member)
        except Exception as e:
            # TODO: log error
            return service_response(500, "Error retrieving member", "danger", None)

    @staticmethod
    def is_member_accessible_by_user(member: Member) -> bool:
        """
        Checks if the current user has permission to access a member.

        Args:
            member (Member): The member to check.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        return member.family_id in [family.family_id for family in current_user.families]

    @staticmethod
    def create_member(**member_data) -> Tuple[dict, int]:
        """
        Creates a new family member.

        Args:
            **member_data: A dictionary with member data.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            new_member = Member(**member_data)
            db.session.add(new_member)
            db.session.commit()
            return service_response(201, "Member created successfully", "success", new_member)
        except Exception as e:
            db.session.rollback()
            # TODO: log error
            return service_response(500, "Error creating member", "danger", None)

    @staticmethod
    def get_member_siblings(member_id: int) -> Tuple[dict, int]:
        """
        Retrieves all siblings of a family member by their member ID.

        Args:
            member_id (int): The ID of the member.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If siblings are found, the dictionary will include the
            sibling data with a success message. If not found, it will contain an error message.
        """
        try:
            data, status = MemberService.get_member(member_id)
            if status != 200:
                return data, status
            current_member = data.get('data')

            siblings = db.session.query(Member).where(
                Member.mother != None,
                Member.mother == current_member.mother,
                Member.father != None,
                Member.father == current_member.father,
                Member.member_id != current_member.member_id,
            ).order_by(Member.birthdate).all()

            if not siblings:
                return service_response(200, "No siblings found", "warning", None)
            return service_response(200, "Siblings retrieved successfully", "success", siblings)
        except Exception as e:
            # TODO: log error
            return service_response(500, "Error retrieving siblings", "danger", None)

    @staticmethod
    def get_member_children(member_id: int) -> Tuple[dict, int]:
        """
        Retrieves all children of a family member by their member ID.

        Args:
            member_id (int): The ID of the member.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If children are found, the dictionary will include the
            child data with a success message. If not found, it will contain an error message.
        """
        try:
            data, status = MemberService.get_member(member_id)
            if status != 200:
                return data, status
            current_member = data.get('data')

            children = db.session.query(Member).where(
                db.or_(
                Member.mother == current_member.member_id,
                Member.father == current_member.member_id
                )
            ).order_by(Member.birthdate).all()

            if not children:
                return service_response(200, "No children found", "warning", None)
            return service_response(200, "Children retrieved successfully", "success", children)
        except Exception as e:
            # TODO: log error
            return service_response(500, "Error retrieving children: ", "danger", None)

    @staticmethod
    def get_member_spouses(member_id: int) -> Tuple[dict, int]:
        """
        Retrieves all spouses of a family member by their member ID.

        Args:
            member_id (int): The ID of the member.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary with the response message and
            the HTTP status code. If spouses are found, the dictionary will include the
            spouse data with a success message. If not found, it will contain an error message.
        """
        try:
            data, status = MemberService.get_member(member_id)
            if status != 200:
                return data, status
            current_member = data.get('data')

            spouses_relationships = db.session.query(Relationship).where(
                db.or_(
                Relationship.member_id_1==current_member.member_id,
                Relationship.member_id_2==current_member.member_id,
                ),
                Relationship.relationship_type=='spouse'
                ).all()

            spouses = []
            for relationship in spouses_relationships:
                if relationship.member1 != current_member:
                    spouses.append(relationship.member1)
                else:
                    spouses.append(relationship.member2)

            if not spouses:
                return service_response(200, "No spouses found", "warning", None)
            return service_response(200, "Spouses retrieved successfully", "success", spouses)
        except Exception as e:
            # TODO: log error
            return service_response(500, "Error retrieving spouses", "danger", None)

    @staticmethod
    def update_member(member_id: int, **member_data) -> Tuple[dict, int]:
        """
        Updates a family member's information.

        Args:
            member_id (int): The ID of the member to update.
            **member_data: A dictionary with updated member data.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            data, status = MemberService.get_member(member_id)
            if status != 200:
                return data, status
            member = data.get('data')

            for key, value in member_data.items():
                setattr(member, key, value)

            db.session.commit()
            return service_response(200, "Member updated successfully", "success", member)
        except Exception as e:
            db.session.rollback()
            # TODO: log error
            return service_response(500, "Error updating member", "danger", None)

    @staticmethod
    def delete_member(member_id: int) -> Tuple[dict, int]:
        """
        Deletes a family member.

        Args:
            member_id (int): The ID of the member to delete.

        Returns:
            Tuple[dict, int]: A tuple containing a dictionary and HTTP status code.
        """
        try:
            data, status = MemberService.get_member(member_id)
            if status != 200:
                return data, status
            member = data.get('data')

            db.session.delete(member)
            db.session.commit()
            return service_response(200, "Member deleted successfully", "success", None)
        except Exception as e:
            db.session.rollback()
            # TODO: log error
            return service_response(500, "Error deleting member", "danger", None)

class RelationshipService:
    """Service class for managing relationships between family members."""

    @staticmethod
    def create_relationship(member_id_1: int, member_id_2: int, relationship_type: str) -> Tuple[dict, int]:
        try:
            member1 = db.session.query(Member).get(member_id_1)
            member2 = db.session.query(Member).get(member_id_2)

            if not member1 or not member2:
                return service_response(404, "One or both members not found", "warning", None)

            new_relationship = Relationship(
                member_id_1=member_id_1,
                member_id_2=member_id_2,
                relationship_type=relationship_type
            )
            db.session.add(new_relationship)
            db.session.commit()
            return service_response(201, "Relationship created successfully", "success", new_relationship)
        except Exception as e:
            db.session.rollback()
            # TODO: log error
            return service_response(500, "Error creating relationship", "danger", None)