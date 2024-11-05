from fasthtml.common import (
    # FastHTML's HTML tags
    A, AX, Button, Card, CheckboxX, Container, Div, Form, Grid, Group,P, H1, H2, H3, H4, H5, Hr, Hidden, Input, Li, Ul, Main, Script, Style, Textarea, Title, Titled, Select, Option, Table, Tr, Th, Td,
    # FastHTML's specific symbols
    Beforeware, FastHTML, fast_app, SortableJS, fill_form, picolink, serve, NotStr,
    # From Starlette, Fastlite, fastcore, and the Python standard library:
    FileResponse, NotFoundError, RedirectResponse, database, patch, dataclass, UploadFile
)
import os
import datetime
import json
import base64
import requests

TYPLESS_API_KEY = os.getenv('TYPLESS_API_KEY')
if not TYPLESS_API_KEY:
    raise ValueError("Please set the TYPLESS_API_KEY environment variable")


db = database('data/docs.db')

docs = db.t.docs
if docs not in db.t:
    docs.create(id=int, filename=str, document_type=str, content_b64=str, result=str, pk='id')

# Create a dataclass for the docs table entries
Doc = docs.dataclass()

# This will be our 404 handler, which will return a simple error page.
def _not_found(req, exc): return Titled('Oh no!', Div('We could not find that page :('))

# FastHTML includes the "HTMX" and "Surreal" libraries in headers, unless you pass `default_hdrs=False`.
app = FastHTML(exception_handlers={404: _not_found},
               # PicoCSS is a tiny CSS framework that we'll use for this project.
               # `picolink` is pre-defined with the header for the PicoCSS stylesheet.
               hdrs=(picolink,
                     # `Style` is an `FT` object, which are 3-element lists consisting of:
                     # (tag_name, children_list, attrs_dict).
                     Style(':root { --pico-font-size: 100%; }'),
                )
      )
# `app.route` (or `rt`) requires only the path, using the decorated function's name as the HTTP verb.
rt = app.route

@rt("/") # Index page
def get():
    frm = Form(
        H3('Upload a file to be processed by Typless:'),
        Group(
            Input(type="file", name="file", accept=".png, .jpg, .jpeg, .JPG, .pdf", required=True),
            ),
        Group(
            P('Select the type of document:'),
            Select(
                Option('Simple Invoice', value='simple-invoice'),
                Option('Garage Invoice', value='garage-invoice'),
                Option('Report', value='report'),
                name='doc_type',
                required=True,
                style='max-width: 200px;'
            ),
            style='display: flex; justify-content: space-between; align-items: center;',
        ),
        Button('Process'),
        P('Processing...', id="processing", cls="htmx-indicator"),
        hx_post='/process', hx_swap='afterend', hx_indicator="#processing",
        style='max-width: 500px;'
    )

    return Titled("Typless example", frm)

@rt("/process")
def post(file: UploadFile, doc_type: str):

    # UploadFile(filename='ATL_2024-09-24_report.pdf', size=600810, headers=Headers({'content-disposition': 'form-data; name="file"; filename="ATL_2024-09-24_report.pdf"', 'content-type': 'application/pdf'}))
    # Read the file content
    file_content = file.file.read()

    # Encode the content as Base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')

    
    # API call to Typless

    url = "https://developers.typless.com/api/extract-data"

    payload = {
        "document_type_name": doc_type,
        "file_name": file.filename,
        "file": encoded_content,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {TYPLESS_API_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
    else:
        return Card(H2('Failed to process the file'),
                    P('An error occurred while processing the file. Please try again later.'),
                    P('Error message from Typless:'),
                    Div(response.text),
                    header='Error ❌')

    
    # Extract fields from the result
    extracted_fields = result.get('extracted_fields', {})
    field_elements = [
        Group(
            Table(
                Tr(
                    Th(H5(field_dict['name'])),
                    Th('Confidence Score')
                ),
                *[
                    Tr(
                        Td(value['value']),
                        Td(f"{value['confidence_score']*100:.2f}%")
                    )
                    for value in field_dict['values']
                ],
                style='width: 100%; border-collapse: collapse;'
            ),
            style='margin-bottom: 20px;'
        )
        for field_dict in extracted_fields
    ]



    '''
    "line_items": [
        [
            {
                "values": [
                    {
                        "x": 324,
                        "y": 761,
                        "width": 304,
                        "height": 26,
                        "page_number": 0,
                        "value": "IZP.LONEC-ZADNJI",
                        "confidence_score": 0.5
                    }
                ],
                "name": "product_description",
                "data_type": "STRING"
            },
    '''
    # Extract line items from the result
    line_items = result.get('line_items', [])

    # Create a table for line items
    line_item_table = Table(
        Tr(
            Th('Product Number'),
            Th('Product Description'),
            Th('Quantity'),
            Th('Price')
        ),
        *[
            Tr(
                Td(next((value['values'][0]['value'] for value in item if value['name'] == 'product_number'), '')),
                Td(next((value['values'][0]['value'] for value in item if value['name'] == 'product_description'), '')),
                Td(round(float(next((value['values'][0]['value'] for value in item if value['name'] == 'quantity'), '')),2)),
                Td(round(float(next((value['values'][0]['value'] for value in item if value['name'] == 'price'), '')),2))
            )
            for item in line_items
        ],
    )



    doc_dict = {
        "filename":file.filename,
        "document_type":doc_type,
        "content_b64":encoded_content,
        "result":json.dumps(result)
        }

    return Form(Card(H2(f'{file.filename}'),
                P(f'Content type: {doc_type}'),
                H3('Extracted fields:'),
                Div(*field_elements),
                H3('Line items:'),
                line_item_table,
                Button('Save', id='save_button'),
                Hidden(json.dumps(doc_dict), name='doc'),
         header='Document uploaded successfully ✅',
         footer=f'Uploaded at: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'),
         
            hx_post='/save', hx_target='#save_button', hx_swap='outerHTML', hx_indicator=True)

@rt("/save")
def post(doc: str):
    doc = Doc(**json.loads(doc))
    # Insert the document into the database
    docs.insert(doc)
    return Button('Saved', disabled=True)


serve() # Start the server