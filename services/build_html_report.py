from typing import List, Dict, Any 

class BuildHtmlReport:
    def __call__(self, report: List[Dict[str, Any]]) -> str:
        rows = []

        for item in report:
            row_number = item.get("row", "")
            recipient = item.get("recipient", "")
            status = item.get("status", False)
            error = item.get("error")

            status_text = "Sent" if status else "Failed"
            error_text = error or ""

            rows.append(
                f'''
                    <tr>
                        <td>{row_number}</td>
                        <td>{recipient}</td>
                        <td>{status_text}</td>
                        <td>{error_text}</td>
                    </tr>
                '''
            )

        return f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">

                <style>
                    body {{
                        font-family: Arial, Helvetica, sans-serif;
                        background-color: #f5f5f5;
                        margin: 0;
                        padding: 30px;
                    }}

                    .container {{
                        max-width: 900px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 10px;
                    }}

                    h2 {{
                        margin-top: 0;
                        color: #222222;
                    }}

                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}

                    th,
                    td {{
                        border: 1px solid #dddddd;
                        padding: 10px;
                        text-align: left;
                    }}

                    th {{
                        background-color: #f0f0f0;
                        font-weight: bold;
                    }}

                    tr:nth-child(even) {{
                        background-color: #fafafa;
                    }}
                </style>
            </head>

            <body>
                <div class="container">

                    <h2>MailmanAI Report</h2>

                    <p>
                        Report about the email dispatch task.
                    </p>

                    <table>
                        <thead>
                            <tr>
                                <th>Row</th>
                                <th>Recipient</th>
                                <th>Status</th>
                                <th>Error</th>
                            </tr>
                        </thead>

                        <tbody>
                            {"".join(rows)}
                        </tbody>
                    </table>

                </div>
            </body>
            </html>
        '''