"""
Standardized API response builder
"""
from typing import Any, Dict, Optional, List
from frappe.utils import now
import frappe

class APIResponseBuilder:
    """Builds standardized API responses"""

    @staticmethod
    def success(
        data: Any,
        message: Optional[str] = None,
        meta: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Build a success response

        Args:
            data: Response data
            message: Optional success message
            meta: Optional metadata

        Returns:
            Standardized success response
        """
        response = {
            'success': True,
            'data': data,
            'timestamp': now()
        }

        if message:
            response['message'] = message

        if meta:
            response['meta'] = meta

        return response

    @staticmethod
    def error(
        error_message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Build an error response

        Args:
            error_message: User-friendly error message
            error_code: Optional error code
            details: Optional error details

        Returns:
            Standardized error response
        """
        response = {
            'success': False,
            'error': error_message,
            'timestamp': now()
        }

        if error_code:
            response['error_code'] = error_code

        if details:
            response['details'] = details

        # Log the error
        frappe.log_error(f"API Error: {error_message}", error_code or "API Error")

        return response

    @staticmethod
    def paginated(
        data: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a paginated response

        Args:
            data: List of items
            total: Total number of items
            page: Current page number
            page_size: Items per page
            message: Optional message

        Returns:
            Standardized paginated response
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        response = {
            'success': True,
            'data': data,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'timestamp': now()
        }

        if message:
            response['message'] = message

        return response