# -*- coding: utf-8 -*-
# Copyright (c) 2025, CoaleTech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _

# DocType configuration for Chat Room
def get_data():
	return {
		'fieldname': 'room_id',
		'non_standard_fieldnames': {
			'Chat Message': 'room',
			'Chat Participant': 'room'
		},
		'transactions': [
			{
				'label': _('Messages'),
				'items': ['Chat Message']
			},
			{
				'label': _('Participants'),
				'items': ['Chat Participant']
			}
		]
	}