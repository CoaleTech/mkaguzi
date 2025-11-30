import frappe

def check_doctypes():
    # Check if doctypes exist
    doctypes = ['Chat AI Model Registry', 'Chat Room', 'Chat Message', 'Chat Participant', 'Audit Engagement', 'Audit Finding']
    for dt in doctypes:
        exists = frappe.db.exists('DocType', dt)
        print(f"{dt} exists: {exists}")
        if exists:
            # Try to get a doc
            try:
                doc = frappe.get_doc('DocType', dt)
                print(f"  Module: {doc.module}")
                print(f"  App: {doc.app}")
            except Exception as e:
                print(f"  Error getting doc: {e}")
    
    # Check all doctypes
    all_doctypes = frappe.get_all('DocType', fields=['name', 'module', 'app'])
    print(f"\nTotal doctypes: {len(all_doctypes)}")
    
    # Group by app
    apps = {}
    for dt in all_doctypes:
        app = dt.app or 'No App'
        if app not in apps:
            apps[app] = []
        apps[app].append(dt.name)
    
    for app, dts in apps.items():
        print(f"\n{app}: {len(dts)} doctypes")
        if app == 'mkaguzi':
            for dt in sorted(dts)[:10]:  # Show first 10
                print(f"  {dt}")
            if len(dts) > 10:
                print(f"  ... and {len(dts) - 10} more")