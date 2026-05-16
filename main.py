import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import database
from datetime import datetime, date

database.initialize_database()
database.auto_check_passed_out()

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

C = {
    'bg':        '#F0EFF6',
    'surface':   '#FFFFFF',
    'accent':    '#5B4FCF',
    'accent2':   '#7B6FE0',
    'accent3':   '#DDD9F8',
    'ink':       '#14132A',
    'ink2':      '#3D3B5C',
    'ink3':      '#8585AA',
    'teal':      '#178A64',
    'teal_bg':   '#D8F3E9',
    'amber':     '#A06A00',
    'amber_bg':  '#FDF0D0',
    'coral':     '#B83520',
    'coral_bg':  '#FCEAE5',
    'green_bg':  '#E2F4D4',
    'green':     '#2E6010',
    'sidebar':   '#16152C',
    'sidebar2':  '#1E1D38',
    'divider':   '#E8E7F2',
}

FONT_H1    = ('Segoe UI Semibold', 18)
FONT_TITLE = ('Segoe UI Semibold', 14)
FONT_LABEL = ('Segoe UI', 12)
FONT_BODY  = ('Segoe UI', 11)
FONT_SMALL = ('Segoe UI', 10)
FONT_TINY  = ('Segoe UI', 9)


def make_label(parent, text, font=FONT_LABEL, fg=None, **kw):
    return ctk.CTkLabel(parent, text=text, font=font,
                        text_color=fg or C['ink2'], **kw)


def make_entry(parent, placeholder='', width=220):
    return ctk.CTkEntry(parent, placeholder_text=placeholder, width=width,
                        fg_color=C['surface'], border_color=C['accent3'],
                        text_color=C['ink'], height=36)


def make_btn(parent, text, cmd, style='primary', width=140, icon='', height=36):
    label = f"{icon} {text}" if icon else text
    base = dict(text=label, command=cmd, width=width, height=height,
                font=FONT_LABEL, corner_radius=8)
    if style == 'primary':
        return ctk.CTkButton(parent, **base, fg_color=C['accent'],
                             hover_color=C['accent2'], text_color='white')
    if style == 'danger':
        return ctk.CTkButton(parent, **base, fg_color='#B83520',
                             hover_color='#8C280F', text_color='white')
    if style == 'success':
        return ctk.CTkButton(parent, **base, fg_color=C['teal'],
                             hover_color='#0F6B4C', text_color='white')
    return ctk.CTkButton(parent, **base, fg_color=C['accent3'],
                         hover_color='#C9C4F0', text_color=C['accent'])


def card_frame(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=C['surface'], corner_radius=16, **kw)


