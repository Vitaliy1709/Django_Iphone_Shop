import os
import sys

from .models import Product
import xlrd

os.environ["DJANGO_SETTINGS_MODULE"] = "iphone_shop.settings"

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class UploadingProducts(object):
    foreign_key_field = ["category"]
    model = Product

    def __init__(self, data):
        data = data
        self.uploaded_file = data.get("file")
        self.parsing()

    def getting_related_model(self, field_name):
        model = self.model
        related_model = model._meta.get_field(field_name).remote_field.model
        return related_model

    def getting_headers(self):
        s = self.s
        headers = dict()
        for column in range(s.ncols):
            value = s.cell(0, column).value
            headers[column] = value
        return headers

    def parsing(self):
        uploaded_file = self.uploaded_file
        wb = xlrd.open_workbook(file_contents=uploaded_file.read())
        s = wb.sheet_by_index(0)
        self.s = s

        headers = self.getting_headers()
        print(headers)

        product_bulk_list = list()

        for row in range(1, s.nrows):
            row_dict = dict()
            for column in range(s.ncols):
                value = s.cell(row, column).value
                field_name = headers[column]
                print(field_name)

                # preventing adding id field with empty value even if it is exist in the uploaded_file
                if field_name == "id" or not value:
                    continue

                if field_name in self.foreign_key_field:
                    related_model = self.getting_related_model(field_name)

                    instance, created = related_model.objects.get_or_create(name=value)
                    value = instance

                row_dict[field_name] = value

            print(row_dict)

            product_bulk_list.append(Product(**row_dict))
            # Product.objects.create(**row_dict)

        # bulk creating
        Product.objects.bulk_create(product_bulk_list)
        return True
