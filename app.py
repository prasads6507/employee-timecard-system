
# # from flask import Flask, render_template, request, redirect, url_for, session, send_file
# # from flask_bcrypt import Bcrypt
# # from flask_sqlalchemy import SQLAlchemy
# # from datetime import datetime
# # import csv, io, os
# # from fpdf import FPDF
# # from datetime import datetime, time, timedelta

# # # Overtime thresholds (edit if your policy is different)
# # DAILY_OT_THRESHOLD_MIN = 8 * 60      # 8 hours/day
# # WEEKLY_OT_THRESHOLD_MIN = 40 * 60    # 40 hours/week


# # app = Flask(__name__)
# # app.secret_key = 'your_secret_key_here'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecard.db'
# # db = SQLAlchemy(app)
# # bcrypt = Bcrypt(app)

# # class User(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     username = db.Column(db.String(100), unique=True, nullable=False)
# #     password = db.Column(db.String(200), nullable=False)
# #     role = db.Column(db.String(20), nullable=False)

# # class TimeLog(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
# #     clock_in = db.Column(db.DateTime)
# #     clock_out = db.Column(db.DateTime)

# # def clamp(dt, start, end):
# #     """Clamp datetime dt into [start, end]."""
# #     if dt < start: return start
# #     if dt > end: return end
# #     return dt

# # def minutes_in_range(log, start, end):
# #     """
# #     Count minutes of a TimeLog within [start, end].
# #     Handles still-clocked-in shifts and clamps to range.
# #     """
# #     if not log.clock_in:
# #         return 0
# #     s = clamp(log.clock_in, start, end)
# #     e = clamp(log.clock_out or datetime.now(), start, end)
# #     if e <= s:
# #         return 0
# #     return int((e - s).total_seconds() // 60)

# # def day_bounds(dt_date):
# #     """Return start/end datetimes (00:00..23:59:59.999) for a given date."""
# #     start = datetime.combine(dt_date, time.min)
# #     end   = datetime.combine(dt_date, time.max)
# #     return start, end

# # def this_week_bounds():
# #     """
# #     Week = Mon..Sun.
# #     Returns (week_start, week_end) for the current week.
# #     """
# #     today = datetime.today().date()
# #     week_start_date = today - timedelta(days=today.weekday())  # Monday
# #     week_end_date   = week_start_date + timedelta(days=6)      # Sunday
# #     return day_bounds(week_start_date)[0], day_bounds(week_end_date)[1]

# # def totals_for_user_today_and_week(user_id):
# #     """Return (today_minutes, today_ot, week_minutes, week_ot, clocked_in_now)."""
# #     # Today bounds
# #     today = datetime.today().date()
# #     today_start, today_end = day_bounds(today)

# #     # Week bounds
# #     week_start, week_end = this_week_bounds()

# #     # Fetch logs overlapping this week (fewer DB reads than separate queries)
# #     logs = TimeLog.query.filter(
# #         TimeLog.user_id == user_id,
# #         TimeLog.clock_in >= week_start  # reasonable assumption for this app
# #     ).all()

# #     # Compute totals
# #     today_minutes = sum(minutes_in_range(log, today_start, today_end) for log in logs)
# #     week_minutes  = sum(minutes_in_range(log, week_start,  week_end)  for log in logs)
# #     clocked_in_now = any(log.clock_out is None for log in logs)

# #     today_ot = max(0, today_minutes - DAILY_OT_THRESHOLD_MIN)
# #     week_ot  = max(0, week_minutes  - WEEKLY_OT_THRESHOLD_MIN)

# #     return today_minutes, today_ot, week_minutes, week_ot, clocked_in_now


# # @app.route('/')
# # def index():
# #     return render_template('login.html')

# # @app.route('/login', methods=['POST'])
# # def login():
# #     username = request.form['username']
# #     password = request.form['password']
# #     print("Submitted:", username, password)

# #     user = User.query.filter_by(username=username).first()
# #     if user:
# #         print("Found user:", user.username, user.password)
# #     else:
# #         print("User not found")

# #     if user and user.password == password:
# #         session['user_id'] = user.id
# #         session['role'] = user.role
# #         return redirect(url_for('dashboard'))

# #     print("Login failed")
# #     return 'Invalid credentials'


# # @app.route('/logout')
# # def logout():
# #     session.clear()
# #     return redirect(url_for('index'))

# # # @app.route('/dashboard')
# # # def dashboard():
# # #     if 'user_id' not in session:
# # #         return redirect(url_for('index'))
# # #     if session.get('role') == 'admin':
# # #         logs = TimeLog.query.all()
# # #     else:
# # #         logs = TimeLog.query.filter_by(user_id=session['user_id']).all()
# # #     return render_template('dashboard.html', logs=logs, role=session.get('role'))

# # # @app.route('/dashboard')
# # # def dashboard():
# # #     if 'user_id' not in session:
# # #         return redirect(url_for('index'))

# # #     user = User.query.get(session['user_id'])
# # #     logs = TimeLog.query.all() if user.role == 'admin' else TimeLog.query.filter_by(user_id=user.id).all()

# # #     summary = {}
# # #     today = datetime.now().date()
# # #     if user.role == 'admin':
# # #         users = User.query.all()
# # #         for u in users:
# # #             entries = TimeLog.query.filter(TimeLog.user_id == u.id, TimeLog.clock_in >= datetime.combine(today, datetime.min.time())).all()
# # #             total_minutes = sum(
# # #                 ((entry.clock_out or datetime.now()) - entry.clock_in).seconds // 60 for entry in entries
# # #             )
# # #             clocked_in = any(entry.clock_out is None for entry in entries)
# # #             summary[u.username] = {
# # #                 'clocked_in': clocked_in,
# # #                 'total_minutes': total_minutes
# # #             }

# # #     return render_template('dashboard.html', logs=logs, role=user.role, summary=summary if user.role == 'admin' else None, user=user)

