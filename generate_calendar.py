import datetime
import argparse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def round_to_week(start_date, end_date):
    start_weekday = start_date.weekday()
    if start_weekday != 6:
        start_date -= datetime.timedelta(days=(start_weekday + 1) % 7)
    end_weekday = end_date.weekday()
    if end_weekday != 5:
        end_date += datetime.timedelta(days=(5 - end_weekday + 7) % 7)
    return start_date, end_date

def generate_weekly_calendar(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, "%Y/%m/%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y/%m/%d").date()
    start_date, end_date = round_to_week(start_date, end_date)

    c = canvas.Canvas("calendar.pdf", pagesize=landscape(letter))
    width, height = landscape(letter)
    margin = 0.5 * inch
    usable_width = width - 2 * margin
    usable_height = height - 2 * margin

    row_height = usable_height / 7
    date_col_width = usable_width * 0.15  # 15% width for date column
    note_col_width = (usable_width - date_col_width) / 4  # 5 equal note columns

    # Pre-calculate vertical line positions
    x_positions = [margin + date_col_width + i * note_col_width for i in range(5)]
    x_positions.insert(0, margin)  # First vertical line (start of date column)
    x_positions.append(width - margin)  # Last vertical border

    current_date = start_date
    while current_date <= end_date:
        week_start = current_date
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, height - margin + 0.1 * inch, f"Week of {week_start.strftime('%B %d, %Y')}")

        # Top border line - thick
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1.0)
        c.line(margin, height - margin, width - margin, height - margin)

        for i in range(7):
            y_top = height - margin - i * row_height
            y_bottom = y_top - row_height
            day_date = week_start + datetime.timedelta(days=i)
            date_part = day_date.strftime("%Y/%m/%d")
            day_part = day_date.strftime("%a")

            # Horizontal row borders - thicker
            c.setLineWidth(2.0)
            c.line(margin, y_bottom, width - margin, y_bottom)

            # Vertical lines - thinner
            c.setLineWidth(0.5)
            for x in x_positions:
                c.line(x, y_top, x, y_bottom)

            # Date text - centered with day in next line
            c.setFillColor(colors.red if i in [0, 6] else colors.black)
            c.setFont("Helvetica-Bold", 12)
            text_x_center = margin + date_col_width / 2
            text_y_center = y_bottom + row_height / 2
            c.drawCentredString(text_x_center, text_y_center + 4, date_part)
            c.drawCentredString(text_x_center, text_y_center - 10, day_part)
            c.setFillColor(colors.black)

        # Bottom and rightmost borders - thick
        c.setLineWidth(1.0)
        c.line(margin, margin, width - margin, margin)
        c.line(width - margin, height - margin, width - margin, margin)

        c.showPage()
        current_date += datetime.timedelta(days=7)

    c.save()
    print("calendar.pdf generated successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a weekly calendar PDF.")
    parser.add_argument("start_date", help="Start date in YYYY/MM/DD format")
    parser.add_argument("end_date", help="End date in YYYY/MM/DD format")
    args = parser.parse_args()

    generate_weekly_calendar(args.start_date, args.end_date)
