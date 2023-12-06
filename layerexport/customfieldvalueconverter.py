from PyQt5.QtCore import QVariant
from qgis.core import QgsApplication, QgsField, QgsVectorFileWriter, QgsVectorLayer


class CustomFieldValueConverter(QgsVectorFileWriter.FieldValueConverter):

    def __init__(self, layer: QgsVectorLayer, prefer_alias=True):
        QgsVectorFileWriter.FieldValueConverter.__init__(self)
        self.__formattersAllowList = ["CheckBox", "DateTime", "KeyValue", "List", "RelationReference", "ValueRelation", "ValueMap"]
        self.layer = layer
        self.__prefer_alias = prefer_alias
        self.__mFormatters = {}
        self.__mConfig = {}

        for i, field in enumerate(layer.fields()):
            setup = field.editorWidgetSetup()
            fieldFormatter = QgsApplication.fieldFormatterRegistry().fieldFormatter(setup.type())
            if fieldFormatter.id() in self.__formattersAllowList:
                self.__mFormatters[i] = fieldFormatter
                self.__mConfig[i] = setup.config()

    def fieldDefinition(self, field):
        if not self.layer:
            return field
        idx = self.layer.fields().indexFromName(field.name())
        if idx in self.__mFormatters:
            field_name = self.layer.attributeDisplayName(idx) if self.__prefer_alias else field.name()
            if idx == "DateTime":
                return QgsField(field_name, QVariant.DateTime)
            return QgsField(field_name, QVariant.String)
        else:
            return field

    def convert(self, idx, value):
        formatter = self.__mFormatters.get(idx)
        if formatter is None:
            return value
        return formatter.representValue(self.layer, idx, self.__mConfig.get(idx), None, value)

    def clone(self):
        return CustomFieldValueConverter(self.layer, self.__prefer_alias)