# # # @app.route('/dashboard')
# # # def dashboard():
# # #     if 'user_id' not in session:
# # #         return redirect(url_for('index'))

# # #     user = User.query.get(session['user_id'])
# # #     logs = TimeLog.query.all() if user.role == 'admin' else TimeLog.query.filter_by(user_id=user.id).all()

# # #     summary = {}
# # #     today = datetime.now().date()

# # #     if user.role == 'admin':
# # #         users = User.query.all()
# # #         for u in users:
# # #             entries = TimeLog.query.filter(
# # #                 TimeLog.user_id == u.id,
# # #                 db.func.date(TimeLog.clock_in) == today
# # #             ).all()

# # #             total_minutes = sum(
# # #                 int(((entry.clock_out or datetime.now()) - entry.clock_in).total_seconds() // 60)
# # #                 for entry in entries
# # #             )

# # #             clocked_in = any(entry.clock_out is None for entry in entries)

# # #             summary[u.username] = {
# # #                 'clocked_in': clocked_in,
# # #                 'total_minutes': total_minutes
# # #             }

# # #     return render_template('dashboard.html',
# # #                            logs=logs,
# # #                            role=user.role,
# # #                            summary=summary if user.role == 'admin' else None,
# # #                            user=user)

# # from datetime import datetime, time

# # # @app.route('/dashboard')
# # # def dashboard():
# # #     if 'user_id' not in session:
# # #         return redirect(url_for('index'))

# # #     user = User.query.get(session['user_id'])
# # #     logs = TimeLog.query.all() if user.role == 'admin' else TimeLog.query.filter_by(user_id=user.id).all()

# # #     summary = {}
# # #     if user.role == 'admin':
# # #         today_start = datetime.combine(datetime.today().date(), time.min)
# # #         today_end = datetime.combine(datetime.today().date(), time.max)

# # #         users = User.query.all()
# # #         for u in users:
# # #             entries = TimeLog.query.filter(
# # #                 TimeLog.user_id == u.id,
# # #                 TimeLog.clock_in >= today_start,
# # #                 TimeLog.clock_in <= today_end
# # #             ).all()

# # #             total_minutes = 0
# # #             for entry in entries:
# # #                 if entry.clock_in:
# # #                     clock_out_time = entry.clock_out if entry.clock_out else datetime.now()
# # #                     total_minutes += int((clock_out_time - entry.clock_in).total_seconds() // 60)

# # #             clocked_in = any(entry.clock_out is None for entry in entries)

# # #             summary[u.username] = {
# # #                 'clocked_in': clocked_in,
# # #                 'total_minutes': total_minutes
# # #             }

# # #     return render_template('dashboard.html',
# # #                            logs=logs,
# # #                            role=user.role,
# # #                            summary=summary if user.role == 'admin' else None,
# # #                            user=user)

# # @app.route('/dashboard')
# # def dashboard():
# #     if 'user_id' not in session:
# #         return redirect(url_for('index'))

# #     user = User.query.get(session['user_id'])

# #     # Logs to show in the table (unchanged behavior)
# #     logs = TimeLog.query.all() if user.role == 'admin' else TimeLog.query.filter_by(user_id=user.id).all()

# #     # Build summaries
# #     summary = None
# #     my_today = my_today_ot = my_week = my_week_ot = 0
# #     my_clocked_in = False

# #     # Employee's own summary (shown to everyone)
# #     my_today, my_today_ot, my_week, my_week_ot, my_clocked_in = totals_for_user_today_and_week(user.id)

# #     # Admin: table with everyone’s daily/weekly & overtime
# #     if user.role == 'admin':
# #         summary = {}
# #         for u in User.query.all():
# #             tmin, tot, wmin, wot, cnow = totals_for_user_today_and_week(u.id)
# #             summary[u.username] = {
# #                 'clocked_in': cnow,
# #                 'today_minutes': tmin,
# #                 'today_ot': tot,
# #                 'week_minutes': wmin,
# #                 'week_ot': wot,
# #             }

# #     return render_template(
# #         'dashboard.html',
# #         user=user,
# #         role=user.role,
# #         logs=logs,
# #         summary=summary,  # dict for admin, None otherwise
# #         my_today=my_today,
# #         my_today_ot=my_today_ot,
# #         my_week=my_week,
# #         my_week_ot=my_week_ot,
# #         my_clocked_in=my_clocked_in
# #     )



# # @app.route('/clock_in')
# # def clock_in():
# #     if 'user_id' in session:
# #         log = TimeLog(user_id=session['user_id'], clock_in=datetime.now())
# #         db.session.add(log)
# #         db.session.commit()
# #     return redirect(url_for('dashboard'))

# # @app.route('/clock_out')
# # def clock_out():
# #     if 'user_id' in session:
# #         log = TimeLog.query.filter_by(user_id=session['user_id'], clock_out=None).order_by(TimeLog.clock_in.desc()).first()
# #         if log:
# #             log.clock_out = datetime.now()
# #             db.session.commit()
# #     return redirect(url_for('dashboard'))

# # # @app.route('/export_csv')
# # # def export_csv():
# # #     output = io.StringIO()
# # #     writer = csv.writer(output)
# # #     writer.writerow(['Username', 'Clock In', 'Clock Out'])
# # #     logs = TimeLog.query.all()
# # #     for log in logs:
# # #         user = User.query.get(log.user_id)
# # #         writer.writerow([user.username, log.clock_in, log.clock_out])
# # #     output.seek(0)
# # #     return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='timelogs.csv')

# # # @app.route('/export_csv')
# # # def export_csv():
# # #     output = io.StringIO()
# # #     writer = csv.writer(output)
# # #     writer.writerow(['Username', 'Clock In', 'Clock Out', 'Total Minutes Today', 'Clocked In'])

# # #     today_start = datetime.combine(datetime.today().date(), time.min)
# # #     today_end = datetime.combine(datetime.today().date(), time.max)

