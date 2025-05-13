"""Details of the table data for the tables to be scraped."""

# pylint: disable=W0718 - # broad-exception-caught
# pylint: disable=W0105 - # pointless-string-statement

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


"""Potential other file downloads:
Bills:
    https://ibs.stoneprofits.com/ListBills.aspx
    https://ibs.stoneprofits.com/vBill.aspx?ID=110687

    
"""


class TableType(Enum):
    """Define the type of table for scraping."""

    SUBLINKS = 1
    DATA = 2
    FILES = 3


@dataclass
class TableInfoDataClass:
    """Information for scraping a table. The key is the user-friendly name.

    Attributes:
        table_name (str): The HTML element representing the main table
            (e.g., "#ListOpenPurchaseOrdersTable").
        table_type (TableType): The type of table (e.g., SUBLINKS, DATA,
            FILES).
        url_path (str, optional): The relative URL path of the webpage
            containing the table (e.g., "/listPos.aspx?tab=4"). (The base
            URL will be added.)
        table_key_name (str, optional): A description of the field used as
            a key (e.g., "purchase_order"). Only used for SUBLINK
            table_type.
        column_number (int, optional): Zero-based column number of the
            sub-table link (SUBLINK table_type) or the file to download
            (FILES table_type).
        subtables (Optional[Dict[str, "TableInfoDataClass"]], optional):
            A dict of child TableInfoDataClass objects representing
            sub-tables.
    """

    table_id: str
    table_type: TableType
    file_prefix: str = ""
    url_path: str = ""
    table_key_name: str = ""
    column_number: int = 0
    secondary_column_number: int = None
    table_tab_xpath: str = ""
    subtables: Optional[Dict[str, "TableInfoDataClass"]] = None

    # File Download info
    files_table_url_form: str = ""
    table_url_form_id_name: str = "ID"


table_info: Dict[str, TableInfoDataClass] = {}

table_info["open_purchase_orders"] = TableInfoDataClass(
    url_path="/listPos.aspx?tab=4",
    file_prefix="OPO",
    table_type=TableType.SUBLINKS,
    table_id="#ListOpenPurchaseOrdersTable",
    table_key_name="purchase_order",
    column_number=1,
    subtables={
        "po_details": TableInfoDataClass(
            table_id="#ListPOTable", table_type=TableType.DATA
        ),
        "po_crm": TableInfoDataClass(
            table_id="#ListCRMTable", table_type=TableType.DATA
        ),
        "po_files": TableInfoDataClass(
            table_id="#tblFiles", table_type=TableType.FILES
        ),
    },
    files_table_url_form="fileupload/cUpload.aspx?TransactionID={id}&Source=PO",
)


table_info["supplier_invoices"] = TableInfoDataClass(
    url_path="/listPurchases.aspx?ListStartDate=1/1/2022&ListEndDate=12/1/2024",
    file_prefix="SIPL",
    table_type=TableType.SUBLINKS,
    table_id="#ListSupplierInvoicesTable",
    table_key_name="sipl",
    column_number=0,
    secondary_column_number=1,
    subtables={
        "sipl_items": TableInfoDataClass(
            table_id="#ListInventoryTable",
            table_type=TableType.DATA,
            table_tab_xpath="//*[@id='tabs']/li[1]/a",
        ),
        "sipl_freight_bills": TableInfoDataClass(
            table_id="#ListFreightTable",
            table_type=TableType.DATA,
            table_tab_xpath="//*[@id='tabs']/li[2]/a",
        ),
    },
    files_table_url_form=(
        "fileupload/cUpload.aspx?TransactionID={id}&Source=SIPL_Files&POID={id_2}"
    ),
)

table_info["items"] = TableInfoDataClass(
    url_path="/listItems.aspx",
    file_prefix="ITEMS",
    table_type=TableType.SUBLINKS,
    table_id="#listItemsTable",
    table_key_name="item",
    column_number=0,
    subtables={},
)


