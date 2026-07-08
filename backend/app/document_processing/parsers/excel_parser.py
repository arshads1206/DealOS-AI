"""
DealOS AI — Excel/CSV Parser.

Extracts tabular data from Excel and CSV files.
Converts to text representation for chunking and embedding.
"""

import io

import pandas as pd
import structlog

logger = structlog.get_logger(__name__)


class ExcelParser:
    """Extract text content from Excel and CSV files."""

    @staticmethod
    async def parse(content: bytes, filename: str) -> list[dict]:
        """
        Parse an Excel or CSV file and convert to text.

        Each sheet (or the entire CSV) becomes a separate page.
        Tables are converted to a readable text format.
        """
        pages = []
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        try:
            if extension == "csv":
                df = pd.read_csv(io.BytesIO(content))
                text = ExcelParser._dataframe_to_text(df, "CSV Data")
                if text:
                    pages.append({
                        "page_number": 1,
                        "text": text,
                        "metadata": {
                            "source_type": "csv",
                            "rows": len(df),
                            "columns": len(df.columns),
                        },
                    })
            else:
                # Excel with potentially multiple sheets
                excel_file = pd.ExcelFile(io.BytesIO(content))
                for sheet_idx, sheet_name in enumerate(excel_file.sheet_names):
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    text = ExcelParser._dataframe_to_text(df, sheet_name)
                    if text:
                        pages.append({
                            "page_number": sheet_idx + 1,
                            "text": text,
                            "metadata": {
                                "source_type": "xlsx",
                                "sheet_name": sheet_name,
                                "rows": len(df),
                                "columns": len(df.columns),
                            },
                        })

            logger.info("excel_parsed", filename=filename, pages=len(pages))

        except Exception as e:
            logger.error("excel_parse_error", error=str(e))
            raise

        return pages

    @staticmethod
    def _dataframe_to_text(df: pd.DataFrame, title: str) -> str:
        """Convert a DataFrame to a readable text representation."""
        if df.empty:
            return ""

        lines = [f"# {title}", ""]

        # Column headers
        columns = " | ".join(str(col) for col in df.columns)
        lines.append(columns)
        lines.append("-" * len(columns))

        # Data rows (limit to 500 rows for very large files)
        for _, row in df.head(500).iterrows():
            row_text = " | ".join(str(val) for val in row.values)
            lines.append(row_text)

        if len(df) > 500:
            lines.append(f"\n... ({len(df) - 500} more rows)")

        return "\n".join(lines)