# # #     users = User.query.all()
# # #     for user in users:
# # #         logs = TimeLog.query.filter_by(user_id=user.id).all()
# # #         entries_today = [log for log in logs if today_start <= log.clock_in <= today_end]

# # #         total_minutes = sum(
# # #             int(((log.clock_out or datetime.now()) - log.clock_in).total_seconds() // 60)
# # #             for log in entries_today
# # #         )
# # #         clocked_in = any(log.clock_out is None for log in entries_today)

# # #         for log in logs:
# # #             writer.writerow([
# # #                 user.username,
# # #                 log.clock_in,
# # #                 log.clock_out,
# # #                 total_minutes,
# # #                 'Yes' if clocked_in else 'No'
# # #             ])

# # #     output.seek(0)
# # #     return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='timelogs_summary.csv')

# # # @app.route('/export_csv')
# # # def export_csv():
# # #     output = io.StringIO()
# # #     writer = csv.writer(output)
# # #     writer.writerow(['Username', 'Clock In', 'Clock Out', 'Total Minutes Today', 'Clocked In'])

# # #     today_start = datetime.combine(datetime.today().date(), time.min)
# # #     today_end = datetime.combine(datetime.today().date(), time.max)

# # #     users = User.query.all()
# # #     for user in users:
# # #         logs = TimeLog.query.filter_by(user_id=user.id).all()
# # #         entries_today = [log for log in logs if today_start <= log.clock_in <= today_end]

# # #         total_minutes = sum(
# # #             int(((log.clock_out or datetime.now()) - log.clock_in).total_seconds() // 60)
# # #             for log in entries_today
# # #         )
# # #         clocked_in = any(log.clock_out is None for log in entries_today)

# # #         for log in logs:
# # #             clock_in_str = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
# # #             clock_out_str = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
# # #             writer.writerow([
# # #                 user.username,
# # #                 clock_in_str,
# # #                 clock_out_str,
# # #                 total_minutes,
# # #                 'Yes' if clocked_in else 'No'
# # #             ])

# # #     output.seek(0)
# # #     return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='timelogs_summary.csv')

# # @app.route('/export_csv')
# # def export_csv():
# #     if 'user_id' not in session:
# #         return redirect(url_for('index'))

# #     from sqlalchemy import and_

# #     current_user = User.query.get(session['user_id'])
# #     is_admin = (current_user.role == 'admin')

# #     # CSV buffer
# #     output = io.StringIO()
# #     writer = csv.writer(output)

# #     if not is_admin:
# #         # EMPLOYEE: only their own logs
# #         logs = (TimeLog.query
# #                 .filter_by(user_id=current_user.id)
# #                 .order_by(TimeLog.clock_in.desc())
# #                 .all())

# #         writer.writerow(['Username', 'Clock In', 'Clock Out'])
# #         for log in logs:
# #             ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
# #             co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
# #             writer.writerow([current_user.username, ci, co])

# #         output.seek(0)
# #         return send_file(
# #             io.BytesIO(output.getvalue().encode()),
# #             mimetype='text/csv',
# #             as_attachment=True,
# #             download_name=f'timelogs_{current_user.username}.csv'
# #         )

# #     # ADMIN: with optional filters (date range + employee)
# #     start_date_str = request.args.get('start_date', '').strip()
# #     end_date_str   = request.args.get('end_date', '').strip()
# #     employee_q     = request.args.get('employee', '').strip()

# #     def parse_date(d):
# #         try:
# #             return datetime.strptime(d, "%Y-%m-%d").date()
# #         except:
# #             return None

# #     start_dt = end_dt = None
# #     if start_date_str:
# #         sd = parse_date(start_date_str)
# #         if sd: start_dt = datetime.combine(sd, time.min)
# #     if end_date_str:
# #         ed = parse_date(end_date_str)
# #         if ed: end_dt = datetime.combine(ed, time.max)

# #     logs_query = TimeLog.query.join(User, TimeLog.user_id == User.id)
# #     if employee_q:
# #         logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
# #     if start_dt and end_dt:
# #         logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
# #     elif start_dt:
# #         logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
# #     elif end_dt:
# #         logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)

# #     logs = logs_query.order_by(TimeLog.clock_in.desc()).all()

# #     writer.writerow(['Username', 'Clock In', 'Clock Out'])
# #     for log in logs:
# #         ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
# #         co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
# #         writer.writerow([log.user.username, ci, co])

# #     output.seek(0)
# #     return send_file(
# #         io.BytesIO(output.getvalue().encode()),
# #         mimetype='text/csv',
# #         as_attachment=True,
# #         download_name='timelogs_admin.csv'
# #     )


# # # @app.route('/export_pdf')
# # # def export_pdf():
# # #     pdf = FPDF()
# # #     pdf.add_page()
# # #     pdf.set_font('Arial', size=12)
# # #     pdf.cell(200, 10, txt='Employee Time Logs', ln=True, align='C')
# # #     logs = TimeLog.query.all()
# # #     for log in logs:
# # #         user = User.query.get(log.user_id)
# # #         line = f"{user.username} | {log.clock_in} | {log.clock_out}"
# # #         pdf.cell(200, 10, txt=line, ln=True)
# # #     pdf.output('timelogs.pdf')
# # #     return send_file('timelogs.pdf', as_attachment=True)

# # # @app.route('/export_pdf')
# # # def export_pdf():
# # #     pdf = FPDF()
# # #     pdf.add_page()
# # #     pdf.set_font('Arial', 'B', 12)
# # #     pdf.cell(200, 10, txt='Employee Time Logs with Summary', ln=True, align='C')

# # #     today_start = datetime.combine(datetime.today().date(), time.min)
# # #     today_end = datetime.combine(datetime.today().date(), time.max)

# # #     users = User.query.all()
# # #     for user in users:
# # #         logs = TimeLog.query.filter_by(user_id=user.id).all()
# # #         entries_today = [log for log in logs if today_start <= log.clock_in <= today_end]

