from typing import Optional

import pandas
import pandas as pd
from PyQt5.QtCore import QDateTime, QLocale
from qgis.core import QgsMessageLog, QgsTask

from . import SagisWorksheetType
from .excelexportcontext import ExcelExportContext


class ExcelExportTask(QgsTask):

    def __init__(self, context: ExcelExportContext):
        super().__init__(description="Excel Export")

        self.context = context
        self.object_ids = self.context.object_ids

        self.worksheet_configs = [w for w in self.context.config.sagis_excel_export_item.work_sheet if w.active]
        self.total = len(self.object_ids) * len(self.worksheet_configs)
        self.counter = 0

        self.error: Optional[Exception] = None

    def run(self) -> bool:
        # Debugging
        # import pycharm_debugging
        # pycharm_debugging.connect_debugger()

        if not self.context.config:
            return False
        if not self.context.datasource.database:
            return False
        if not self.object_ids:
            return False

        try:
            dataframes = []

            for worksheet_config in self.worksheet_configs:
                if self.isCanceled():
                    return False

                dataframe = self.process_worksheet(worksheet_config)
                if dataframe is not None and not dataframe.empty:
                    dataframes.append(dataframe)

            if self.isCanceled():
                return False

            self.write_file(dataframes)

            # data: list[(list[str], list[list])] = []  # list of tuples (column_names, data lists)
            # for worksheet in self.worksheet_configs:
            #     if self.isCanceled():
            #         return False
            #     column_names, data_lists = self.process_worksheet(worksheet)
            #     if not column_names or not data_lists:
            #         continue
            #     data.append((column_names, data_lists))
            # self.write_file2(data)

            return True
        except Exception as ex:
            self.error = ex.__repr__()
            return False

    # def finished(self, result: bool) -> None:
    #     if result:
    #         if result:
    #             QgsMessageLog.logMessage("Excel Export finished successfully", "SAGis Alkis Search", level=Qgis.MessageLevel.Info)
    #         else:
    #             QgsMessageLog.logMessage("Excel Export finished with errors", "SAGis Alkis Search")

    def cancel(self):
        QgsMessageLog.logMessage("Excel Export cancelled", "SAGis Alkis Search")
        super().cancel()

    def process_worksheet(self, worksheet: SagisWorksheetType) -> Optional[pd.DataFrame]:
        data_dicts = self.get_worksheet_data(worksheet)
        if not data_dicts:
            return None

        dataframe = pd.DataFrame(data_dicts)
        result_dataframe = dataframe

        # Geometry as WKT
        # geom_columns = self.context.datasource.get_geom_columns(
        #     self.context.config.sagis_excel_export_item.feature_class)
        # for column in geom_columns:
        #     result_dataframe = dataframe[column].apply(self.context.datasource.geom_as_wkt)

        if worksheet.order_by:
            column_names = result_dataframe.columns.tolist()
            if worksheet.order_by in column_names:
                return result_dataframe.sort_values(worksheet.order_by)
            # Try to find column name with differing case.
            for column in column_names:
                if column.lower() == worksheet.order_by.lower():
                    return result_dataframe.sort_values(column)
        return result_dataframe

    def get_worksheet_data(self, worksheet: SagisWorksheetType) -> list[dict]:
        data_dicts = []
        for object_id in self.object_ids:
            if self.isCanceled():
                return []

            sql = worksheet.sql.format(object_id)  # Insert object id
            data = self.get_data(sql)
            if data:
                data_dicts.extend(data)
            self.counter += 1
            self.setProgress(self.counter / self.total * 100)

        return data_dicts

    def get_data(self, sql: str) -> list[dict]:
        if not sql:
            return []
        result = self.context.datasource.select_into_dict_list(sql, null_value_to_none=True)
        if not result:
            return []

        # Format dates
        locale = QLocale.system()
        result = [{k: v.toString(locale.dateFormat(locale.ShortFormat)) if isinstance(v, QDateTime) else v for k, v in row.items()} for row in result]

        # Geometry as WKT
        # geom_columns = self.context.datasource.get_geom_columns('ax_flurstueck', to_lower=True)
        # result = [{k: self.context.datasource.geom_as_wkt(v) if k in geom_columns else v for k, v in row.items()} for row in result]

        return result

    def write_file(self, dataframes: list[pd.DataFrame]):
        num_dataframes = len(dataframes)
        num_worksheet_configs = len(self.worksheet_configs)

        if num_dataframes != num_worksheet_configs:
            if self.context.datasource.error_text:
                raise ConnectionError(self.context.datasource.error_text)
            raise ValueError(
                f"Number of active worksheet configurations({num_worksheet_configs}) does not match number of dataframes ({num_dataframes})"
            )

        file_path = self.context.file_path

        with pandas.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            for i, config in enumerate(self.worksheet_configs):
                dataframe = dataframes[i]

                # #######
                # data = {"type1": ["a", "b", "c"], "type2": [1, 2, 3], "type3": ["a1", "b2", "c3"]}
                # dataframe = pd.DataFrame.from_dict(data)
                # #######

                sheet_name = f"{config.work_sheet_name} ({len(dataframe.index)})"[:31]

                # Write file
                dataframe.to_excel(writer, sheet_name=sheet_name, header=True, index=False)

                # Get worksheet
                worksheet = writer.sheets[sheet_name]

                # Rename columns
                if config.column_header_aliases and config.column_header_aliases.alias:
                    column_aliases = {a.column_name.lower(): a.title for a in config.column_header_aliases.alias}

                    # Comments
                    for alias in config.column_header_aliases.alias:
                        if not alias.value:
                            continue
                        column_name = alias.column_name.lower()
                        if column_name not in dataframe:
                            continue
                        col_index = dataframe.columns.get_loc(column_name)
                        worksheet.write_comment(0, col_index, alias.value, {"font_name": "Calibri", "font_size": 11})
                else:
                    column_aliases = {}

                # Change worksheet tab color
                if config.tab_color:
                    worksheet.set_tab_color(config.tab_color.lower())

                # Add table
                max_row, max_col = dataframe.shape
                columns = [{"header": column_aliases.get(column_name, column_name)} for column_name in dataframe.columns.values]
                worksheet.add_table(0, 0, max_row, max_col - 1, options={"style": "Table Style Medium 1", "columns": columns})

                # Autofit columns
                worksheet.autofit()

                for k, info in worksheet.col_info.items():
                    if info[0] == 255.0:
                        max_len = max([len(str(s)) for s in dataframe.iloc[:, k].values] + [len(dataframe.columns[k])])
                        worksheet.set_column(k, k, max_len)
