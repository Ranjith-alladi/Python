import pdfplumber
import pandas as pd



def table_extraction(header, file_path):
    pdf = pdfplumber.open(file_path)

    def Data_processing(table_values, column_values):
        required_values = []
        extra_values = [] 
        n = 0
        for _ in range(n, len(table_values)):
            if n < len(table_values):
                val_top = table_values[n]['top']
                val_bottom = table_values[n]['bottom']
                temp = [x for x in table_values if x['top'] < val_bottom and x['bottom'] > val_top]
                l = len(column_values)
                if len(temp) > l // 2:
                    for i in column_values:
                        if column_values[-1]['text'] == i['text'] and n == len(table_values):
                            required_values.append('')
                        for _ in range(n, len(table_values)):
                            if table_values[n]['x0'] < i['x1'] and table_values[n]['top'] < val_bottom and table_values[n]['bottom'] > val_top:
                                required_values.append(table_values[n]['text'])
                                n += 1
                                break
                            else:
                                required_values.append('')
                                break
                else:
                    extra_values.extend(temp)
                    n += 1
            else:
                break
        return required_values, extra_values

    def find_header(header_name, pdf):
        a = []
        for page in pdf.pages:
            page_words = page.extract_words(keep_blank_chars=True, x_tolerance=2)
            for x in page_words:
                if header_name.lower() == x["text"].lower():
                    a.append(page)
        return a

    print(f"Looking for header: {header}")
    page_count = find_header(header, pdf)

    if not page_count:
        print(f"Header '{header}' not found in the PDF.")
        return None  

    if len(page_count) > 1:
        page_data = []
        for i in page_count:
            lines = i.lines
            words = i.extract_words(keep_blank_chars=True, x_tolerance=1)
            heading_value = [x for x in words if header.lower() in x['text'].lower()]
            # print(heading_value)
            table_words = [x for x in words if x['top'] > heading_value[0]['bottom']]
            column_values = [x for x in table_words if x['top'] - heading_value[0]['bottom'] < 10]
            table_lines = [x for x in lines if x['top'] > heading_value[0]['bottom']]

            if len(table_lines) == 1:
                table_values = [x for x in table_words if x['top'] > column_values[0]['bottom']]
                result = Data_processing(table_values, column_values)
                required_values = result[0]
                extra_values = result[1]
                page_dict = {}
                for n, i in enumerate(column_values):
                    page_dict[i['text']] = []
                    v = n
                    value = []
                    for _ in required_values:
                        if v < len(required_values):
                            value.append(required_values[v])
                            v += len(column_values)
                    page_dict[i['text']] = value
                page_df1 = pd.DataFrame(page_dict)

                if len(extra_values) >= len(column_values):
                    extra_names = [x['text'].split(':')[0] for x in extra_values]
                    extra_heads = list(set(extra_names))
                    dict1 = {}
                    for i in extra_heads:
                        dict1[i] = []
                        values = [x['text'].split(":")[-1] for x in extra_values if x['text'].split(":")[0] in i]
                        dict1[i] = values
                    page_df2 = pd.DataFrame(dict1)
                    page_df = pd.concat([page_df1, page_df2], axis=1)
                else:
                    page_df = page_df1
            else:
                end_line = table_lines[1]
                table_values = [x for x in table_words if x['top'] > column_values[0]['bottom'] and x['top'] < end_line['bottom']]
                result = Data_processing(table_values, column_values)
                required_values = result[0]
                extra_values = result[1]
                page_dict = {}
                for n, i in enumerate(column_values):
                    page_dict[i['text']] = []
                    v = n
                    value = []
                    for _ in required_values:
                        if v < len(required_values):
                            value.append(required_values[v])
                            v += len(column_values)
                    page_dict[i['text']] = value
                page_df = pd.DataFrame(page_dict)
                page_data.append(page_df)

                if len(extra_values) >= len(column_values):
                    extra_names = [x['text'].split(':')[0] for x in extra_values]
                    extra_heads = list(set(extra_names))
                    dict1 = {}
                    for i in extra_heads:
                        dict1[i] = []
                        values = [x['text'].split(":")[-1] for x in extra_values if x['text'].split(":")[0] in i]
                        dict1[i] = values
                    page_df2 = pd.DataFrame(dict1)
                    page_df = pd.concat([page_df1, page_df2], axis=1)
                else:
                    page_df = page_df1
                page_data.insert(0, page_df)

        final_df = pd.concat(page_data, axis=0)
        return final_df

    else:
        page_data = page_count[0]
        lines = page_data.lines
        words = page_data.extract_words(keep_blank_chars=True, x_tolerance=1)
        heading_value = [x for x in words if header.lower() in x['text'].lower()]
        table_words = [x for x in words if x['top'] > heading_value[0]['bottom']]
        column_values = [x for x in table_words if x['top'] - heading_value[0]['bottom'] < 10]
        table_lines = [x for x in lines if x['top'] > heading_value[0]['bottom']]
        end_line = table_lines[1]
        table_values = [x for x in table_words if x['top'] > column_values[0]['bottom'] and x['top'] < end_line['bottom']]
        result = Data_processing(table_values, column_values)
        required_values = result[0]
        extra_values = result[1]

        page_dict = {}
        for n, i in enumerate(column_values):
            page_dict[i['text']] = []
            v = n
            value = []
            for _ in required_values:         
                if v < len(required_values):
                    value.append(required_values[v])
                    v += len(column_values)
            page_dict[i['text']] = value
        page_df1 = pd.DataFrame(page_dict)

        if len(extra_values) >= len(column_values):
            extra_names = [x['text'].split(':')[0] for x in extra_values]
            extra_heads = list(set(extra_names))
            dict1 = {}
            for i in extra_heads:
                dict1[i] = []
                values = [x['text'].split(":")[-1] for x in extra_values if x['text'].split(":")[0] in i]
                dict1[i] = values
            page_df2 = pd.DataFrame(dict1)
            page_df = pd.concat([page_df1, page_df2], axis=1)
        else:
            page_df = page_df1
        return page_df