# # #         total_minutes = sum(
# # #             int(((log.clock_out or datetime.now()) - log.clock_in).total_seconds() // 60)
# # #             for log in entries_today
# # #         )
# # #         clocked_in = any(log.clock_out is None for log in entries_today)

# # #         pdf.set_font('Arial', 'B', 10)
# # #         pdf.cell(200, 10, txt=f"{user.username} - Total Minutes Today: {total_minutes} - Clocked In: {'Yes' if clocked_in else 'No'}", ln=True)

# # #         pdf.set_font('Arial', '', 10)
# # #         for log in logs:
# # #             line = f"   {log.clock_in} | {log.clock_out or '---'}"
# # #             pdf.cell(200, 8, txt=line, ln=True)

# # #     pdf_path = 'timelogs_summary.pdf'
# # #     pdf.output(pdf_path)
# # #     return send_file(pdf_path, as_attachment=True)

# # @app.route('/export_pdf')
# # def export_pdf():
# #     if 'user_id' not in session:
# #         return redirect(url_for('index'))

# #     from sqlalchemy import and_

# #     current_user = User.query.get(session['user_id'])
# #     is_admin = (current_user.role == 'admin')

# #     pdf = FPDF()
# #     pdf.add_page()
# #     pdf.set_font('Arial', 'B', 13)

# #     if not is_admin:
# #         # EMPLOYEE: only their own logs
# #         pdf.cell(0, 10, f"Time Logs — {current_user.username}", ln=True, align='C')
# #         logs = (TimeLog.query
# #                 .filter_by(user_id=current_user.id)
# #                 .order_by(TimeLog.clock_in.desc())
# #                 .all())

# #         pdf.set_font('Arial', '', 10)
# #         for log in logs:
# #             ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
# #             co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else '—'
# #             pdf.cell(0, 8, f"{ci}  |  {co}", ln=True)

# #         path = f"timelogs_{current_user.username}.pdf"
# #         pdf.output(path)
# #         return send_file(path, as_attachment=True)

# #     # ADMIN: with optional filters (date range + employee)
# #     start_date_str = request.args.get('start_date', '').strip()
# #     end_date_str   = request.args.get('end_date', '').strip()
# #     employee_q     = request.args.get('employee', '').strip()

# #     def parse_date(d):
# #         try:
# #             return datetime.strptime(d, "%Y-%m-%d").date()
# #         except:
# #             return None

# #     start_dt = end_dt = None
# #     if start_date_str:
# #         sd = parse_date(start_date_str)
# #         if sd: start_dt = datetime.combine(sd, time.min)
# #     if end_date_str:
# #         ed = parse_date(end_date_str)
# #         if ed: end_dt = datetime.combine(ed, time.max)

# #     logs_query = TimeLog.query.join(User, TimeLog.user_id == User.id)
# #     if employee_q:
# #         logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
# #     if start_dt and end_dt:
# #         logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
# #     elif start_dt:
# #         logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
# #     elif end_dt:
# #         logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)

# #     logs = logs_query.order_by(TimeLog.clock_in.desc()).all()

# #     pdf.cell(0, 10, "Employee Time Logs", ln=True, align='C')
# #     pdf.set_font('Arial', '', 10)

# #     for log in logs:
# #         uname = log.user.username
# #         ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
# #         co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else '—'
# #         pdf.cell(0, 8, f"{uname}: {ci}  |  {co}", ln=True)

# #     path = 'timelogs_admin.pdf'
# #     pdf.output(path)
# #     return send_file(path, as_attachment=True)


# # @app.route('/add_user', methods=['GET', 'POST'])
# # def add_user_web():
# #     if 'user_id' not in session or session.get('role') != 'admin':
# #         return redirect(url_for('index'))

# #     if request.method == 'POST':
# #         username = request.form['username']
# #         password = request.form['password']
# #         role = request.form['role']

# #         existing = User.query.filter_by(username=username).first()
# #         if existing:
# #             return '❌ User already exists.'
# #         new_user = User(username=username, password=password, role=role)
# #         db.session.add(new_user)
# #         db.session.commit()
# #         return '✅ User added successfully.'

# #     return render_template('add_user.html')

# # @app.route('/delete_user/<username>', methods=['POST'])
# # def delete_user(username):
# #     if 'user_id' not in session or session.get('role') != 'admin':
# #         return redirect(url_for('index'))

# #     user_to_delete = User.query.filter_by(username=username).first()
# #     if user_to_delete:
# #         if user_to_delete.id == session['user_id']:
# #             return "❌ You can't delete yourself."

# #         # Delete their time logs first
# #         TimeLog.query.filter_by(user_id=user_to_delete.id).delete()
# #         db.session.delete(user_to_delete)
# #         db.session.commit()
# #         return redirect(url_for('dashboard'))

# #     return "❌ User not found"



# # if __name__ == '__main__':
# #     with app.app_context():
# #         db.create_all()
# #     app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, session, send_file
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import and_
# from sqlalchemy.orm import joinedload
# from datetime import datetime, time, timedelta
# import csv, io, os
# from fpdf import FPDF

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'

# # SQLite file in project folder
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecard.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # ----------------------
# # Models
# # ----------------------
# class User(db.Model):
#     id       = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)  # plaintext for demo
#     role     = db.Column(db.String(20), nullable=False)   # 'admin' | 'employee'

# class TimeLog(db.Model):
#     id        = db.Column(db.Integer, primary_key=True)
#     user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     clock_in  = db.Column(db.DateTime)
#     clock_out = db.Column(db.DateTime)
#     # Relationship so templates & exports can use log.user.username
#     user      = db.relationship('User', backref='time_logs')

# # ----------------------
# # Auth
# # ----------------------
# @app.route('/')
# def index():
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username'].strip()
#     password = request.form['password'].strip()

