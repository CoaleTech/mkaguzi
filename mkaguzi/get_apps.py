import frappe

def get_installed_apps():
    print("Installed apps:", frappe.get_installed_apps())