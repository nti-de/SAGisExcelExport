import pandas
import pandas.io.formats.excel


def format_excel(file_name: str, index=True, freeze_panes=None, enable_filters=False):
    """Formats the Excel file based on the given options."""

    # Save default header style and set used style to None
    header_style = pandas.io.formats.excel.ExcelFormatter.header_style
    pandas.io.formats.excel.ExcelFormatter.header_style = None

    try:
        with pandas.ExcelFile(file_name) as excel_file:
            sheet_name = excel_file.sheet_names[0]
            dataframe = pandas.read_excel(excel_file)

        with pandas.ExcelWriter(file_name, mode="w", engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, sheet_name, index=index, freeze_panes=freeze_panes)

            worksheet = writer.sheets[sheet_name]

            # Filter
            if enable_filters:
                # Exclude row index
                first_col = 1 if index else 0
                worksheet.autofilter(0, first_col, dataframe.shape[0], dataframe.shape[1] - 1 + first_col)

            # Autofit
            worksheet.autofit()
    finally:
        # Reset to default header style
        pandas.io.formats.excel.ExcelFormatter.header_style = header_style