#     user = User.query.filter_by(username=username).first()
#     if user and user.password == password:  # plaintext check (demo simplicity)
#         session['user_id'] = user.id
#         session['role']    = user.role
#         return redirect(url_for('dashboard'))
#     return 'Invalid credentials'

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# # ----------------------
# # Helper functions (time math)
# # ----------------------
# DAILY_OT_THRESHOLD_MIN  = 8 * 60    # 8h/day
# WEEKLY_OT_THRESHOLD_MIN = 40 * 60   # 40h/week

# def clamp(dt, start, end):
#     """Clamp datetime dt into [start, end]."""
#     if dt < start: return start
#     if dt > end:   return end
#     return dt

# def minutes_in_range(log, start, end):
#     """
#     Count minutes of a TimeLog within [start, end].
#     Handles still-clocked-in shifts and clamps to range.
#     """
#     if not log.clock_in:
#         return 0
#     s = clamp(log.clock_in, start, end)
#     e = clamp(log.clock_out or datetime.now(), start, end)
#     if e <= s:
#         return 0
#     return int((e - s).total_seconds() // 60)

# def day_bounds(dt_date):
#     """Return start/end datetimes (00:00..23:59:59.999) for a given date."""
#     start = datetime.combine(dt_date, time.min)
#     end   = datetime.combine(dt_date, time.max)
#     return start, end

# def this_week_bounds():
#     """Week = Mon..Sun. Return (start, end) datetimes."""
#     today = datetime.today().date()
#     week_start_date = today - timedelta(days=today.weekday())  # Monday
#     week_end_date   = week_start_date + timedelta(days=6)      # Sunday
#     return day_bounds(week_start_date)[0], day_bounds(week_end_date)[1]

# def totals_for_user_today_and_week(user_id):
#     """Return (today_minutes, today_ot, week_minutes, week_ot, clocked_in_now)."""
#     today = datetime.today().date()
#     today_start, today_end = day_bounds(today)
#     week_start, week_end   = this_week_bounds()

#     logs = (TimeLog.query
#             .filter(TimeLog.user_id == user_id, TimeLog.clock_in >= week_start)
#             .order_by(TimeLog.clock_in.asc())
#             .all())

#     today_minutes  = sum(minutes_in_range(l, today_start, today_end) for l in logs)
#     week_minutes   = sum(minutes_in_range(l, week_start,  week_end)  for l in logs)
#     clocked_in_now = any(l.clock_out is None for l in logs)

#     today_ot = max(0, today_minutes - DAILY_OT_THRESHOLD_MIN)
#     week_ot  = max(0, week_minutes  - WEEKLY_OT_THRESHOLD_MIN)
#     return today_minutes, today_ot, week_minutes, week_ot, clocked_in_now

# # ----------------------
# # Dashboard (with filters for admin)
# # ----------------------
# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('index'))

#     user = User.query.get(session['user_id'])

#     # Read filters (admin only)
#     start_date_str = request.args.get('start_date', '').strip()
#     end_date_str   = request.args.get('end_date', '').strip()
#     employee_q     = request.args.get('employee', '').strip()  # username partial

#     def parse_date(d):
#         try:    return datetime.strptime(d, "%Y-%m-%d").date()
#         except: return None

#     start_dt = end_dt = None
#     if user.role == 'admin':
#         if start_date_str:
#             sd = parse_date(start_date_str)
#             if sd: start_dt = datetime.combine(sd, time.min)
#         if end_date_str:
#             ed = parse_date(end_date_str)
#             if ed: end_dt = datetime.combine(ed, time.max)

#         logs_query = (TimeLog.query
#                       .join(User, TimeLog.user_id == User.id)
#                       .options(joinedload(TimeLog.user)))
#         if employee_q:
#             logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
#         if start_dt and end_dt:
#             logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
#         elif start_dt:
#             logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
#         elif end_dt:
#             logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)
#         logs = logs_query.order_by(TimeLog.clock_in.desc()).all()
#     else:
#         logs = (TimeLog.query
#                 .filter_by(user_id=user.id)
#                 .options(joinedload(TimeLog.user))
#                 .order_by(TimeLog.clock_in.desc())
#                 .all())

#     # Personal daily/weekly summary for header cards
#     my_today, my_today_ot, my_week, my_week_ot, my_clocked_in = totals_for_user_today_and_week(user.id)

#     # Admin team summary (always for "today" & "this week")
#     summary = None
#     if user.role == 'admin':
#         summary = {}
#         for u in User.query.order_by(User.username.asc()).all():
#             tmin, tot, wmin, wot, cnow = totals_for_user_today_and_week(u.id)
#             summary[u.username] = {
#                 'clocked_in'   : cnow,
#                 'today_minutes': tmin,
#                 'today_ot'     : tot,
#                 'week_minutes' : wmin,
#                 'week_ot'      : wot,
#             }

#     # For employee dropdown in the filter form
#     employees = User.query.order_by(User.username.asc()).all() if user.role == 'admin' else []

#     return render_template(
#         'dashboard.html',
#         user=user,
#         role=user.role,
#         logs=logs,
#         summary=summary,
#         # personal
#         my_today=my_today,
#         my_today_ot=my_today_ot,
#         my_week=my_week,
#         my_week_ot=my_week_ot,
#         my_clocked_in=my_clocked_in,
#         # filters
#         employees=employees,
#         start_date_val=start_date_str,
#         end_date_val=end_date_str,
#         employee_val=employee_q
#     )

# # ----------------------
# # Clock in/out
# # ----------------------
# @app.route('/clock_in')
# def clock_in():
#     if 'user_id' in session:
#         db.session.add(TimeLog(user_id=session['user_id'], clock_in=datetime.now()))
#         db.session.commit()
#     return redirect(url_for('dashboard'))

# @app.route('/clock_out')
# def clock_out():
#     if 'user_id' in session:
#         log = (TimeLog.query
#                .filter_by(user_id=session['user_id'], clock_out=None)
#                .order_by(TimeLog.clock_in.desc())
#                .first())
#         if log:
#             log.clock_out = datetime.now()
#             db.session.commit()
#     return redirect(url_for('dashboard'))

