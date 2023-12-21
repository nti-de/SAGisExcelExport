# SAGis Excel Export

SAGis Excel Export ist eine Erweiterung für die GIS-Software QGIS zum Exportieren von XLSX-Dateien.

## Funktionen

- Einfacher Export-Dialog mit Auswahl von Attributfeldern
  - Auswählbare Attributfelder basierend auf der Konfiguration des Attributformulars in den Layer-Eigenschaften (verstecke Elemente werden ignoriert, verwendung von Aliase)
  - Einige erweiterte Einstellung zur Formatierung der XLSX-Datei
- Export-Dialog für den Export aus einer PostgreSQL-Datenbank anhand von vordefinierten XML-Vorlagen (/resources/config/Export/SAGisExcelExportDefinition.xsd)

## Nutzung

### Software-Voraussetzungen

- QGIS >= 3.28.12
- PostgreSQL (nur für Export mit Vorlage) >= 12 mit PostGIS 3.1

### Installation

SAGis Excel Export kann über das QGIS-Plugin Repository heruntergeladen werden.

Für eine erfolgreiche Ausführung des Programms müssen zudem folgende Python-Komponenten installiert werden:
- openpyxl (getestet mit Version 3.0.9)
- pandas (getestet mit Version 2.0.2)
- xlsxwriter (getestet mit Version 3.1.9)
- xsdata (getestet mit Version 23.8)

<details><summary><b>Anleitung anzeigen</b></summary>

1. Suchen Sie das Installationsverzeichnis von QGIS (Zumeist `C:\OSGeo4W\` oder `C:\Program Files\QGIS 3.*'`)

2. Im Verzeichnis befindet sich die _OSGeo4W-Shell_ (Datei mit dem Namen `OSGeo4W.bat`). Starten Sie die _OSGeo4W-Shell_ und führen Sie den folgenden Befehl im sich öffnenden Programm aus:

  ```sh
  o4w_env & python3 -m pip install openpyxl pandas xlsxwriter xsdata
  ```
</details>

### Kontakt
- Mail: qgis-de@nti-group.com
- Web: https://www.nti-group.com/de
---

<sup>
Copyright © 2023 NTI Deutschland GmbH
</sup></br>
<sup>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
</sup>
<sup>
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
</sup>
<sup>
You should have received a copy of the GNU General Public License
along with this program.  If not, see https://www.gnu.org/licenses/.
</sup>