table_info["customers"] = TableInfoDataClass(
    # listReportTable ??
    url_path="/listCustomers.aspx",
    file_prefix="CUSTOMERS",
    table_type=TableType.SUBLINKS,
    table_id="listReportTable",
    table_key_name="cust_id",
    column_number=0,
    subtables={
        "files": TableInfoDataClass(
            table_id="#ListInventoryTable",
            table_type=TableType.DATA,
            table_tab_xpath="//*[@id='tabs']/li[14]/a",
        ),
        "crm": TableInfoDataClass(
            table_id="#ListFreightTable",
            table_type=TableType.DATA,
            table_tab_xpath="//*[@id='tabs']/li[2]/a",
        ),
    },
    files_table_url_form="fileupload/cUpload.aspx?PartyID={id}&Source=Customers",
)


table_info["salesorders"] = TableInfoDataClass(
    # listReportTable ??
    url_path="/listSaleOrders.aspx?ListStartDate=1/1/2022&ListEndDate=10/31/2024",
    file_prefix="CUSTOMERS",
    table_type=TableType.SUBLINKS,
    table_id="listSaleOrdersTable",
    table_key_name="so",
    column_number=0,
    subtables={},
    files_table_url_form=(
        "fileupload/cUpload.aspx?TransactionID={id}&"
        "Source=SaleOrder&PresaleID=0&SageOrHausProAPI="
    ),
)


table_info["quotes"] = TableInfoDataClass(
    # listReportTable ??
    # https://ibs.stoneprofits.com/vQuote.aspx?ID=112023#tab=4 has 1 file
    # Quote# 13237-1 Oppo…# 13237
    url_path=(
        "/listOpportunities.aspx?tab=4&ListStartDate=1/1/2022&ListEndDate=10/31/2024"
    ),
    file_prefix="QUOTES",
    table_type=TableType.SUBLINKS,
    table_id="ListQuoteTable",
    table_key_name="qo",
    column_number=0,
    subtables={},
    # file download
    files_table_url_form=(
        "fileupload/cUpload.aspx?TransactionID={id}&"
        "Source=Presale&SubSource=Quote&OpportunityID={id_2}"
    ),
)


table_info["quote_details_opportunites"] = TableInfoDataClass(
    # This has opportunity & quote, so we can map the 2 together.
    url_path="/R_D_QuoteItemDetails.aspx?navi=&q1=1%2F1%2F2022&q2=&q=Customer",
    file_prefix="OPPS",
    table_type=TableType.SUBLINKS,
    table_id="listQuoteDetailsTable",
    table_key_name="qo",
    column_number=3,  # This is the Opp# - need to get the internal ID.
    subtables={},
)


table_info["opportunities"] = TableInfoDataClass(
    url_path=(
        "/listOpportunities.aspx?tab=0&list=ListOpportunities&"
        "ListStartDate=1/1/2022&ListEndDate=10/31/2024"
    ),
    file_prefix="OPPOR",
    table_type=TableType.SUBLINKS,
    table_id="ListOpportunitiesTable",
    table_key_name="opp",
    column_number=0,  # This is the Opp# - need to get the internal ID.
    subtables={},
    files_table_url_form=(
        "fileupload/cUpload.aspx?TransactionID={id}&"
        "Source=Presale&SubSource=Opportunity"
    ),
)


table_info["products"] = TableInfoDataClass(
    url_path="/listItems.aspx",
    table_type=TableType.SUBLINKS,
    table_id="listItemsTable",
    table_key_name="item",
    column_number=1,
)

table_info["vendors"] = TableInfoDataClass(
    # Vendors:
    # https://ibs.stoneprofits.com/listVendors.aspx
    # https://ibs.stoneprofits.com/vVendor.aspx?ID=314#tab=6
    url_path="/listVendors.aspx",
    table_type=TableType.SUBLINKS,
    table_id="listReportTable",
    table_key_name="vendor",
    files_table_url_form=(
        "fileupload/cUpload.aspx?FileType=image&PartyID={id}&Source=Vendors"
    ),
)


table_info["bills"] = TableInfoDataClass(
    # Bills:
    # https://ibs.stoneprofits.com/ListBills.aspx
    # https://ibs.stoneprofits.com/vBill.aspx?ID=110687
    url_path="/ListBills.aspx",  # Need date limited range....
    table_type=TableType.SUBLINKS,
    table_id="listReportTable",
    table_key_name="bills",
    files_table_url_form=("fileupload/cUpload.aspx?TransactionID=110687&Source=Bill"),
    column_number=1,
)