def build_treeview(parent, columns, headings, col_widths=None, row_height=42):
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('School.Treeview',
                    background=C['surface'], foreground=C['ink'],
                    rowheight=row_height, fieldbackground=C['surface'],
                    font=('Segoe UI', 11), borderwidth=0)
    style.configure('School.Treeview.Heading',
                    background=C['accent3'], foreground=C['accent'],
                    font=('Segoe UI Semibold', 11), relief='flat', padding=(10, 8))
    style.map('School.Treeview',
              background=[('selected', C['accent'])],
              foreground=[('selected', 'white')])

    frame = tk.Frame(parent, bg=C['bg'], highlightthickness=0)
    frame.pack(fill='both', expand=True)

    vsb = ttk.Scrollbar(frame, orient='vertical')
    vsb.pack(side='right', fill='y')
    hsb = ttk.Scrollbar(frame, orient='horizontal')
    hsb.pack(side='bottom', fill='x')

    tree = ttk.Treeview(frame, columns=columns, show='headings',
                        style='School.Treeview',
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    for col, head in zip(columns, headings):
        tree.heading(col, text=head, anchor='w')
    if col_widths:
        for col, w in zip(columns, col_widths):
            tree.column(col, width=w, minwidth=40, anchor='w')

    tree.tag_configure('even',      background='#F3F2FA')
    tree.tag_configure('odd',       background=C['surface'])
    tree.tag_configure('passedout', foreground='#9999BB', background='#F4F4F8',
                       font=('Segoe UI', 11))
    tree.tag_configure('highlight', foreground=C['teal'])
    tree.pack(fill='both', expand=True)
    return tree


def insert_row(tree, values, status='', idx=0):
    if status == 'Passed Out':
        tag = 'passedout'
    elif idx % 2 == 0:
        tag = 'even'
    else:
        tag = 'odd'
    tree.insert('', 'end', tags=(tag,), values=values)


class SchoolManagementApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("EduCore — School Management System")
        self.geometry("1360x800")
        self.minsize(1100, 700)
        self.configure(fg_color=C['bg'])
        self._build_layout()
        self._build_sidebar()
        self._build_main()
        self._show_page('dashboard')

    def _build_layout(self):
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=C['sidebar'],
                                          width=230, corner_radius=0)
        self.sidebar_frame.pack(side='left', fill='y')
        self.sidebar_frame.pack_propagate(False)
        self.main_frame = ctk.CTkFrame(self, fg_color=C['bg'], corner_radius=0)
        self.main_frame.pack(side='left', fill='both', expand=True)

    def _build_sidebar(self):
        sb = self.sidebar_frame
        brand = ctk.CTkFrame(sb, fg_color='transparent')
        brand.pack(fill='x', padx=18, pady=(26, 14))
        ir = ctk.CTkFrame(brand, fg_color='transparent')
        ir.pack(fill='x')
        ib = ctk.CTkFrame(ir, fg_color=C['accent'], width=46, height=46, corner_radius=12)
        ib.pack(side='left')
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text='🎓', font=('Segoe UI', 22)).pack(expand=True)
        tc = ctk.CTkFrame(ir, fg_color='transparent')
        tc.pack(side='left', padx=(12, 0))
        ctk.CTkLabel(tc, text='EduCore', font=('Segoe UI Bold', 16),
                     text_color='white').pack(anchor='w')
        ctk.CTkLabel(tc, text='School Management', font=FONT_TINY,
                     text_color='#5555AA').pack(anchor='w')

        ctk.CTkFrame(sb, fg_color='#25243F', height=1).pack(fill='x', padx=16, pady=(10, 8))

        self._nav_btns = {}
        for group_label, items in [
            ('MAIN', [('Dashboard', 'dashboard', '📊'),
                      ('Students',  'students',  '👥'),
                      ('Registration', 'register', '➕')]),
            ('ACADEMIC', [('Attendance', 'attendance', '📅'),
                          ('Grades',    'grades',     '🎓'),
                          ('Fees',      'fees',       '💳')]),
            ('SCHOOL', [('Teachers', 'teachers', '🧑‍🏫'),
                        ('Sections', 'sections', '🏫')]),
        ]:
            ctk.CTkLabel(sb, text=group_label, font=('Segoe UI Bold', 8),
                         text_color='#3D3C60').pack(anchor='w', padx=22, pady=(10, 2))
            for label, page, emoji in items:
                btn = ctk.CTkButton(
                    sb, text=f'  {emoji}  {label}',
                    command=lambda p=page: self._show_page(p),
                    fg_color='transparent', hover_color='#26254A',
                    text_color='#8080BB', anchor='w', height=38,
                    corner_radius=10, font=FONT_BODY)
                btn.pack(fill='x', padx=10, pady=1)
                self._nav_btns[page] = btn

        foot = ctk.CTkFrame(sb, fg_color=C['sidebar2'], corner_radius=12)
        foot.pack(side='bottom', fill='x', padx=12, pady=16)
        av = ctk.CTkFrame(foot, fg_color=C['accent'], width=36, height=36, corner_radius=10)
        av.grid(row=0, column=0, rowspan=2, padx=12, pady=12)
        av.grid_propagate(False)
        ctk.CTkLabel(av, text='SA', font=('Segoe UI Bold', 11),
                     text_color='white').place(relx=0.5, rely=0.5, anchor='center')
        ctk.CTkLabel(foot, text='School Admin', font=('Segoe UI Semibold', 11),
                     text_color='white').grid(row=0, column=1, sticky='sw', padx=(0, 10))
        ctk.CTkLabel(foot, text='Administrator', font=FONT_TINY,
                     text_color='#5555AA').grid(row=1, column=1, sticky='nw', padx=(0, 10))

    def _build_main(self):
        mf = self.main_frame
        tb = ctk.CTkFrame(mf, fg_color=C['surface'], height=66, corner_radius=0)
        tb.pack(fill='x')
        tb.pack_propagate(False)

        left_tb = ctk.CTkFrame(tb, fg_color='transparent')
        left_tb.pack(side='left', padx=24)
        self._page_title_var = ctk.StringVar(value='Dashboard')
        ctk.CTkLabel(left_tb, textvariable=self._page_title_var,
                     font=FONT_H1, text_color=C['ink']).pack(pady=20)

        # Search bar
        sb = ctk.CTkFrame(tb, fg_color=C['bg'], corner_radius=10,
                          border_width=1, border_color=C['divider'])
        sb.pack(side='right', padx=16, pady=10, fill='y')

        ctk.CTkLabel(sb, text='🔍', font=('Segoe UI', 13),
                     text_color=C['ink3']).pack(side='left', padx=(12, 4))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add('write', self._on_search_type)
        self._search_entry = ctk.CTkEntry(
            sb, textvariable=self._search_var,
            placeholder_text='Search name, ID, year…',
            width=190, border_width=0, fg_color='transparent',
            text_color=C['ink'], font=FONT_LABEL)
        self._search_entry.pack(side='left', pady=6)
        self._search_entry.bind('<Return>', self._do_search)
        self._search_entry.bind('<FocusIn>', self._show_search_dropdown)
        self._search_entry.bind('<FocusOut>', lambda e: self.after(200, self._hide_search_dropdown))

        def sep():
            ctk.CTkFrame(sb, fg_color=C['divider'], width=1).pack(side='left', fill='y', pady=8)

        sep()
        self._search_grade_var = ctk.StringVar(value='All Grades')
        ctk.CTkOptionMenu(sb, variable=self._search_grade_var,
                          values=['All Grades'] + [f'Grade {g}' for g in range(1, 11)],
                          fg_color=C['bg'], button_color=C['bg'],
                          button_hover_color=C['accent3'], text_color=C['ink2'],
                          dropdown_fg_color=C['surface'], dropdown_text_color=C['ink'],
                          width=115, font=FONT_SMALL).pack(side='left', padx=2)

        sep()
        self._search_section_var = ctk.StringVar(value='All Sections')
        _top_sec_names = ['All Sections'] + sorted(set(
            s['name'] for s in database.get_section_names()
        ))
        ctk.CTkOptionMenu(sb, variable=self._search_section_var,
                          values=_top_sec_names,
                          fg_color=C['bg'], button_color=C['bg'],
                          button_hover_color=C['accent3'], text_color=C['ink2'],
                          dropdown_fg_color=C['surface'], dropdown_text_color=C['ink'],
                          width=112, font=FONT_SMALL).pack(side='left', padx=2)

        sep()
        self._search_status_var = ctk.StringVar(value='All')
        ctk.CTkOptionMenu(sb, variable=self._search_status_var,
                          values=['All', 'Active', 'Passed Out', 'Inactive'],
                          fg_color=C['bg'], button_color=C['bg'],
                          button_hover_color=C['accent3'], text_color=C['ink2'],
                          dropdown_fg_color=C['surface'], dropdown_text_color=C['ink'],
                          width=100, font=FONT_SMALL).pack(side='left', padx=2)

        sep()
        self._search_year_var = ctk.StringVar()
        ctk.CTkEntry(sb, textvariable=self._search_year_var,
                     placeholder_text='Year', width=58, border_width=0,
                     fg_color='transparent', text_color=C['ink'],
                     font=FONT_SMALL).pack(side='left', padx=(6, 2))

        make_btn(sb, 'Search', self._do_search, style='primary',
                 width=74, height=32).pack(side='left', padx=(4, 10))

        self._search_dropdown = None
        self._search_results_cache = []

        self._pages_frame = ctk.CTkFrame(mf, fg_color=C['bg'], corner_radius=0)
        self._pages_frame.pack(fill='both', expand=True)

        self._pages = {}
        self._build_dashboard()
        self._build_students()
        self._build_register()
        self._build_attendance()
        self._build_grades()
        self._build_fees()
        self._build_teachers()
        self._build_sections()

    def _show_page(self, page_id):
        for p in self._pages.values():
            p.pack_forget()
        if page_id in self._pages:
            self._pages[page_id].pack(fill='both', expand=True)
        for pid, btn in self._nav_btns.items():
            btn.configure(fg_color='#26254A' if pid == page_id else 'transparent',
                          text_color='white' if pid == page_id else '#8080BB')
        self._page_title_var.set({
            'dashboard': 'Dashboard', 'students': 'Students',
            'register': 'Register Student', 'attendance': 'Attendance',
            'grades': 'Grades & Exams', 'fees': 'Fees & Payments',
            'teachers': 'Teachers', 'sections': 'Sections',
        }.get(page_id, page_id.title()))
        {
            'students': self._refresh_students,
            'attendance': self._refresh_attendance,
            'grades': self._refresh_grades,
            'fees': self._refresh_fees,
            'teachers': self._refresh_teachers,
            'sections': self._refresh_sections,
            'dashboard': self._refresh_dashboard,
        }.get(page_id, lambda: None)()

    # ── Search ───────────────────────────────────────────────────────────────

    def _parse_filters(self):
        yr = self._search_year_var.get().strip()
        try: year = int(yr) if yr else None
        except ValueError: year = None
        gs = self._search_grade_var.get()
        grade = None if gs == 'All Grades' else gs.replace('Grade ', '')
        ss = self._search_section_var.get()
        section = None if ss == 'All Sections' else ss
        status = self._search_status_var.get()
        return year, grade, section, status

    def _on_search_type(self, *_):
        q = self._search_var.get().strip()
        if len(q) < 1:
            self._hide_search_dropdown()
            return
        year, grade, section, status = self._parse_filters()
        results = database.search_students(q, year_filter=year, grade_filter=grade,
                                           section_filter=section, status_filter=status)
        self._search_results_cache = results
        self._update_search_dropdown(results)

    def _do_search(self, *_):
        self._hide_search_dropdown()
        q = self._search_var.get().strip()
        year, grade, section, status = self._parse_filters()
        self._show_page('students')
        rows = database.search_students(q, year_filter=year, grade_filter=grade,
                                        section_filter=section, status_filter=status,
                                        include_all=True)
        self._populate_students_tree(rows)

    def _show_search_dropdown(self, *_):
        if self._search_results_cache:
            self._update_search_dropdown(self._search_results_cache)

    def _hide_search_dropdown(self):
        if self._search_dropdown:
            try: self._search_dropdown.destroy()
            except Exception: pass
            self._search_dropdown = None

    def _update_search_dropdown(self, results):
        self._hide_search_dropdown()
        if not results: return
        self._search_entry.update_idletasks()
        x = self._search_entry.winfo_rootx() - 20
        y = self._search_entry.winfo_rooty() + self._search_entry.winfo_height() + 4
        count = min(len(results), 9)
        self._search_dropdown = tk.Toplevel(self)
        self._search_dropdown.wm_overrideredirect(True)
        self._search_dropdown.geometry(f"460x{count*46+10}+{x}+{y}")
        self._search_dropdown.configure(bg=C['surface'])
        self._search_dropdown.attributes('-topmost', True)

        for i, s in enumerate(results[:9]):
            sc = {'Active': C['teal'], 'Passed Out': '#9999BB',
                  'Inactive': C['coral']}.get(s['status'], C['ink3'])
            bg = C['bg'] if i % 2 == 0 else C['surface']
            row = tk.Frame(self._search_dropdown, bg=bg, cursor='hand2')
            row.pack(fill='x', padx=4, pady=1)
            inner = tk.Frame(row, bg=bg)
            inner.pack(fill='x', padx=10, pady=8)
            grade_sec = f"G{s['grade']}-{s['section_name']}" if s.get('grade') else '—'
            batch = f"  ·  {s['batch_year']}" if s.get('batch_year') else ''
            tk.Label(inner, text=f"{s['first_name']} {s['last_name']}",
                     bg=bg, fg=C['ink'], font=('Segoe UI Semibold', 11), anchor='w').pack(side='left')
            tk.Label(inner, text=f"  #{s['id']}  {grade_sec}{batch}",
                     bg=bg, fg=C['ink3'], font=('Segoe UI', 9), anchor='w').pack(side='left')
            tk.Label(inner, text=s['status'], bg=bg, fg=sc,
                     font=('Segoe UI Semibold', 9)).pack(side='right')

            def _click(e, sid=s['id']):
                self._hide_search_dropdown()
                self._open_student_detail(sid)
            for w in [row, inner] + list(inner.winfo_children()):
                w.bind('<Button-1>', _click)
            row.bind('<Enter>', lambda e, r=row, b=bg: r.configure(bg=C['accent3']))
            row.bind('<Leave>', lambda e, r=row, b=bg: r.configure(bg=b))

    # ════════════════════════════════════════════════════════════════════════
    # DASHBOARD
    # ════════════════════════════════════════════════════════════════════════

    def _build_dashboard(self):
        page = ctk.CTkScrollableFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['dashboard'] = page

        sr = ctk.CTkFrame(page, fg_color='transparent')
        sr.pack(fill='x', padx=24, pady=(20, 0))
        self._dash_stat_frames = {}
        for i, (key, emoji, label, fg, bg) in enumerate([
            ('students',   '👥', 'Active Students', C['accent'], C['accent3']),
            ('teachers',   '🧑‍🏫', 'Teachers',        C['teal'],   C['teal_bg']),
            ('fees',       '💳', 'Fees Collected',  C['amber'],  C['amber_bg']),
            ('attendance', '📅', 'Attendance Rate', C['coral'],  C['coral_bg']),
        ]):
            card = card_frame(sr)
            card.grid(row=0, column=i, padx=(0, 14), sticky='nsew')
            sr.columnconfigure(i, weight=1)
            ib = ctk.CTkFrame(card, fg_color=bg, width=46, height=46, corner_radius=12)
            ib.pack(anchor='w', padx=20, pady=(20, 0))
            ib.pack_propagate(False)
            ctk.CTkLabel(ib, text=emoji, font=('Segoe UI', 22)).pack(expand=True)
            v = ctk.CTkLabel(card, text='—', font=('Segoe UI Semibold', 28), text_color=C['ink'])
            v.pack(anchor='w', padx=20, pady=(8, 0))
            ctk.CTkLabel(card, text=label, font=FONT_SMALL,
                         text_color=C['ink3']).pack(anchor='w', padx=20, pady=(2, 18))
            self._dash_stat_frames[key] = v

        bot = ctk.CTkFrame(page, fg_color='transparent')
        bot.pack(fill='both', expand=True, padx=24, pady=16)
        bot.columnconfigure(0, weight=2)
        bot.columnconfigure(1, weight=1)

        rc = card_frame(bot)
        rc.grid(row=0, column=0, sticky='nsew', padx=(0, 14))
        rh = ctk.CTkFrame(rc, fg_color='transparent')
        rh.pack(fill='x', padx=18, pady=(18, 8))
        ctk.CTkLabel(rh, text='Recent Registrations', font=FONT_TITLE,
                     text_color=C['ink']).pack(side='left')
        make_btn(rh, 'View All', lambda: self._show_page('students'),
                 style='secondary', width=80, height=28).pack(side='right')
        self._dash_tree = build_treeview(
            rc, columns=('name','section','batch','date','status'),
            headings=('Student','Section','Batch','Registered','Status'),
            col_widths=(170, 100, 60, 110, 80))
        self._dash_tree.bind('<Double-1>', lambda e: self._dash_click())

        qa = card_frame(bot)
        qa.grid(row=0, column=1, sticky='nsew')
        ctk.CTkLabel(qa, text='Quick Actions', font=FONT_TITLE,
                     text_color=C['ink']).pack(anchor='w', padx=18, pady=(18, 14))
        for lbl, pid, col in [
            ('➕  Register Student', 'register',   C['accent3']),
            ('📅  Mark Attendance',  'attendance', C['teal_bg']),
            ('🎓  Enter Grades',     'grades',     C['amber_bg']),
            ('💳  Record Payment',   'fees',       C['coral_bg']),
        ]:
            ctk.CTkButton(qa, text=lbl, command=lambda p=pid: self._show_page(p),
                          fg_color=col, hover_color=C['accent3'], text_color=C['ink2'],
                          anchor='w', corner_radius=10, height=42, font=FONT_LABEL
                          ).pack(fill='x', padx=14, pady=4)

    def _dash_click(self):
        item = self._dash_tree.focus()
        if item:
            vals = self._dash_tree.item(item, 'values')
            if vals:
                results = database.search_students(vals[0])
                if results:
                    self._open_student_detail(results[0]['id'])
                else:
                    self._show_page('students')

    def _refresh_dashboard(self):
        stats = database.get_dashboard_stats()
        self._dash_stat_frames['students'].configure(text=str(stats.get('total_students', 0)))
        self._dash_stat_frames['teachers'].configure(text=str(stats.get('total_teachers', 0)))
        self._dash_stat_frames['fees'].configure(text=f"PKR {(stats.get('fees_collected') or 0):,.0f}")
        self._dash_stat_frames['attendance'].configure(text=f"{stats.get('attendance_rate', 0)}%")
        students = database.get_all_students()[:12]
        for r in self._dash_tree.get_children(): self._dash_tree.delete(r)
        for i, s in enumerate(students):
            sec = f"G{s['grade']}-{s['section_name']}" if s.get('grade') else '—'
            insert_row(self._dash_tree, (
                f"{s['first_name']} {s['last_name']}", sec,
                s.get('batch_year') or '—',
                str(s['registration_date'])[:10], s.get('status', 'Active'),
            ), status=s.get('status', ''), idx=i)

    # ════════════════════════════════════════════════════════════════════════
    # STUDENTS
    # ════════════════════════════════════════════════════════════════════════

    def _build_students(self):
        page = ctk.CTkFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['students'] = page

        # Toolbar
        tb = ctk.CTkFrame(page, fg_color=C['surface'], corner_radius=0, height=56)
        tb.pack(fill='x')
        tb.pack_propagate(False)
        make_btn(tb, '➕ Register New', lambda: self._show_page('register'),
                 width=150).pack(side='right', padx=12, pady=10)
        make_btn(tb, '🗑 Delete', self._delete_selected_student,
                 style='danger', width=100).pack(side='right', padx=(0,8), pady=10)
        make_btn(tb, '👁 Details', self._view_selected_student,
                 style='secondary', width=100).pack(side='right', padx=(0,8), pady=10)
        make_btn(tb, '🔄 Passed Out', self._toggle_show_all,
                 style='secondary', width=140).pack(side='left', padx=12, pady=10)

        # Filter bar
        fb = ctk.CTkFrame(page, fg_color=C['bg'], corner_radius=0)
        fb.pack(fill='x', padx=20, pady=(8, 4))
        make_label(fb, 'Filter:', fg=C['ink3'], font=FONT_SMALL).pack(side='left', padx=(0,8))

        self._stud_grade_var = ctk.StringVar(value='All Grades')
        ctk.CTkOptionMenu(fb, variable=self._stud_grade_var,
                          values=['All Grades']+[f'Grade {g}' for g in range(1,11)],
                          fg_color=C['surface'], button_color=C['accent'],
                          text_color=C['ink'], width=120,
                          command=lambda _: self._refresh_students()).pack(side='left', padx=4)

        self._stud_section_var = ctk.StringVar(value='All Sections')
        _sec_names = ['All Sections'] + sorted(set(
            s['name'] for s in database.get_section_names()
        ))
        ctk.CTkOptionMenu(fb, variable=self._stud_section_var,
                          values=_sec_names,
                          fg_color=C['surface'], button_color=C['accent'],
                          text_color=C['ink'], width=120,
                          command=lambda _: self._refresh_students()).pack(side='left', padx=4)

        self._stud_status_var = ctk.StringVar(value='Active')
        ctk.CTkOptionMenu(fb, variable=self._stud_status_var,
                          values=['All','Active','Passed Out','Inactive'],
                          fg_color=C['surface'], button_color=C['accent'],
                          text_color=C['ink'], width=110,
                          command=lambda _: self._refresh_students()).pack(side='left', padx=4)

        make_label(fb, 'Year:', fg=C['ink3'], font=FONT_SMALL).pack(side='left', padx=(12,4))
        self._stud_year_entry = make_entry(fb, 'e.g. 2023', width=100)
        self._stud_year_entry.pack(side='left')
        make_btn(fb, 'Apply', self._refresh_students, style='secondary', width=70, height=32).pack(side='left', padx=4)
        make_btn(fb, 'Clear', self._clear_student_filters, style='secondary', width=60, height=32).pack(side='left', padx=2)

        self._student_count_lbl = ctk.CTkLabel(fb, text='', font=FONT_SMALL, text_color=C['ink3'])
        self._student_count_lbl.pack(side='right', padx=12)

        self._show_all_students = False

        card = card_frame(page)
        card.pack(fill='both', expand=True, padx=20, pady=(4, 20))
        self._students_tree = build_treeview(
            card,
            columns=('id','name','gender','section','batch','dob','phone','email','status'),
            headings=('ID','Student Name','Gender','Section','Batch','DOB','Phone','Email','Status'),
            col_widths=(40,170,70,110,60,110,120,170,90))
        self._students_tree.bind('<Double-1>', lambda e: self._view_selected_student())

    def _clear_student_filters(self):
        self._stud_grade_var.set('All Grades')
        self._stud_section_var.set('All Sections')
        self._stud_status_var.set('Active')
        self._stud_year_entry.delete(0, 'end')
        self._refresh_students()

    def _toggle_show_all(self):
        self._show_all_students = not self._show_all_students
        self._refresh_students()

    def _refresh_students(self, search=None, year_filter=None, status_filter=None):
        grade_str = self._stud_grade_var.get()
        grade = None if grade_str == 'All Grades' else grade_str.replace('Grade ', '')
        sec_str = self._stud_section_var.get()
        section = None if sec_str == 'All Sections' else sec_str
        status = status_filter or self._stud_status_var.get()
        if status == 'All': status = None
        yr = self._stud_year_entry.get().strip()
        try: year = int(yr) if yr else year_filter
        except ValueError: year = year_filter

        rows = database.search_students(
            search or '', year_filter=year, grade_filter=grade,
            section_filter=section, status_filter=status,
            include_all=self._show_all_students)
        self._populate_students_tree(rows)

    def _populate_students_tree(self, rows):
        for r in self._students_tree.get_children(): self._students_tree.delete(r)
        for i, s in enumerate(rows):
            sec = f"G{s['grade']}-{s['section_name']}" if s.get('grade') else '—'
            insert_row(self._students_tree, (
                s['id'], f"{s['first_name']} {s['last_name']}",
                s.get('gender') or '—', sec,
                s.get('batch_year') or '—', s.get('dob') or '—',
                s.get('phone') or '—', s.get('email') or '—',
                s.get('status', 'Active'),
            ), status=s.get('status', ''), idx=i)
        count = len(rows)
        self._student_count_lbl.configure(text=f"{count} student{'s' if count!=1 else ''}")

    def _get_selected_student_id(self):
        item = self._students_tree.focus()
        if not item: return None
        vals = self._students_tree.item(item, 'values')
        return int(vals[0]) if vals else None

    def _view_selected_student(self):
        sid = self._get_selected_student_id()
        if not sid: messagebox.showinfo('Info', 'Select a student row first.'); return
        self._open_student_detail(sid)

    def _delete_selected_student(self):
        sid = self._get_selected_student_id()
        if not sid: messagebox.showinfo('Info', 'Select a student row first.'); return
        s = database.get_student_by_id(sid)
        if not s: return
        if not messagebox.askyesno('Confirm Delete',
                f"Permanently delete {s['first_name']} {s['last_name']} (ID {sid})?\n"
                "All grades, fees and attendance records will be removed."): return
        ok, err = database.delete_student(sid)
        if ok: messagebox.showinfo('Deleted', 'Student removed.'); self._refresh_students()
        else: messagebox.showerror('Error', err)

    def _open_student_detail(self, student_id):
        s = database.get_student_by_id(student_id)
        if not s: return

        dlg = ctk.CTkToplevel(self)
        dlg.title(f"Student Profile — {s['first_name']} {s['last_name']}")
        dlg.geometry('740x820')
        dlg.minsize(620, 600)
        dlg.resizable(True, True)
        dlg.grab_set()
        dlg.configure(fg_color=C['bg'])

        # ── Header ────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(dlg, fg_color=C['accent'], corner_radius=0, height=124)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        # Avatar circle
        av = ctk.CTkFrame(hdr, fg_color='white', width=68, height=68, corner_radius=34)
        av.pack(side='left', padx=26, pady=28)
        av.pack_propagate(False)
        initials = f"{s['first_name'][0]}{s['last_name'][0]}".upper()
        ctk.CTkLabel(av, text=initials, font=('Segoe UI Bold', 24),
                     text_color=C['accent']).place(relx=0.5, rely=0.5, anchor='center')

        nc = ctk.CTkFrame(hdr, fg_color='transparent')
        nc.pack(side='left', pady=24)
        ctk.CTkLabel(nc, text=f"{s['first_name']} {s['last_name']}",
                     font=('Segoe UI Bold', 20), text_color='white').pack(anchor='w')
        sec = f"Grade {s['grade']} — Section {s['section_name']}" if s.get('grade') else 'No Section Assigned'
        ctk.CTkLabel(nc, text=f"Student ID: #{s['id']}  ·  {sec}",
                     font=('Segoe UI', 12), text_color='#CCCCFF').pack(anchor='w', pady=(4, 0))

        status_colors = {'Active': ('#1A7A4A', '#A0FFA0'), 'Passed Out': ('#55557A', '#CCCCDD'),
                         'Inactive': ('#8C280F', '#FFAAAA'), 'Pending': ('#7A5200', '#FFE0A0')}
        sfg, sbg = status_colors.get(s.get('status', ''), (C['ink'], '#DDDDEE'))
        ctk.CTkLabel(nc, text=f"  {s.get('status', 'Active')}  ",
                     font=('Segoe UI Semibold', 11), fg_color=sbg,
                     text_color=sfg, corner_radius=8).pack(anchor='w', pady=(8, 0))

        # Batch badge top-right
        if s.get('batch_year'):
            ctk.CTkLabel(hdr, text=f"Batch {s['batch_year']}",
                         font=('Segoe UI Semibold', 12), text_color='#AAAAFF').pack(
                side='right', padx=24, pady=48, anchor='e')

        # ── Scrollable body ───────────────────────────────────────────────
        body = ctk.CTkScrollableFrame(dlg, fg_color=C['bg'], corner_radius=0)
        body.pack(fill='both', expand=True)

        def sec_title(text, emoji=''):
            f = ctk.CTkFrame(body, fg_color='transparent')
            f.pack(fill='x', padx=22, pady=(20, 6))
            ctk.CTkLabel(f, text=f"{emoji}  {text}" if emoji else text,
                         font=('Segoe UI Bold', 13),
                         text_color=C['accent']).pack(side='left')
            ctk.CTkFrame(f, fg_color=C['accent3'], height=2).pack(
                side='left', fill='x', expand=True, padx=(12, 0))

        def info_grid(pairs, cols=2):
            g = ctk.CTkFrame(body, fg_color=C['surface'], corner_radius=14)
            g.pack(fill='x', padx=22, pady=4)
            for i in range(cols):
                g.columnconfigure(i, weight=1)
            for idx, (lbl, val) in enumerate(pairs):
                cell = ctk.CTkFrame(g, fg_color='transparent')
                cell.grid(row=idx // cols, column=idx % cols, sticky='ew', padx=20, pady=10)
                ctk.CTkLabel(cell, text=lbl, font=('Segoe UI', 9),
                             text_color=C['ink3']).pack(anchor='w')
                ctk.CTkLabel(cell, text=str(val) if val else '—',
                             font=('Segoe UI Semibold', 13),
                             text_color=C['ink']).pack(anchor='w', pady=(2, 0))

        # Personal Information
        sec_title('Personal Information', '👤')
        info_grid([
            ('Student ID',      f"#{s['id']}"),
            ('Full Name',       f"{s['first_name']} {s['last_name']}"),
            ('Gender',          s.get('gender') or '—'),
            ('Date of Birth',   s.get('dob') or '—'),
            ('Phone Number',    s.get('phone') or '—'),
            ('Email Address',   s.get('email') or '—'),
        ])
        # Address on full width
        if s.get('address'):
            af = ctk.CTkFrame(body, fg_color=C['surface'], corner_radius=14)
            af.pack(fill='x', padx=22, pady=(2, 4))
            ctk.CTkLabel(af, text='Home Address', font=('Segoe UI', 9),
                         text_color=C['ink3']).pack(anchor='w', padx=20, pady=(10, 0))
            ctk.CTkLabel(af, text=s['address'], font=('Segoe UI Semibold', 12),
                         text_color=C['ink'], wraplength=640, justify='left').pack(
                anchor='w', padx=20, pady=(2, 12))

        # Academic Information
        sec_title('Academic Information', '🎓')
        info_grid([
            ('Current Section',    sec),
            ('Status',             s.get('status', 'Active')),
            ('Batch Year',         s.get('batch_year') or '—'),
            ('Enrollment Year',    s.get('enrollment_year') or '—'),
            ('Registration Date',  str(s.get('registration_date', ''))[:10]),
            ('Guardian Name',      s.get('guardian_name') or '—'),
        ])

        # Grade Records
        grades = database.get_grades_by_student(student_id)
        if grades:
            sec_title('Grade Records', '📊')
            gf = ctk.CTkFrame(body, fg_color=C['surface'], corner_radius=14)
            gf.pack(fill='x', padx=22, pady=4)
            # Header row
            hr = ctk.CTkFrame(gf, fg_color=C['accent3'], corner_radius=8)
            hr.pack(fill='x', padx=10, pady=(10, 2))
            for h, w in [('Course', 150), ('Mid', 70), ('Final', 70),
                         ('Assignment', 90), ('Overall', 80), ('Grade', 60), ('Date', 100)]:
                ctk.CTkLabel(hr, text=h, font=('Segoe UI Semibold', 10),
                             text_color=C['accent'], width=w).pack(side='left', padx=4, pady=6)
            for i, g in enumerate(grades):
                grade_color = {'A+': C['teal'], 'A': C['teal'], 'B': C['accent'],
                               'C': C['amber'], 'D': C['coral'], 'F': '#AA0000'}.get(
                    g.get('grade', ''), C['ink2'])
                bg = '#F3F2FA' if i % 2 == 0 else C['surface']
                gr = ctk.CTkFrame(gf, fg_color=bg, corner_radius=4)
                gr.pack(fill='x', padx=10, pady=1)
                for vi, (v, w) in enumerate([
                    (g.get('course_name', '—'), 150),
                    (g.get('mid_term') or '—', 70),
                    (g.get('final_exam') or '—', 70),
                    (g.get('assignment') or '—', 90),
                    (f"{g['overall']}%" if g.get('overall') else '—', 80),
                    (g.get('grade') or '—', 60),
                    (str(g.get('exam_date') or '—')[:10], 100),
                ]):
                    ctk.CTkLabel(gr, text=str(v),
                                 font=('Segoe UI Semibold', 11) if vi == 5 else ('Segoe UI', 11),
                                 text_color=grade_color if vi == 5 else C['ink'],
                                 width=w).pack(side='left', padx=4, pady=6)
            ctk.CTkFrame(gf, fg_color='transparent', height=8).pack()
        else:
            sec_title('Grade Records', '📊')
            ctk.CTkLabel(body, text='No grade records found.',
                         font=FONT_SMALL, text_color=C['ink3']).pack(anchor='w', padx=26, pady=(0, 8))

        # Fee Records
        fees = database.get_fees_by_student(student_id)
        if fees:
            sec_title('Fee Records', '💳')
            ff = ctk.CTkFrame(body, fg_color=C['surface'], corner_radius=14)
            ff.pack(fill='x', padx=22, pady=4)
            paid_tot   = sum(f['amount'] for f in fees if f.get('status') == 'paid')
            unpaid_tot = sum(f['amount'] for f in fees if f.get('status') in ('unpaid', 'overdue', 'partial'))
            summary_row = ctk.CTkFrame(ff, fg_color=C['accent3'], corner_radius=8)
            summary_row.pack(fill='x', padx=10, pady=(10, 4))
            ctk.CTkLabel(summary_row, text=f"✅  Total Paid: PKR {paid_tot:,.0f}",
                         font=('Segoe UI Semibold', 12), text_color=C['teal']).pack(
                side='left', padx=18, pady=8)
            ctk.CTkLabel(summary_row, text=f"⏳  Pending: PKR {unpaid_tot:,.0f}",
                         font=('Segoe UI Semibold', 12), text_color=C['coral']).pack(
                side='left', padx=18)
            ctk.CTkLabel(summary_row, text=f"Total Records: {len(fees)}",
                         font=FONT_SMALL, text_color=C['ink3']).pack(side='right', padx=18)
            for i, f in enumerate(fees):
                sc = C['teal'] if f['status'] == 'paid' else \
                     C['amber'] if f['status'] == 'partial' else C['coral']
                bg = '#F3F2FA' if i % 2 == 0 else C['surface']
                fr = ctk.CTkFrame(ff, fg_color=bg, corner_radius=6)
                fr.pack(fill='x', padx=10, pady=2)
                ctk.CTkLabel(fr, text=f"PKR {f['amount']:,.0f}",
                             font=('Segoe UI Semibold', 13), text_color=C['ink']).pack(
                    side='left', padx=14, pady=8)
                status_badge = ctk.CTkLabel(fr, text=f" {f.get('status', '').capitalize()} ",
                                            font=('Segoe UI Semibold', 10), text_color='white',
                                            fg_color=sc, corner_radius=6)
                status_badge.pack(side='left', padx=4)
                ctk.CTkLabel(fr, text=f"Due: {f.get('due_date') or '—'}",
                             font=FONT_SMALL, text_color=C['ink3']).pack(side='left', padx=10)
                if f.get('paid_date'):
                    ctk.CTkLabel(fr, text=f"Paid on: {f['paid_date']}",
                                 font=FONT_SMALL, text_color=C['teal']).pack(side='left', padx=6)
                if f.get('payment_method'):
                    ctk.CTkLabel(fr, text=f"🏦 {f.get('payment_method')}",
                                 font=FONT_SMALL, text_color=C['ink3']).pack(side='right', padx=14)
            ctk.CTkFrame(ff, fg_color='transparent', height=8).pack()
        else:
            sec_title('Fee Records', '💳')
            ctk.CTkLabel(body, text='No fee records found.',
                         font=FONT_SMALL, text_color=C['ink3']).pack(anchor='w', padx=26, pady=(0, 8))

        # Academic History
        history = database.get_student_history(student_id)
        if history:
            sec_title('Academic History', '📅')
            for h in history:
                hr2 = ctk.CTkFrame(body, fg_color=C['surface'], corner_radius=12)
                hr2.pack(fill='x', padx=22, pady=3)
                yf = ctk.CTkFrame(hr2, fg_color=C['accent'], width=72, corner_radius=10)
                yf.pack(side='left', padx=12, pady=10)
                yf.pack_propagate(False)
                ctk.CTkLabel(yf, text=str(h.get('batch_year') or '?'),
                             font=('Segoe UI Semibold', 12), text_color='white').pack(expand=True)
                info_f = ctk.CTkFrame(hr2, fg_color='transparent')
                info_f.pack(side='left', padx=8, pady=8)
                ctk.CTkLabel(info_f, text=f"Grade {h.get('grade', '?')}",
                             font=('Segoe UI Semibold', 13), text_color=C['ink']).pack(anchor='w')
                ctk.CTkLabel(info_f, text=h.get('status', ''),
                             font=FONT_SMALL, text_color=C['ink3']).pack(anchor='w')
                if h.get('notes'):
                    ctk.CTkLabel(hr2, text=h['notes'], font=FONT_SMALL,
                                 text_color=C['ink3']).pack(side='left', padx=4)

        # Attendance Summary
        try:
            att_summary = database.get_attendance_summary(student_id)
        except Exception:
            att_summary = {}
        if att_summary:
            sec_title('Attendance Summary', '📆')
            present = att_summary.get('present', 0)
            late    = att_summary.get('late', 0)
            absent  = att_summary.get('absent', 0)
            total   = present + late + absent
            rate    = round((present + late * 0.5) / total * 100) if total else 0

            att_card = ctk.CTkFrame(body, fg_color=C['surface'], corner_radius=14)
            att_card.pack(fill='x', padx=22, pady=4)
            att_row = ctk.CTkFrame(att_card, fg_color='transparent')
            att_row.pack(fill='x', padx=18, pady=14)
            for label, val, color in [
                ('Present', present, C['teal']),
                ('Late',    late,    C['amber']),
                ('Absent',  absent,  C['coral']),
                ('Rate',    f"{rate}%", C['accent']),
            ]:
                ac = ctk.CTkFrame(att_row, fg_color=C['bg'], corner_radius=10)
                ac.pack(side='left', expand=True, fill='x', padx=6, pady=0)
                ctk.CTkLabel(ac, text=str(val), font=('Segoe UI Bold', 20),
                             text_color=color).pack(pady=(10, 2))
                ctk.CTkLabel(ac, text=label, font=FONT_TINY,
                             text_color=C['ink3']).pack(pady=(0, 10))

        ctk.CTkFrame(body, fg_color='transparent', height=16).pack()

        # ── Action bar ───────────────────────────────────────────────────
        act = ctk.CTkFrame(dlg, fg_color=C['surface'], corner_radius=0, height=68)
        act.pack(fill='x', side='bottom')
        act.pack_propagate(False)

        if s.get('status') == 'Active':
            def mark_passed():
                ok, err = database.mark_student_passed_out(student_id)
                if ok:
                    messagebox.showinfo('Done', 'Marked as Passed Out.', parent=dlg)
                    dlg.destroy()
                    self._refresh_students()
                else:
                    messagebox.showerror('Error', err, parent=dlg)
            make_btn(act, 'Mark Passed Out', mark_passed,
                     style='secondary', width=160).pack(side='left', padx=16, pady=16)

        if s.get('status') == 'Passed Out':
            make_btn(act, '🔄 Re-Enroll',
                     lambda: self._open_reenroll_dialog(student_id, dlg),
                     style='success', width=130).pack(side='left', padx=16, pady=16)

        def del_student():
            if messagebox.askyesno('Confirm', 'Delete this student permanently?', parent=dlg):
                ok, err = database.delete_student(student_id)
                if ok:
                    dlg.destroy()
                    self._refresh_students()
                else:
                    messagebox.showerror('Error', err, parent=dlg)

        make_btn(act, '🗑 Delete', del_student, style='danger', width=100).pack(
            side='right', padx=16, pady=16)
        make_btn(act, 'Close', dlg.destroy, style='secondary', width=90).pack(
            side='right', padx=(0, 8), pady=16)

    def _open_reenroll_dialog(self, student_id, parent_dlg=None):
        dlg = ctk.CTkToplevel(self)
        dlg.title('Re-Enroll Student')
        dlg.geometry('440x340')
        dlg.grab_set()
        dlg.configure(fg_color=C['bg'])
        s = database.get_student_by_id(student_id)
        ctk.CTkLabel(dlg, text=f"Re-Enroll: {s['first_name']} {s['last_name']}",
                     font=FONT_TITLE).pack(pady=(24,16))
        sections = database.get_section_names()
        sec_labels = [f"Grade {sec['grade']}-{sec['name']}" for sec in sections]
        f1 = ctk.CTkFrame(dlg, fg_color='transparent')
        f1.pack(fill='x', padx=24, pady=8)
        make_label(f1, 'New Section / Grade').pack(anchor='w')
        sec_var = ctk.StringVar(value=sec_labels[0] if sec_labels else '')
        ctk.CTkOptionMenu(f1, variable=sec_var, values=sec_labels or ['—'],
                          fg_color=C['surface'], button_color=C['accent'],
                          text_color=C['ink'], height=36).pack(fill='x', pady=(4,0))
        f2 = ctk.CTkFrame(dlg, fg_color='transparent')
        f2.pack(fill='x', padx=24, pady=8)
        make_label(f2, 'Batch Year').pack(anchor='w')
        be = make_entry(f2, str(date.today().year), width=999)
        be.pack(fill='x', pady=(4,0))
        be.insert(0, str(date.today().year))

        def submit():
            sel = sec_var.get()
            section_id = next((s2['id'] for s2 in sections
                               if f"Grade {s2['grade']}-{s2['name']}" == sel), None)
            if not section_id: messagebox.showerror('Error','Select section.',parent=dlg); return
            try: yr = int(be.get().strip())
            except ValueError: messagebox.showerror('Error','Enter valid year.',parent=dlg); return
            ok,err = database.re_enroll_student(student_id, section_id, yr)
            if ok:
                messagebox.showinfo('Success',f'Re-enrolled in batch {yr}.',parent=dlg)
                dlg.destroy()
                if parent_dlg: parent_dlg.destroy()
                self._refresh_students()
            else: messagebox.showerror('Error',err,parent=dlg)
        make_btn(dlg,'✅ Re-Enroll',submit,width=200).pack(pady=20)

    # ════════════════════════════════════════════════════════════════════════
    # REGISTRATION
    # ════════════════════════════════════════════════════════════════════════

    def _build_register(self):
        page = ctk.CTkScrollableFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['register'] = page
        outer = ctk.CTkFrame(page, fg_color='transparent')
        outer.pack(fill='both', expand=True, padx=24, pady=16)
        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=1)

        form_card = card_frame(outer)
        form_card.grid(row=0, column=0, sticky='nsew', padx=(0,14))

        fhdr = ctk.CTkFrame(form_card, fg_color=C['accent'], corner_radius=0, height=52)
        fhdr.pack(fill='x')
        fhdr.pack_propagate(False)
        ctk.CTkLabel(fhdr, text='  👤  New Student Registration',
                     font=('Segoe UI Semibold', 14), text_color='white').pack(side='left', padx=16)

        self._reg = {}
        grid = ctk.CTkFrame(form_card, fg_color='transparent')
        grid.pack(fill='x', padx=20, pady=(16,0))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        fn_row = 0; col = 0
        for key, label, span in [
            ('first_name', 'First Name',                 0),
            ('last_name',  'Last Name',                  0),
            ('dob',        'Date of Birth (YYYY-MM-DD)', 1),
            ('phone',      'Phone Number',               1),
            ('email',      'Email Address',              1),
            ('address',    'Home Address',               1),
        ]:
            cell = ctk.CTkFrame(grid, fg_color='transparent')
            if span:
                cell.grid(row=fn_row, column=0, columnspan=2, sticky='ew', pady=6, padx=2)
                fn_row += 1
            else:
                cell.grid(row=fn_row//2, column=col, sticky='ew', pady=6,
                          padx=(2,8) if col==0 else (8,2))
                col = 1-col
                if col == 0: fn_row += 1
            ctk.CTkLabel(cell, text=label, font=('Segoe UI Semibold',11),
                         text_color=C['ink3']).pack(anchor='w')
            e = make_entry(cell, placeholder=label, width=999)
            e.pack(fill='x', pady=(2,0))
            self._reg[key] = e

        row2 = ctk.CTkFrame(form_card, fg_color='transparent')
        row2.pack(fill='x', padx=20, pady=(12,0))
        for i in range(4): row2.columnconfigure(i, weight=1)

        def make_dropdown_cell(col_idx, label, values, var_attr, cmd=None):
            cell = ctk.CTkFrame(row2, fg_color='transparent')
            cell.grid(row=0, column=col_idx, sticky='ew', padx=(0,8) if col_idx<3 else 0)
            ctk.CTkLabel(cell, text=label, font=('Segoe UI Semibold',11),
                         text_color=C['ink3']).pack(anchor='w')
            var = ctk.StringVar(value=values[0])
            m = ctk.CTkOptionMenu(cell, variable=var, values=values,
                                  fg_color=C['surface'], button_color=C['accent'],
                                  text_color=C['ink'], height=36, command=cmd)
            m.pack(fill='x', pady=(2,0))
            return var, m

        self._reg['gender'], _ = make_dropdown_cell(0, 'Gender', ['Male','Female','Other'], '_')
        self._reg_grade_var, _ = make_dropdown_cell(
            1, 'Grade (1–10)', [str(g) for g in range(1,11)], '_',
            cmd=self._on_reg_grade_change)

        sec_cell = ctk.CTkFrame(row2, fg_color='transparent')
        sec_cell.grid(row=0, column=2, sticky='ew', padx=(0,8))
        ctk.CTkLabel(sec_cell, text='Section', font=('Segoe UI Semibold',11),
                     text_color=C['ink3']).pack(anchor='w')
        self._sections_data = database.get_section_names()
        self._reg_sec_var = ctk.StringVar(value='A')
        self._reg_section_menu = ctk.CTkOptionMenu(
            sec_cell, variable=self._reg_sec_var, values=['A','B','C','D'],
            fg_color=C['surface'], button_color=C['accent'],
            text_color=C['ink'], height=36)
        self._reg_section_menu.pack(fill='x', pady=(2,0))
        self._on_reg_grade_change('1')

        batch_cell = ctk.CTkFrame(row2, fg_color='transparent')
        batch_cell.grid(row=0, column=3, sticky='ew')
        ctk.CTkLabel(batch_cell, text='Batch Year', font=('Segoe UI Semibold',11),
                     text_color=C['ink3']).pack(anchor='w')
        self._reg_batch_entry = make_entry(batch_cell, str(date.today().year), width=999)
        self._reg_batch_entry.pack(fill='x', pady=(2,0))
        self._reg_batch_entry.insert(0, str(date.today().year))

        btn_row = ctk.CTkFrame(form_card, fg_color='transparent')
        btn_row.pack(fill='x', padx=20, pady=20)
        make_btn(btn_row, '🔄 Clear', self._clear_register, style='secondary', width=120).pack(side='left')
        make_btn(btn_row, '✅ Register Student', self._submit_register, width=180).pack(side='right')

        info_card = card_frame(outer)
        info_card.grid(row=0, column=1, sticky='nsew')
        ihdr = ctk.CTkFrame(info_card, fg_color=C['teal_bg'], corner_radius=0, height=48)
        ihdr.pack(fill='x')
        ihdr.pack_propagate(False)
        ctk.CTkLabel(ihdr, text='  💡  Tips', font=FONT_TITLE,
                     text_color=C['teal']).pack(side='left', padx=16)
        for icon, tip in [
            ('✅','First & last name required'),
            ('📅','DOB format: YYYY-MM-DD'),
            ('🏫','Grades 1–10, Sections A–D'),
            ('📧','Email must be unique'),
            ('📆','Batch year = enrollment year'),
            ('🔄','Passed out students can re-enroll'),
            ('🔍','Search by name, ID or year'),
        ]:
            rf = ctk.CTkFrame(info_card, fg_color='transparent')
            rf.pack(fill='x', padx=16, pady=5)
            ctk.CTkLabel(rf, text=icon, font=FONT_BODY, width=26).pack(side='left')
            ctk.CTkLabel(rf, text=tip, font=FONT_SMALL, text_color=C['ink2'],
                         wraplength=150, justify='left').pack(side='left', padx=6)

    def _on_reg_grade_change(self, grade_val):
        sections = [s for s in self._sections_data if str(s['grade'])==str(grade_val)]
        names = [s['name'] for s in sections] or ['A','B','C','D']
        self._reg_section_menu.configure(values=names)
        self._reg_sec_var.set(names[0])

    def _clear_register(self):
        for w in self._reg.values():
            if isinstance(w, ctk.CTkEntry): w.delete(0,'end')
        self._reg_batch_entry.delete(0,'end')
        self._reg_batch_entry.insert(0, str(date.today().year))

    def _submit_register(self):
        first = self._reg['first_name'].get().strip()
        last  = self._reg['last_name'].get().strip()
        if not first or not last:
            messagebox.showerror('Error','First and last name are required.')
            return
        dob     = self._reg['dob'].get().strip() or None
        phone   = self._reg['phone'].get().strip() or None
        email   = self._reg['email'].get().strip() or None
        address = self._reg['address'].get().strip() or None
        gender  = self._reg['gender'].get()
        grade   = self._reg_grade_var.get()
        sec_name = self._reg_sec_var.get()
        section_id = next((s['id'] for s in self._sections_data
                           if str(s['grade'])==str(grade) and s['name']==sec_name), None)
        try: batch_yr = int(self._reg_batch_entry.get().strip())
        except ValueError: messagebox.showerror('Error','Enter a valid batch year.'); return
        new_id, err = database.register_student(
            first, last, dob, gender, address, phone, email,
            section_id, batch_year=batch_yr, enrollment_year=batch_yr)
        if err: messagebox.showerror('Error', f'Registration failed:\n{err}'); return
        if messagebox.askyesno('✅ Registered',
                               f'Student ID: {new_id}  —  {first} {last}\n\nView student profile?'):
            self._clear_register()
            self._open_student_detail(new_id)
        else:
            self._clear_register()

    # ════════════════════════════════════════════════════════════════════════
    # ATTENDANCE
    # ════════════════════════════════════════════════════════════════════════

    def _build_attendance(self):
        page = ctk.CTkFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['attendance'] = page

        tb = ctk.CTkFrame(page, fg_color=C['surface'], corner_radius=0, height=56)
        tb.pack(fill='x')
        tb.pack_propagate(False)
        make_label(tb, 'Date:', fg=C['ink3']).pack(side='left', padx=(16,4))
        self._att_date = make_entry(tb, date.today().isoformat(), width=140)
        self._att_date.pack(side='left', padx=4, pady=10)
        self._att_date.insert(0, date.today().isoformat())
        make_label(tb, 'Section:', fg=C['ink3']).pack(side='left', padx=(12,4))
        sections = database.get_section_names()
        self._att_sections = sections
        sec_labels = [f"Grade {s['grade']}-{s['name']}" for s in sections]
        self._att_section_var = ctk.StringVar(value=sec_labels[0] if sec_labels else '')
        ctk.CTkOptionMenu(tb, variable=self._att_section_var, values=sec_labels or ['None'],
                          fg_color=C['surface'], button_color=C['accent'],
                          text_color=C['ink'], width=160).pack(side='left', padx=4)
        make_btn(tb, '📥 Load', self._load_attendance_students, style='secondary', width=90).pack(side='left',padx=8)
        make_btn(tb, '💾 Save', self._save_attendance, width=130).pack(side='right', padx=12)

        card = card_frame(page)
        card.pack(fill='both', expand=True, padx=20, pady=(8,20))
        self._att_tree = build_treeview(card,
            columns=('id','name','status'),
            headings=('ID','Student','Status'),
            col_widths=(50,280,120))
        self._att_status_map = {}
        self._att_controls = ctk.CTkScrollableFrame(card, fg_color=C['surface'], height=260)
        self._att_controls.pack(fill='x', padx=4, pady=4)
        self._att_rows_widgets = []

    def _load_attendance_students(self):
        sel = self._att_section_var.get()
        section_id = next((s['id'] for s in self._att_sections
                           if f"Grade {s['grade']}-{s['name']}"==sel), None)
        att_date = self._att_date.get().strip() or date.today().isoformat()
        for w in self._att_rows_widgets: w.destroy()
        self._att_rows_widgets.clear(); self._att_status_map.clear()
        for r in self._att_tree.get_children(): self._att_tree.delete(r)

        rows = database.get_attendance_by_date(att_date, section_id)
        for i, r in enumerate(rows):
            sid = r['id']; name = f"{r['first_name']} {r['last_name']}"
            status = r.get('status') or 'present'
            var = ctk.StringVar(value=status)
            self._att_status_map[sid] = var
            insert_row(self._att_tree, (sid, name, status.capitalize()), idx=i)
            row_f = ctk.CTkFrame(self._att_controls,
                                 fg_color=C['bg'] if i%2==0 else C['surface'], corner_radius=8)
            row_f.pack(fill='x', padx=6, pady=2)
            make_label(row_f, f"#{sid}", fg=C['ink3'], font=FONT_TINY, width=32).pack(side='left',padx=(10,0))
            make_label(row_f, name, fg=C['ink'], font=FONT_LABEL, width=210).pack(side='left',padx=8)
            for opt, col in [('present',C['teal']),('late',C['amber']),('absent',C['coral'])]:
                ctk.CTkRadioButton(row_f, text=opt.capitalize(), variable=var, value=opt,
                                   text_color=C['ink2'], fg_color=col, font=FONT_BODY,
                                   command=lambda s=sid,v=var: self._update_att_tree(s,v)
                                   ).pack(side='left', padx=12)
            self._att_rows_widgets.append(row_f)

    def _update_att_tree(self, student_id, var):
        for item in self._att_tree.get_children():
            vals = self._att_tree.item(item,'values')
            if int(vals[0]) == student_id:
                self._att_tree.item(item, values=(vals[0],vals[1],var.get().capitalize()))
                break

    def _save_attendance(self):
        att_date = self._att_date.get().strip() or date.today().isoformat()
        if not self._att_status_map: messagebox.showwarning('Warning','Load students first.'); return
        errors = []
        for sid, var in self._att_status_map.items():
            ok,err = database.mark_attendance(sid, att_date, var.get())
            if not ok: errors.append(f'Student {sid}: {err}')
        if errors: messagebox.showerror('Errors','\n'.join(errors))
        else: messagebox.showinfo('✅ Saved', f'Attendance saved for {att_date}.')

    def _refresh_attendance(self):
        self._att_date.delete(0,'end')
        self._att_date.insert(0, date.today().isoformat())

    # ════════════════════════════════════════════════════════════════════════
    # GRADES
    # ════════════════════════════════════════════════════════════════════════

    def _build_grades(self):
        page = ctk.CTkFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['grades'] = page
        tb = ctk.CTkFrame(page, fg_color=C['surface'], corner_radius=0, height=56)
        tb.pack(fill='x')
        tb.pack_propagate(False)
        make_label(tb, 'Course:', fg=C['ink3']).pack(side='left', padx=(16,6))
        self._grade_courses = []
        self._grade_course_var = ctk.StringVar()
        self._grade_course_menu = ctk.CTkOptionMenu(
            tb, variable=self._grade_course_var, values=['—'],
            command=lambda _: self._refresh_grades(),
            fg_color=C['surface'], button_color=C['accent'],
            text_color=C['ink'], width=220)
        self._grade_course_menu.pack(side='left', padx=4)
        make_btn(tb, '✏️ Add / Edit Grade', self._open_grade_dialog, width=160).pack(side='right',padx=12)
        card = card_frame(page)
        card.pack(fill='both', expand=True, padx=20, pady=(8,20))
        self._grades_tree = build_treeview(card,
            columns=('id','name','section','midterm','final','assign','overall','grade'),
            headings=('ID','Student','Section','Mid-Term','Final','Assignment','Overall','Grade'),
            col_widths=(40,170,110,80,80,90,80,60))

    def _refresh_grades(self):
        conn = database.create_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM courses ORDER BY name")
            self._grade_courses = [dict(r) for r in cur.fetchall()]
            cur.close(); conn.close()
        labels = [f"{c['id']} — {c['name']}" for c in self._grade_courses]
        if labels:
            self._grade_course_menu.configure(values=labels)
            if not self._grade_course_var.get() or self._grade_course_var.get()=='—':
                self._grade_course_var.set(labels[0])
        sel = self._grade_course_var.get()
        course_id = next((c['id'] for c in self._grade_courses if sel.startswith(str(c['id']))), None)
        for r in self._grades_tree.get_children(): self._grades_tree.delete(r)
        if course_id is None: return
        for i, s in enumerate(database.get_grades_by_course(course_id)):
            tag = ('even' if i%2==0 else 'odd')
            self._grades_tree.insert('','end',tags=(tag,),values=(
                s['id'], f"{s['first_name']} {s['last_name']}",
                f"G{s['section_grade']}-{s['section_name']}" if s.get('section_grade') else '—',
                s.get('mid_term') or '—', s.get('final_exam') or '—',
                s.get('assignment') or '—',
                f"{s['overall']}%" if s.get('overall') else '—',
                s.get('grade') or '—',
            ))

    def _open_grade_dialog(self):
        item = self._grades_tree.focus()
        if not item: messagebox.showinfo('Info','Select a student row first.'); return
        vals = self._grades_tree.item(item,'values')
        student_id = int(vals[0])
        course_id = next((c['id'] for c in self._grade_courses
                          if self._grade_course_var.get().startswith(str(c['id']))), None)
        if not course_id: return

        dlg = ctk.CTkToplevel(self)
        dlg.title('Enter Grades')
        dlg.geometry('380x360')
        dlg.grab_set()
        dlg.configure(fg_color=C['bg'])

        hdr = ctk.CTkFrame(dlg, fg_color=C['accent'], height=56, corner_radius=0)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f'  🎓  Grades: {vals[1]}',
                     font=FONT_TITLE, text_color='white').pack(side='left', padx=16)

        body = ctk.CTkFrame(dlg, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=24, pady=16)
        entries = {}
        for label, key in [('Mid-Term (0–100)','mid'),('Final Exam (0–100)','final'),('Assignment (0–100)','assignment')]:
            f = ctk.CTkFrame(body, fg_color='transparent')
            f.pack(fill='x', pady=6)
            ctk.CTkLabel(f, text=label, font=('Segoe UI Semibold',11), text_color=C['ink3']).pack(anchor='w')
            e = make_entry(f, placeholder='e.g. 85', width=999)
            e.pack(fill='x', pady=(2,0))
            entries[key] = e
        f3 = ctk.CTkFrame(body, fg_color='transparent')
        f3.pack(fill='x', pady=6)
        ctk.CTkLabel(f3, text='Exam Date (YYYY-MM-DD)', font=('Segoe UI Semibold',11), text_color=C['ink3']).pack(anchor='w')
        de = make_entry(f3, date.today().isoformat(), width=999)
        de.pack(fill='x', pady=(2,0))

        def submit():
            try: mid=float(entries['mid'].get()); fin=float(entries['final'].get()); asg=float(entries['assignment'].get())
            except ValueError: messagebox.showerror('Error','Enter valid numbers.',parent=dlg); return
            ok,err = database.save_grade(student_id, course_id, mid, fin, asg, de.get().strip() or date.today().isoformat())
            if ok: messagebox.showinfo('✅ Saved','Grade saved.',parent=dlg); dlg.destroy(); self._refresh_grades()
            else: messagebox.showerror('Error',err,parent=dlg)
        make_btn(body,'💾 Save Grade',submit,width=999,height=40).pack(fill='x',pady=(12,0))

    # ════════════════════════════════════════════════════════════════════════
    # FEES
    # ════════════════════════════════════════════════════════════════════════

    def _build_fees(self):
        page = ctk.CTkFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['fees'] = page

        stats = ctk.CTkFrame(page, fg_color='transparent')
        stats.pack(fill='x', padx=20, pady=(16, 8))
        self._fee_stat_labels = {}
        for i, (key, label, emoji, bg, fg) in enumerate([
            ('collected',    'Total Collected', '✅', C['teal_bg'],  C['teal']),
            ('pending',      'Pending Amount',  '⏳', C['amber_bg'], C['amber']),
            ('pending_count','Pending Records', '📋', C['accent3'],  C['accent']),
        ]):
            c = card_frame(stats)
            c.grid(row=0, column=i, padx=(0, 14), sticky='ew')
            stats.columnconfigure(i, weight=1)
            top = ctk.CTkFrame(c, fg_color='transparent')
            top.pack(fill='x', padx=18, pady=(18, 0))
            icon_box = ctk.CTkFrame(top, fg_color=bg, width=40, height=40, corner_radius=10)
            icon_box.pack(side='left')
            icon_box.pack_propagate(False)
            ctk.CTkLabel(icon_box, text=emoji, font=('Segoe UI', 18)).pack(expand=True)
            lbl = ctk.CTkLabel(top, text='—', font=('Segoe UI Bold', 24), text_color=fg)
            lbl.pack(side='right', padx=4)
            ctk.CTkLabel(c, text=label, font=('Segoe UI', 11),
                         text_color=C['ink3']).pack(anchor='w', padx=18, pady=(6, 18))
            self._fee_stat_labels[key] = lbl

        main = ctk.CTkFrame(page, fg_color='transparent')
        main.pack(fill='both', expand=True, padx=20, pady=(0,20))
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=1)

        lc = card_frame(main)
        lc.grid(row=0, column=0, sticky='nsew', padx=(0,14))
        lhdr = ctk.CTkFrame(lc, fg_color='transparent')
        lhdr.pack(fill='x', padx=18, pady=(16,8))
        ctk.CTkLabel(lhdr, text='Fee Ledger', font=FONT_TITLE, text_color=C['ink']).pack(side='left')
        self._fee_status_filter = ctk.StringVar(value='All')
        ctk.CTkOptionMenu(lhdr, variable=self._fee_status_filter,
                          values=['All','Paid','Unpaid','Overdue'],
                          fg_color=C['accent3'], button_color=C['accent'],
                          text_color=C['accent'], width=100,
                          command=lambda _: self._refresh_fees()).pack(side='right')
        self._fees_tree = build_treeview(lc,
            columns=('id','student','amount','due','paid','method','status'),
            headings=('ID','Student','Amount','Due Date','Paid Date','Method','Status'),
            col_widths=(40,160,95,100,100,110,80))
        self._fees_tree.bind('<Double-1>', self._on_fee_row_click)

        pc = card_frame(main)
        pc.grid(row=0, column=1, sticky='nsew')
        phdr = ctk.CTkFrame(pc, fg_color=C['accent'], corner_radius=0, height=52)
        phdr.pack(fill='x')
        phdr.pack_propagate(False)
        ctk.CTkLabel(phdr, text='  💳  Record New Payment',
                     font=('Segoe UI Semibold', 13), text_color='white').pack(side='left', padx=16)

        fs = ctk.CTkScrollableFrame(pc, fg_color='transparent')
        fs.pack(fill='both', expand=True)
        self._fee = {}

        f_stu = ctk.CTkFrame(fs, fg_color='transparent')
        f_stu.pack(fill='x', padx=16, pady=(14,4))
        ctk.CTkLabel(f_stu, text='Student', font=('Segoe UI Semibold',11),
                     text_color=C['ink3']).pack(anchor='w')
        self._fee_stu_search = make_entry(f_stu, 'Type name or ID…', width=999)
        self._fee_stu_search.pack(fill='x', pady=(4,0))
        self._fee_stu_search.bind('<KeyRelease>', self._on_fee_student_search)

        self._fee_stu_result_frame = ctk.CTkFrame(fs, fg_color=C['bg'], corner_radius=8)
        self._fee_stu_result_frame.pack(fill='x', padx=16, pady=(2,0))
        self._fee_selected_student_id = None
        self._fee_selected_label = ctk.CTkLabel(fs, text='No student selected',
                                                font=FONT_SMALL, text_color=C['ink3'],
                                                fg_color=C['bg'], corner_radius=6)
        self._fee_selected_label.pack(fill='x', padx=16, pady=(2,8))

        for label, key, wtype, opts in [
            ('Amount (PKR)',   'amount',   'entry',  None),
            ('Due Date',       'due_date', 'entry',  None),
            ('Payment Method', 'method',   'option', ['Cash','Bank Transfer','Cheque']),
            ('Status',         'status',   'option', ['paid','unpaid','partial','overdue']),
            ('Notes',          'notes',    'entry',  None),
        ]:
            f = ctk.CTkFrame(fs, fg_color='transparent')
            f.pack(fill='x', padx=16, pady=5)
            ctk.CTkLabel(f, text=label, font=('Segoe UI Semibold',11),
                         text_color=C['ink3']).pack(anchor='w')
            if wtype == 'option':
                w = ctk.CTkOptionMenu(f, values=opts, fg_color=C['surface'],
                                      button_color=C['accent'], text_color=C['ink'], height=36)
            else:
                w = make_entry(f, placeholder=label, width=999)
            w.pack(fill='x', pady=(4,0))
            self._fee[key] = w

        make_btn(fs, '💾 Record Payment', self._submit_fee, width=999, height=40).pack(fill='x',padx=16,pady=16)

    def _on_fee_student_search(self, event):
        q = self._fee_stu_search.get().strip()
        for w in self._fee_stu_result_frame.winfo_children(): w.destroy()
        if len(q) < 1: return
        for s in database.search_students(q)[:6]:
            sec = f"G{s['grade']}-{s['section_name']}" if s.get('grade') else ''
            name = f"{s['first_name']} {s['last_name']}"
            lbl = f"{name}  #{s['id']}  {sec}"
            ctk.CTkButton(self._fee_stu_result_frame, text=lbl,
                          fg_color='transparent', hover_color=C['accent3'],
                          text_color=C['ink2'], anchor='w', height=30, font=FONT_SMALL,
                          command=lambda sid=s['id'], n=name: self._select_fee_student(sid,n)
                          ).pack(fill='x', padx=4, pady=1)

    def _select_fee_student(self, sid, name):
        self._fee_selected_student_id = sid
        self._fee_selected_label.configure(
            text=f"  ✅  {name} (ID {sid})", text_color=C['teal'])
        for w in self._fee_stu_result_frame.winfo_children(): w.destroy()
        self._fee_stu_search.delete(0,'end')
        self._fee_stu_search.insert(0, name)

    def _on_fee_row_click(self, event):
        item = self._fees_tree.focus()
        if not item: return
        vals = self._fees_tree.item(item,'values')
        if not vals: return
        fee_id = int(vals[0])
        conn = database.create_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT student_id FROM fees WHERE id=?", (fee_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if row: self._open_student_detail(row['student_id'])

    def _refresh_fees(self):
        summary = database.get_fee_summary()
        collected = summary.get('collected') or 0
        pending = (summary.get('pending') or 0) + (summary.get('overdue') or 0)
        self._fee_stat_labels['collected'].configure(text=f"PKR {collected:,.0f}")
        self._fee_stat_labels['pending'].configure(text=f"PKR {pending:,.0f}")
        self._fee_stat_labels['pending_count'].configure(text=str(summary.get('pending_count') or 0))

        filt = self._fee_status_filter.get() if hasattr(self,'_fee_status_filter') else 'All'
        for r in self._fees_tree.get_children(): self._fees_tree.delete(r)
        for i, row in enumerate(database.get_all_fees()):
            s = (row.get('status') or '').capitalize()
            if filt != 'All' and s.lower() != filt.lower(): continue
            tag = 'even' if i%2==0 else 'odd'
            self._fees_tree.insert('','end',tags=(tag,),values=(
                row['id'], f"{row['first_name']} {row['last_name']}",
                f"PKR {row['amount']:,.0f}", row.get('due_date') or '—',
                row.get('paid_date') or '—', row.get('payment_method') or '—', s,
            ))

    def _submit_fee(self):
        student_id = self._fee_selected_student_id
        if not student_id: messagebox.showerror('Error','Search and select a student first.'); return
        try: amount = float(self._fee['amount'].get())
        except ValueError: messagebox.showerror('Error','Enter a valid amount.'); return
        due = self._fee['due_date'].get().strip() or date.today().isoformat()
        fee_status = self._fee['status'].get()
        new_id, err = database.add_fee_record(student_id, amount, due, status=fee_status)
        if err: messagebox.showerror('Error', err); return
        if fee_status == 'paid':
            database.record_payment(new_id, date.today().isoformat(), self._fee['method'].get())
        messagebox.showinfo('✅ Success', f'Fee record saved.')
        self._fee_selected_student_id = None
        self._fee_selected_label.configure(text='No student selected', text_color=C['ink3'])
        self._fee_stu_search.delete(0,'end')
        for w in [self._fee['amount'], self._fee['due_date']]:
            if isinstance(w, ctk.CTkEntry): w.delete(0,'end')
        self._refresh_fees()

    # ════════════════════════════════════════════════════════════════════════
    # TEACHERS — SCROLLABLE RESPONSIVE DIALOG
    # ════════════════════════════════════════════════════════════════════════

    def _build_teachers(self):
        page = ctk.CTkFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['teachers'] = page
        tb = ctk.CTkFrame(page, fg_color=C['surface'], corner_radius=0, height=56)
        tb.pack(fill='x')
        tb.pack_propagate(False)
        make_btn(tb, '➕ Add Teacher', self._open_add_teacher_dialog, width=150).pack(side='right',padx=12,pady=10)
        make_btn(tb, '🗑 Delete', self._delete_selected_teacher, style='danger', width=100).pack(side='right',padx=(0,8),pady=10)
        card = card_frame(page)
        card.pack(fill='both', expand=True, padx=20, pady=(8,20))
        self._teachers_tree = build_treeview(card,
            columns=('id','name','subject','email','phone'),
            headings=('ID','Name','Subject','Email','Phone'),
            col_widths=(40,200,140,240,140))

    def _refresh_teachers(self):
        for r in self._teachers_tree.get_children(): self._teachers_tree.delete(r)
        for i, t in enumerate(database.get_all_teachers()):
            insert_row(self._teachers_tree, (
                t['id'], f"{t['first_name']} {t['last_name']}",
                t.get('subject') or '—', t.get('email') or '—', t.get('phone') or '—',
            ), idx=i)

    def _delete_selected_teacher(self):
        item = self._teachers_tree.focus()
        if not item: messagebox.showinfo('Info','Select a teacher row first.'); return
        vals = self._teachers_tree.item(item,'values')
        if messagebox.askyesno('Confirm',f'Delete teacher: {vals[1]}?'):
            ok,err = database.delete_teacher(int(vals[0]))
            if ok: self._refresh_teachers()
            else: messagebox.showerror('Error',err)

    def _open_add_teacher_dialog(self):
        """Fully scrollable teacher dialog — never needs maximising."""
        dlg = ctk.CTkToplevel(self)
        dlg.title('Add New Teacher')
        dlg.resizable(True, True)
        dlg.configure(fg_color=C['bg'])
        dlg.grab_set()

        # Colored header
        hdr = ctk.CTkFrame(dlg, fg_color=C['accent'], corner_radius=0, height=60)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text='  🧑‍🏫  Add New Teacher',
                     font=('Segoe UI Semibold', 15), text_color='white').pack(side='left', padx=18, pady=16)

        # Footer buttons — always visible BELOW scroll, packed BEFORE scroll so it's always shown
        foot = ctk.CTkFrame(dlg, fg_color=C['surface'], corner_radius=0, height=64)
        foot.pack(fill='x', side='bottom')
        foot.pack_propagate(False)

        # All fields in a scrollable frame — fully responsive
        scroll = ctk.CTkScrollableFrame(dlg, fg_color='transparent', width=440)
        scroll.pack(fill='both', expand=True)

        entries = {}
        for key, label, required in [
            ('first_name',    'First Name *',          True),
            ('last_name',     'Last Name *',           True),
            ('email',         'Email Address',         False),
            ('phone',         'Phone Number',          False),
            ('subject',       'Subject / Department',  False),
            ('qualification', 'Qualification',         False),
            ('experience',    'Years of Experience',   False),
            ('address',       'Office / Home Address', False),
        ]:
            f = ctk.CTkFrame(scroll, fg_color='transparent')
            f.pack(fill='x', padx=26, pady=6)
            ctk.CTkLabel(f, text=label,
                         font=('Segoe UI Semibold', 12),
                         text_color=C['accent'] if required else C['ink3']).pack(anchor='w')
            e = ctk.CTkEntry(f, placeholder_text=label.replace(' *', ''),
                             fg_color=C['surface'], border_color=C['accent3'],
                             text_color=C['ink'], height=38, font=('Segoe UI', 12))
            e.pack(fill='x', pady=(4, 0))
            entries[key] = e

        # Gender
        fg2 = ctk.CTkFrame(scroll, fg_color='transparent')
        fg2.pack(fill='x', padx=26, pady=6)
        ctk.CTkLabel(fg2, text='Gender', font=('Segoe UI Semibold', 12),
                     text_color=C['ink3']).pack(anchor='w')
        gender_var = ctk.StringVar(value='Male')
        ctk.CTkOptionMenu(fg2, variable=gender_var, values=['Male', 'Female', 'Other'],
                          fg_color=C['surface'], button_color=C['accent'],
                          text_color=C['ink'], height=38,
                          font=('Segoe UI', 12)).pack(fill='x', pady=(4, 0))

        ctk.CTkLabel(scroll, text='* Required fields', font=FONT_TINY,
                     text_color=C['ink3']).pack(anchor='w', padx=26, pady=(4, 16))

        def submit():
            fn = entries['first_name'].get().strip()
            ln = entries['last_name'].get().strip()
            if not fn or not ln:
                messagebox.showerror('Error', 'First and last name are required.', parent=dlg)
                return
            ok, err = database.add_teacher(fn, ln,
                entries['email'].get().strip(),
                entries['phone'].get().strip(),
                entries['subject'].get().strip())
            if err:
                messagebox.showerror('Error', err, parent=dlg)
            else:
                messagebox.showinfo('✅ Added', f'Teacher {fn} {ln} added.', parent=dlg)
                dlg.destroy()
                self._refresh_teachers()

        make_btn(foot, 'Cancel', dlg.destroy, style='secondary', width=100).pack(
            side='right', padx=14, pady=14)
        make_btn(foot, '✅ Add Teacher', submit, width=170).pack(
            side='right', padx=(0, 8), pady=14)

        # Center dialog — sized to show ~6 fields without scrolling
        dlg.update_idletasks()
        dlg.geometry('480x620')
        dlg.minsize(400, 440)
        x = self.winfo_x() + (self.winfo_width() - 480) // 2
        y = self.winfo_y() + (self.winfo_height() - 620) // 2
        dlg.geometry(f'480x620+{max(0, x)}+{max(0, y)}')

    # ════════════════════════════════════════════════════════════════════════
    # SECTIONS
    # ════════════════════════════════════════════════════════════════════════

    def _build_sections(self):
        page = ctk.CTkScrollableFrame(self._pages_frame, fg_color=C['bg'], corner_radius=0)
        self._pages['sections'] = page
        self._sections_cards_frame = ctk.CTkFrame(page, fg_color='transparent')
        self._sections_cards_frame.pack(fill='both', expand=True, padx=24, pady=16)

    def _refresh_sections(self):
        for w in self._sections_cards_frame.winfo_children(): w.destroy()
        sections = database.get_sections()
        color_sets = [(C['accent'],C['accent3']),(C['teal'],C['teal_bg']),
                      (C['amber'],C['amber_bg']),(C['coral'],C['coral_bg'])]
        emojis = ['🏫','📚','✏️','🎒']
        secs_by_grade = {}
        for sec in sections:
            secs_by_grade.setdefault(str(sec['grade']), []).append(sec)

        row_idx = 0
        for grade in sorted(secs_by_grade.keys(), key=lambda x: int(x)):
            hdr = ctk.CTkFrame(self._sections_cards_frame, fg_color='transparent')
            hdr.grid(row=row_idx, column=0, columnspan=4, sticky='ew', pady=(16,4))
            ctk.CTkLabel(hdr, text=f'  Grade {grade}',
                         font=('Segoe UI Bold',15), text_color=C['ink']).pack(side='left')
            ctk.CTkFrame(hdr, fg_color=C['divider'], height=1).pack(
                side='left', fill='x', expand=True, padx=12)
            row_idx += 1
            for ci, sec in enumerate(secs_by_grade[grade]):
                fg_c, bg_c = color_sets[ci%4]
                c = card_frame(self._sections_cards_frame)
                c.grid(row=row_idx, column=ci%4, padx=6, pady=6, sticky='nsew')
                self._sections_cards_frame.columnconfigure(ci%4, weight=1)
                ib = ctk.CTkFrame(c, fg_color=bg_c, width=50, height=50, corner_radius=12)
                ib.pack(anchor='w', padx=20, pady=(20,0))
                ib.pack_propagate(False)
                ctk.CTkLabel(ib, text=emojis[ci%4], font=('Segoe UI',24)).pack(expand=True)
                ctk.CTkLabel(c, text=f"Grade {sec['grade']} — Section {sec['name']}",
                             font=('Segoe UI Semibold',13), text_color=C['ink']).pack(anchor='w',padx=20,pady=(12,2))
                ctk.CTkLabel(c, text=f"{sec.get('student_count',0)} active students",
                             font=FONT_SMALL, text_color=C['ink3']).pack(anchor='w',padx=20,pady=(0,16))
            row_idx += 1


if __name__ == '__main__':
    app = SchoolManagementApp()
    app.mainloop()
