#!/usr/bin/env python3
import frappe
from mkaguzi.chat_system.setup_chat_system import setup_chat_system

def run_temp_setup():
    # Run setup with admin user
    frappe.set_user("Administrator")
    setup_chat_system()
    frappe.db.commit()
    print("Chat system setup completed!")