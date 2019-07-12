// Copyright (c) 2019, Akshay Mehta and contributors
// For license information, please see license.txt

frappe.ui.form.on("Enrolled Users", "user", function(frm, dt, dn) {
	var grid_row = cur_frm.open_grid_row();
	var user = null;
	var current_doc = null;

	if (!grid_row) {
		current_doc = frappe.get_doc(dt, dn);
		user = current_doc.user;
	} else {
		user = grid_row.grid_form.fields_dict.user.get_value();
	}

	if(user) {
		frappe.db.get_value("Biometric Users", user, "user_name", function(r) {
					if (grid_row) {
						grid_row.grid_form.fields_dict.user_name.set_value(r.user_name);
					} else {
						current_doc.user_name = r.user_name;
					}
					cur_frm.refresh_field('users');
		});
	}
});

frappe.ui.form.on("Biometric Machine", "refresh", function(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button("Import Attendance", function() {
				frappe.call({
					method: "biometric_attendance.biometric_attendance.utils.import_attendance",
					args: { "machine_name": frm.doc.name },
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint("Success");
						}
					}
				});
			});
			frm.add_custom_button("Sync Users", function() {
				frappe.call({
					method: "biometric_attendance.biometric_attendance.utils.sync_users",
					args: { "machine_name": frm.doc.name },
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint("Success");
						}
					}
				});
			});
		}
});

frappe.ui.form.on("Biometric Machine", "onload", function (frm) {
	frappe.realtime.on("import_biometric_attendance", function(data) {
		if (data.progress) {
			frappe.show_progress("Importing Attendance", data.progress / data.total * 100,
				__("Importing {0} of {1}", [data.progress, data.total]));
		}
		//if (data.progress == data.total) {
		//	window.setTimeout(
		//}
	});
});