# # ----------------------
# # Exports (CSV / PDF)
# # Employees: only own logs
# # Admins: all logs (with optional filters)
# # ----------------------
# @app.route('/export_csv')
# def export_csv():
#     if 'user_id' not in session:
#         return redirect(url_for('index'))

#     current_user = User.query.get(session['user_id'])
#     is_admin = (current_user.role == 'admin')

#     output = io.StringIO()
#     writer = csv.writer(output)

#     if not is_admin:
#         # EMPLOYEE: only their own logs
#         logs = (TimeLog.query
#                 .filter_by(user_id=current_user.id)
#                 .options(joinedload(TimeLog.user))
#                 .order_by(TimeLog.clock_in.desc())
#                 .all())

#         writer.writerow(['Username', 'Clock In', 'Clock Out'])
#         for log in logs:
#             ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
#             co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
#             writer.writerow([current_user.username, ci, co])

#         output.seek(0)
#         return send_file(
#             io.BytesIO(output.getvalue().encode()),
#             mimetype='text/csv',
#             as_attachment=True,
#             download_name=f'timelogs_{current_user.username}.csv'
#         )

#     # ADMIN: with optional filters (date range + employee)
#     start_date_str = request.args.get('start_date', '').strip()
#     end_date_str   = request.args.get('end_date', '').strip()
#     employee_q     = request.args.get('employee', '').strip()

#     def parse_date(d):
#         try:
#             return datetime.strptime(d, "%Y-%m-%d").date()
#         except:
#             return None

#     start_dt = end_dt = None
#     if start_date_str:
#         sd = parse_date(start_date_str)
#         if sd: start_dt = datetime.combine(sd, time.min)
#     if end_date_str:
#         ed = parse_date(end_date_str)
#         if ed: end_dt = datetime.combine(ed, time.max)

#     logs_query = (TimeLog.query
#                   .join(User, TimeLog.user_id == User.id)
#                   .options(joinedload(TimeLog.user)))
#     if employee_q:
#         logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
#     if start_dt and end_dt:
#         logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
#     elif start_dt:
#         logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
#     elif end_dt:
#         logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)

#     logs = logs_query.order_by(TimeLog.clock_in.desc()).all()

#     writer.writerow(['Username', 'Clock In', 'Clock Out'])
#     for log in logs:
#         ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
#         co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
#         writer.writerow([log.user.username, ci, co])

#     output.seek(0)
#     return send_file(
#         io.BytesIO(output.getvalue().encode()),
#         mimetype='text/csv',
#         as_attachment=True,
#         download_name='timelogs_admin.csv'
#     )

# @app.route('/export_pdf')
# def export_pdf():
#     if 'user_id' not in session:
#         return redirect(url_for('index'))

#     current_user = User.query.get(session['user_id'])
#     is_admin = (current_user.role == 'admin')

#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font('Arial', 'B', 13)

#     if not is_admin:
#         # EMPLOYEE: only their own logs
#         pdf.cell(0, 10, f"Time Logs — {current_user.username}", ln=True, align='C')
#         logs = (TimeLog.query
#                 .filter_by(user_id=current_user.id)
#                 .options(joinedload(TimeLog.user))
#                 .order_by(TimeLog.clock_in.desc())
#                 .all())

#         pdf.set_font('Arial', '', 10)
#         for log in logs:
#             ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
#             co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else '—'
#             pdf.cell(0, 8, f"{ci}  |  {co}", ln=True)

#         path = f"timelogs_{current_user.username}.pdf"
#         pdf.output(path)
#         return send_file(path, as_attachment=True)

#     # ADMIN: with optional filters (date range + employee)
#     start_date_str = request.args.get('start_date', '').strip()
#     end_date_str   = request.args.get('end_date', '').strip()
#     employee_q     = request.args.get('employee', '').strip()

#     def parse_date(d):
#         try:
#             return datetime.strptime(d, "%Y-%m-%d").date()
#         except:
#             return None

#     start_dt = end_dt = None
#     if start_date_str:
#         sd = parse_date(start_date_str)
#         if sd: start_dt = datetime.combine(sd, time.min)
#     if end_date_str:
#         ed = parse_date(end_date_str)
#         if ed: end_dt = datetime.combine(ed, time.max)

#     logs_query = (TimeLog.query
#                   .join(User, TimeLog.user_id == User.id)
#                   .options(joinedload(TimeLog.user)))
#     if employee_q:
#         logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
#     if start_dt and end_dt:
#         logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
#     elif start_dt:
#         logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
#     elif end_dt:
#         logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)

#     logs = logs_query.order_by(TimeLog.clock_in.desc()).all()

#     pdf.cell(0, 10, "Employee Time Logs", ln=True, align='C')
#     pdf.set_font('Arial', '', 10)
#     for log in logs:
#         uname = log.user.username
#         ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
#         co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else '—'
#         pdf.cell(0, 8, f"{uname}: {ci}  |  {co}", ln=True)

#     path = 'timelogs_admin.pdf'
#     pdf.output(path)
#     return send_file(path, as_attachment=True)

# # ----------------------
# # Admin: add/delete user
# # ----------------------
# @app.route('/add_user', methods=['GET', 'POST'])
# def add_user_web():
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('index'))

#     if request.method == 'POST':
#         username = request.form['username'].strip()
#         password = request.form['password'].strip()
#         role     = request.form['role'].strip()

#         if not username or not password or role not in ('admin', 'employee'):
#             return '❌ Invalid input.'
#         existing = User.query.filter_by(username=username).first()
#         if existing:
#             return '❌ User already exists.'

#         db.session.add(User(username=username, password=password, role=role))
#         db.session.commit()
#         return redirect(url_for('dashboard'))

#     return render_template('add_user.html')

