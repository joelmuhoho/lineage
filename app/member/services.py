from app.extensions import db
from app.models import Member, Relationship
from app.services.service_base import service_response
from typing import Tuple

class MemberService:
    """Service class for managing family members."""

    @staticmethod
    def get_member(member_id: int) -> Tuple[dict, int]:
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
            return service_response(200, "Member retrieved successfully", "success", member)
        except Exception as e:
            return service_response(500, "Error retrieving member: " + str(e), "danger", None)

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
            return service_response(500, "Error creating member: " + str(e), "danger", None)


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
            return service_response(500, "Error creating relationship: " + str(e), "danger", None)