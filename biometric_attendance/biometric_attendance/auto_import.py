import frappe
import datetime
from frappe.utils import cint,  get_time, split_emails

def get_time_difference_in_minutes(timeA, timeB):
	dateTimeA = datetime.datetime.combine(datetime.date.today(), timeA)
	dateTimeB = datetime.datetime.combine(datetime.date.today(), timeB)
	return (dateTimeA-dateTimeB).total_seconds() / 60

@frappe.whitelist()
def auto_import():
	now_time = datetime.datetime.now().time()
	today_date = datetime.date.today()
	machines = frappe.get_all("Biometric Machine")

	for m_name in machines:
		m = frappe.get_doc("Biometric Machine", m_name)
		minute_diff = get_time_difference_in_minutes(get_time(now_time), get_time(m.import_at))
		if cint(m.enabled) and m.last_import_on != today_date \
			and abs(minute_diff) <=10:
			do_auto_import(m)

def do_auto_import(machine):
	from utils import import_attendance, clear_machine_attendance
	try:
		import_attendance(machine.name)
		if cint(machine.clear_after_import):
			clear_machine_attendance(machine.name)
		machine.last_import_on = datetime.date.today()
		machine.save()
		send_email(success=True, machine=machine)
	except Exception as e:
		send_email(success=False, machine=machine, error_status=e)

def send_email(success, machine, error_status=None):
	if not cint(machine.send_notification):
		return

	if success:
		subject = "Attendance Import Successful - {0}".format(machine.name)
		message ="""<h3>Attendance Imported Successfully</h3><p>Hi there, this is just to inform you
		that your attendance have been successfully imported.</p>"""
	else:
		subject = "[Warning] Attendance Import Failed - {0}".format(machine.name)
		message ="""<h3>Attendance Import has Failed</h3><p>Oops, your automated attendance Import has Failed</p>
		<p>Error message: <br>
		<pre><code>%s</code></pre>
		</p>
		<p>Please contact your system manager for more information.</p>
		""" % (error_status)

	recipients = split_emails(machine.notification_mail_address)
	frappe.sendmail(recipients=recipients, subject=subject, message=message)