# @app.route('/delete_user/<username>', methods=['POST'])
# def delete_user(username):
#     if 'user_id' not in session or session.get('role') != 'admin':
#         return redirect(url_for('index'))

#     user_to_delete = User.query.filter_by(username=username).first()
#     if not user_to_delete:
#         return "❌ User not found"
#     if user_to_delete.id == session['user_id']:
#         return "❌ You can't delete yourself."

#     TimeLog.query.filter_by(user_id=user_to_delete.id).delete()
#     db.session.delete(user_to_delete)
#     db.session.commit()
#     return redirect(url_for('dashboard'))

# # ----------------------
# # Bootstrap DB + run
# # ----------------------
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)




from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from datetime import datetime, time, timedelta
import csv, io, os
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# SQLite file in project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------------
# Models
# ----------------------
class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # plaintext for demo
    role     = db.Column(db.String(20), nullable=False)   # 'admin' | 'employee'

class TimeLog(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clock_in  = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)
    # Relationship so templates & exports can use log.user.username
    user      = db.relationship('User', backref='time_logs')

# ----------------------
# PDF unicode-safe helper
# ----------------------
def pdf_safe(text: str) -> str:
    if text is None:
        return ""
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2019": "'",   # right single quote ’
        "\u2018": "'",   # left single quote ‘
        "\u201c": '"',   # left double quote “
        "\u201d": '"',   # right double quote ”
        "\u2022": "*",   # bullet •
        "\u00a0": " ",   # non-breaking space
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "ignore").decode("latin-1")

# ----------------------
# Auth
# ----------------------
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:  # plaintext check (demo simplicity)
        session['user_id'] = user.id
        session['role']    = user.role
        return redirect(url_for('dashboard'))
    return 'Invalid credentials'

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ----------------------
# Helper functions (time math)
# ----------------------
DAILY_OT_THRESHOLD_MIN  = 8 * 60    # 8h/day
WEEKLY_OT_THRESHOLD_MIN = 40 * 60   # 40h/week

def clamp(dt, start, end):
    if dt < start: return start
    if dt > end:   return end
    return dt

def minutes_in_range(log, start, end):
    if not log.clock_in:
        return 0
    s = clamp(log.clock_in, start, end)
    e = clamp(log.clock_out or datetime.now(), start, end)
    if e <= s:
        return 0
    return int((e - s).total_seconds() // 60)

def day_bounds(dt_date):
    start = datetime.combine(dt_date, time.min)
    end   = datetime.combine(dt_date, time.max)
    return start, end

def this_week_bounds():
    today = datetime.today().date()
    week_start_date = today - timedelta(days=today.weekday())  # Monday
    week_end_date   = week_start_date + timedelta(days=6)      # Sunday
    return day_bounds(week_start_date)[0], day_bounds(week_end_date)[1]

def totals_for_user_today_and_week(user_id):
    today = datetime.today().date()
    today_start, today_end = day_bounds(today)
    week_start, week_end   = this_week_bounds()

    logs = (TimeLog.query
            .filter(TimeLog.user_id == user_id, TimeLog.clock_in >= week_start)
            .order_by(TimeLog.clock_in.asc())
            .all())

    today_minutes  = sum(minutes_in_range(l, today_start, today_end) for l in logs)
    week_minutes   = sum(minutes_in_range(l, week_start,  week_end)  for l in logs)
    clocked_in_now = any(l.clock_out is None for l in logs)

    today_ot = max(0, today_minutes - DAILY_OT_THRESHOLD_MIN)
    week_ot  = max(0, week_minutes  - WEEKLY_OT_THRESHOLD_MIN)
    return today_minutes, today_ot, week_minutes, week_ot, clocked_in_now

# ----------------------
# Dashboard (with filters for admin)
# ----------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user = User.query.get(session['user_id'])

    # Read filters (admin only)
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    employee_q     = request.args.get('employee', '').strip()  # username partial

    def parse_date(d):
        try:    return datetime.strptime(d, "%Y-%m-%d").date()
        except: return None

    start_dt = end_dt = None
    if user.role == 'admin':
        if start_date_str:
            sd = parse_date(start_date_str)
            if sd: start_dt = datetime.combine(sd, time.min)
        if end_date_str:
            ed = parse_date(end_date_str)
            if ed: end_dt = datetime.combine(ed, time.max)

        logs_query = (TimeLog.query
                      .join(User, TimeLog.user_id == User.id)
                      .options(joinedload(TimeLog.user)))
        if employee_q:
            logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
        if start_dt and end_dt:
            logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
        elif start_dt:
            logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
        elif end_dt:
            logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)
        logs = logs_query.order_by(TimeLog.clock_in.desc()).all()
    else:
        logs = (TimeLog.query
                .filter_by(user_id=user.id)
                .options(joinedload(TimeLog.user))
                .order_by(TimeLog.clock_in.desc())
                .all())

    # Personal daily/weekly summary for header cards
    my_today, my_today_ot, my_week, my_week_ot, my_clocked_in = totals_for_user_today_and_week(user.id)

    # Admin team summary (always for "today" & "this week")
    summary = None
    if user.role == 'admin':
        summary = {}
        for u in User.query.order_by(User.username.asc()).all():
            tmin, tot, wmin, wot, cnow = totals_for_user_today_and_week(u.id)
            summary[u.username] = {
                'clocked_in'   : cnow,
                'today_minutes': tmin,
                'today_ot'     : tot,
                'week_minutes' : wmin,
                'week_ot'      : wot,
            }

    # For employee dropdown in the filter form
    employees = User.query.order_by(User.username.asc()).all() if user.role == 'admin' else []

    return render_template(
        'dashboard.html',
        user=user,
        role=user.role,
        logs=logs,
        summary=summary,
        # personal
        my_today=my_today,
        my_today_ot=my_today_ot,
        my_week=my_week,
        my_week_ot=my_week_ot,
        my_clocked_in=my_clocked_in,
        # filters
        employees=employees,
        start_date_val=start_date_str,
        end_date_val=end_date_str,
        employee_val=employee_q
    )

