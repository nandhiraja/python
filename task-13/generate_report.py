import argparse
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import smtplib
from email.message import EmailMessage
import os
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="PDF Report Generator")
    parser.add_argument('--month', type=str, required=True, help="Month in YYYY-MM format")
    parser.add_argument('--template', type=str, required=True, help="Template name (without .html)")
    return parser.parse_args()

def fetch_data(month_str):
    print(f"[1/5] Connecting to database... OK")
    conn = sqlite3.connect('data/sales.db')
    
    query_curr = f"""
        SELECT sale_date, region, revenue, units 
        FROM sales 
        WHERE strftime('%Y-%m', sale_date) = '{month_str}'
    """
    df_curr = pd.read_sql_query(query_curr, conn)
    
    dt = datetime.strptime(month_str, "%Y-%m")
    if dt.month == 1:
        prev_month = f"{dt.year - 1}-12"
    else:
        prev_month = f"{dt.year}-{dt.month - 1:02d}"
        
    query_prev = f"""
        SELECT region, SUM(revenue) as prev_revenue 
        FROM sales 
        WHERE strftime('%Y-%m', sale_date) = '{prev_month}'
        GROUP BY region
    """
    df_prev = pd.read_sql_query(query_prev, conn)
    conn.close()
    
    print(f"[2/5] Querying {dt.strftime('%B %Y')} sales data... OK ({len(df_curr)} records)")
    return df_curr, df_prev, dt

def process_data(df_curr, df_prev):
    total_revenue = df_curr['revenue'].sum()
    total_units = df_curr['units'].sum()
    avg_order_value = total_revenue / total_units if total_units > 0 else 0
    
    region_stats = df_curr.groupby('region').agg({
        'revenue': 'sum',
        'units': 'sum'
    }).reset_index()
    
    if not df_prev.empty:
        region_stats = region_stats.merge(df_prev, on='region', how='left')
        region_stats['prev_revenue'] = region_stats['prev_revenue'].fillna(0)
        region_stats['growth'] = region_stats.apply(
            lambda row: ((row['revenue'] - row['prev_revenue']) / row['prev_revenue'] * 100) if row['prev_revenue'] > 0 else 0,
            axis=1
        )
    else:
        region_stats['growth'] = 0
        
    total_prev_revenue = df_prev['prev_revenue'].sum() if not df_prev.empty else 0
    mom_growth = ((total_revenue - total_prev_revenue) / total_prev_revenue * 100) if total_prev_revenue > 0 else 0
    
    declining_regions = region_stats[region_stats['growth'] < 0].to_dict('records')
    
    return {
        'total_revenue': total_revenue,
        'total_units': total_units,
        'avg_order_value': avg_order_value,
        'mom_growth': mom_growth,
        'region_stats': region_stats.to_dict('records'),
        'declining_regions': declining_regions
    }

def generate_charts(df_curr, region_stats):
    plt.figure(figsize=(8, 4))
    regions = [r['region'] for r in region_stats]
    revenues = [r['revenue'] for r in region_stats]
    plt.bar(regions, revenues, color=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'])
    plt.title('Revenue by Region')
    plt.ylabel('Revenue ($)')
    plt.tight_layout()
    
    buf_bar = io.BytesIO()
    plt.savefig(buf_bar, format='png')
    buf_bar.seek(0)
    bar_chart_b64 = base64.b64encode(buf_bar.read()).decode('utf-8')
    plt.close()
    
    daily_sales = df_curr.groupby('sale_date')['revenue'].sum().reset_index()
    plt.figure(figsize=(10, 4))
    plt.plot(daily_sales['sale_date'], daily_sales['revenue'], marker='o', linestyle='-', color='#8e44ad')
    plt.title('Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    
    ax = plt.gca()
    for index, label in enumerate(ax.xaxis.get_ticklabels()):
        if index % 3 != 0:
            label.set_visible(False)
            
    plt.tight_layout()
    
    buf_line = io.BytesIO()
    plt.savefig(buf_line, format='png')
    buf_line.seek(0)
    line_chart_b64 = base64.b64encode(buf_line.read()).decode('utf-8')
    plt.close()
    
    return bar_chart_b64, line_chart_b64

def generate_pdf(html_content, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(
            src=html_content,
            dest=result_file
        )
    return not pisa_status.err

def send_email(pdf_path, month_str):
    print(f"[5/5] Sending email...")
    print(f"      To: exec-team@company.com, sales-leads@company.com")
    print(f"      Subject: \"{month_str} Sales Report\"")
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"      Attachment: {os.path.basename(pdf_path)} ({file_size_mb:.1f} MB)")
    
    msg = EmailMessage()
    msg['Subject'] = f"{month_str} Sales Report"
    msg['From'] = 'reports@company.com'
    msg['To'] = 'exec-team@company.com, sales-leads@company.com'
    msg.set_content("Please find attached the monthly sales report.")
    
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
        
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))
    
    print(f"      Sent successfully")

def main():
    args = parse_args()
    
    print("=== Report Generation ===")
    print(f"$ python generate_report.py --month {args.month} --template {args.template}\n")
    
    df_curr, df_prev, dt = fetch_data(args.month)
    
    if df_curr.empty:
        print("No data found for the given month.")
        return
        
    metrics = process_data(df_curr, df_prev)
    bar_chart_b64, line_chart_b64 = generate_charts(df_curr, metrics['region_stats'])
    
    print(f"[3/5] Rendering template \"{args.template}\"...")
    print(f"      - Header: \"Monthly Sales Report — {dt.strftime('%B %Y')}\"")
    print(f"      - Summary Table: revenue, units sold, avg order value")
    print(f"      - Bar Chart: revenue by region")
    print(f"      - Line Chart: daily sales trend")
    
    if metrics['declining_regions']:
        declines = ", ".join([r['region'] for r in metrics['declining_regions']])
        print(f"      - Conditional Section: \"{declines} region(s) declined MoM\" (included)")
    else:
        print(f"      - Conditional Section: No declining regions (skipped)")
        
    print(f"      - Footer: page numbers, generation timestamp")
    
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(f'{args.template}.html')
    
    html_out = template.render(
        month_name=dt.strftime('%B'),
        year=dt.year,
        generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        bar_chart_b64=bar_chart_b64,
        line_chart_b64=line_chart_b64,
        **metrics
    )
    
    print(f"[4/5] Generating PDF...")
    output_pdf_path = f"reports/sales_report_{args.month}.pdf"
    success = generate_pdf(html_out, output_pdf_path)
    if success:
        print(f"      OK")
    else:
        print(f"      Failed")
        
    send_email(output_pdf_path, dt.strftime('%B %Y'))
    
    print(f"\nOutput: {output_pdf_path}")

if __name__ == "__main__":
    main()
