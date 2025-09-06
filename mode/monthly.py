import datetime
import calendar
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def _round_to_month(start_date: datetime.date, end_date: datetime.date):
    start_date = start_date.replace(day=1)
    next_month = (end_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    end_date = next_month - datetime.timedelta(days=1)
    return start_date, end_date


def generate(start_date_str: str, end_date_str: str) -> None:
    start_date = datetime.datetime.strptime(start_date_str, "%Y/%m/%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y/%m/%d").date()
    start_date, end_date = _round_to_month(start_date, end_date)

    c = canvas.Canvas("calendar.pdf", pagesize=landscape(letter))
    width, height = landscape(letter)
    margin = 0.5 * inch
    usable_width = width - 2 * margin
    usable_height = height - 2 * margin

    cal = calendar.Calendar(firstweekday=6)  # Sunday as first day

    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        month_matrix = cal.monthdayscalendar(year, month)
        num_weeks = len(month_matrix)

        row_height = usable_height / num_weeks
        col_width = usable_width / 7

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - margin + 0.1 * inch, f"{calendar.month_name[month]} {year}")

        # Draw grid
        c.setLineWidth(1.0)
        for i in range(num_weeks + 1):
            y = height - margin - i * row_height
            c.line(margin, y, width - margin, y)
        for j in range(8):
            x = margin + j * col_width
            c.line(x, height - margin, x, margin)

        # Fill dates
        for week_idx, week in enumerate(month_matrix):
            y_top = height - margin - week_idx * row_height
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                x_left = margin + day_idx * col_width
                text_x = x_left + 2
                text_y = y_top - 14
                c.setFillColor(colors.red if day_idx in [0, 6] else colors.black)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(text_x, text_y, str(day))
                c.setFillColor(colors.black)

        c.showPage()
        current_date = (current_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)

    c.save()
    print("calendar.pdf generated successfully!")