# ----------------------
# Clock in/out
# ----------------------
@app.route('/clock_in')
def clock_in():
    if 'user_id' in session:
        db.session.add(TimeLog(user_id=session['user_id'], clock_in=datetime.now()))
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/clock_out')
def clock_out():
    if 'user_id' in session:
        log = (TimeLog.query
               .filter_by(user_id=session['user_id'], clock_out=None)
               .order_by(TimeLog.clock_in.desc())
               .first())
        if log:
            log.clock_out = datetime.now()
            db.session.commit()
    return redirect(url_for('dashboard'))

# ----------------------
# Exports (CSV / PDF)
# Employees: only own logs
# Admins: all logs (with optional filters)
# ----------------------
@app.route('/export_csv')
def export_csv():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    current_user = User.query.get(session['user_id'])
    is_admin = (current_user.role == 'admin')

    output = io.StringIO()
    writer = csv.writer(output)

    if not is_admin:
        # EMPLOYEE: only their own logs
        logs = (TimeLog.query
                .filter_by(user_id=current_user.id)
                .options(joinedload(TimeLog.user))
                .order_by(TimeLog.clock_in.desc())
                .all())

        writer.writerow(['Username', 'Clock In', 'Clock Out'])
        for log in logs:
            ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
            co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
            writer.writerow([current_user.username, ci, co])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'timelogs_{current_user.username}.csv'
        )

    # ADMIN: with optional filters (date range + employee)
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    employee_q     = request.args.get('employee', '').strip()

    def parse_date(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except:
            return None

    start_dt = end_dt = None
    if start_date_str:
        sd = parse_date(start_date_str)
        if sd: start_dt = datetime.combine(sd, time.min)
    if end_date_str:
        ed = parse_date(end_date_str)
        if ed: end_dt = datetime.combine(ed, time.max)

    logs_query = (TimeLog.query
                  .join(User, TimeLog.user_id == User.id)
                  .options(joinedload(TimeLog.user)))
    if employee_q:
        logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
    if start_dt and end_dt:
        logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
    elif start_dt:
        logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
    elif end_dt:
        logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)

    logs = logs_query.order_by(TimeLog.clock_in.desc()).all()

    writer.writerow(['Username', 'Clock In', 'Clock Out'])
    for log in logs:
        ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
        co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else ''
        writer.writerow([log.user.username, ci, co])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='timelogs_admin.csv'
    )

@app.route('/export_pdf')
def export_pdf():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    current_user = User.query.get(session['user_id'])
    is_admin = (current_user.role == 'admin')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 13)

    if not is_admin:
        # EMPLOYEE: only their own logs
        pdf.cell(0, 10, pdf_safe(f"Time Logs - {current_user.username}"), ln=True, align='C')
        logs = (TimeLog.query
                .filter_by(user_id=current_user.id)
                .options(joinedload(TimeLog.user))
                .order_by(TimeLog.clock_in.desc())
                .all())

        pdf.set_font('Arial', '', 10)
        for log in logs:
            ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
            co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else '-'
            pdf.cell(0, 8, pdf_safe(f"{ci}  |  {co}"), ln=True)

        path = f"timelogs_{current_user.username}.pdf"
        pdf.output(path)
        return send_file(path, as_attachment=True)

    # ADMIN: with optional filters (date range + employee)
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    employee_q     = request.args.get('employee', '').strip()

    def parse_date(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except:
            return None

    start_dt = end_dt = None
    if start_date_str:
        sd = parse_date(start_date_str)
        if sd: start_dt = datetime.combine(sd, time.min)
    if end_date_str:
        ed = parse_date(end_date_str)
        if ed: end_dt = datetime.combine(ed, time.max)

    logs_query = (TimeLog.query
                  .join(User, TimeLog.user_id == User.id)
                  .options(joinedload(TimeLog.user)))
    if employee_q:
        logs_query = logs_query.filter(User.username.ilike(f"%{employee_q}%"))
    if start_dt and end_dt:
        logs_query = logs_query.filter(and_(TimeLog.clock_in >= start_dt, TimeLog.clock_in <= end_dt))
    elif start_dt:
        logs_query = logs_query.filter(TimeLog.clock_in >= start_dt)
    elif end_dt:
        logs_query = logs_query.filter(TimeLog.clock_in <= end_dt)

    logs = logs_query.order_by(TimeLog.clock_in.desc()).all()

    pdf.cell(0, 10, pdf_safe("Employee Time Logs"), ln=True, align='C')
    pdf.set_font('Arial', '', 10)
    for log in logs:
        uname = log.user.username
        ci = log.clock_in.strftime('%Y-%m-%d %H:%M:%S') if log.clock_in else ''
        co = log.clock_out.strftime('%Y-%m-%d %H:%M:%S') if log.clock_out else '-'
        pdf.cell(0, 8, pdf_safe(f"{uname}: {ci}  |  {co}"), ln=True)

    path = 'timelogs_admin.pdf'
    pdf.output(path)
    return send_file(path, as_attachment=True)

# ----------------------
# Admin: add/delete user
# ----------------------
@app.route('/add_user', methods=['GET', 'POST'])
def add_user_web():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        role     = request.form['role'].strip()

        if not username or not password or role not in ('admin', 'employee'):
            return '❌ Invalid input.'
        existing = User.query.filter_by(username=username).first()
        if existing:
            return '❌ User already exists.'

        db.session.add(User(username=username, password=password, role=role))
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('add_user.html')

@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))

    user_to_delete = User.query.filter_by(username=username).first()
    if not user_to_delete:
        return "❌ User not found"
    if user_to_delete.id == session['user_id']:
        return "❌ You can't delete yourself."

    TimeLog.query.filter_by(user_id=user_to_delete.id).delete()
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ----------------------
# Bootstrap DB + run
# ----------------------
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
